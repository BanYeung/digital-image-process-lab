import numpy as np
import cv2 as cv
from ctypes import cdll
import ctypes
import time

def cvt_to_c_char_pointer(array):
	return array.ctypes.data_as(ctypes.POINTER(ctypes.c_char))

'''
accept a channel(i.e. a 2D array)
filter it with a gaussian kernel
and reject the even rows and cols

Just Like cv2.pyrDown()
'''
def downsample_by_c(channel):
	src_rows = channel.shape[0]
	src_cols = channel.shape[1]
	dst_rows = src_rows // 2
	dst_cols = src_cols // 2
	
	down = np.zeros([ dst_rows, dst_cols],dtype=np.uint8)
	
	dll = ctypes.cdll.LoadLibrary("./downsample.so")
	dll.downsample(cvt_to_c_char_pointer(channel), cvt_to_c_char_pointer(down), src_cols, dst_rows, dst_cols)
	return down

#'rect_info' characterize the rectangle
#return a rectangle coded in np.int from 'image'
def drawout_rect(image, rect_info):
    image_height = image.shape[0]
    image_width= image.shape[1]
    x_leftTop = rect_info['leftTop'][0]
    y_leftTop = rect_info['leftTop'][1]
    rect_height = rect_info['height']
    rect_width = rect_info['width']
    
    assert(x_leftTop + rect_height <= image_height)
    assert(y_leftTop + rect_width <= image_width)

    return np.array(image[x_leftTop: x_leftTop + rect_height,
                          y_leftTop: y_leftTop + rect_width]).astype(np.int)

#the smallest sum of square of difference
def find_similar_rect(ref_image, ref_rect_info, image):
    assert(ref_image.shape == image.shape)
    shape = ref_image.shape 
    
    #ref_rect is abbreviation of refernce rectangle
    height = ref_rect_info['height']
    width = ref_rect_info['width']

    ref_rect = drawout_rect(ref_image, ref_rect_info)
    move_rect = drawout_rect(image, ref_rect_info)
    mini = np.sum( (ref_rect - move_rect) **2 )
    
    similar_rect_x_leftTop = 0
    similar_rect_y_leftTop = 0

    move_rect_info = {'leftTop':[0, 0], 'height' :height, 'width' : width}
    for x in range(0, shape[0] - height + 1): #range(included, excluded)
        for y in range(0, shape[1] - width +1):
            move_rect_info['leftTop'] = [x, y]
            move_rect = drawout_rect(image, move_rect_info)
            diff = move_rect - ref_rect
            sum_of_squares = np.sum( diff**2)
            if (sum_of_squares < mini):
                mini = sum_of_squares
                similar_rect_x_leftTop = x
                similar_rect_y_leftTop = y
    return similar_rect_x_leftTop,  similar_rect_y_leftTop

'''
assist function ************************************
'''
def dis_from_similar_to_ref(similar_point, ref_point):
    return ref_point[0] - similar_point[0], ref_point[1] - similar_point[1]

def roll(im, x_dis, y_dis, scale_factor):
    im = np.roll(im, x_dis * scale_factor , axis=0)
    im = np.roll(im, y_dis * scale_factor, axis=1)
    return im

def compute_ref_rect(shape, frame_height, frame_width):
    x_leftTop = frame_height
    y_leftTop = frame_width
    ref_rect_info = {'leftTop':[x_leftTop, y_leftTop],'height' : shape[0] - x_leftTop - frame_height, 'width' : shape[1] - y_leftTop - frame_width}
    return ref_rect_info
'''
assist function ************************************
'''

def  down_sample(im1, im2, im3, times):
    scale_factor = 1
    for i in range (0, times):
        scale_factor = scale_factor * 2;
        im1 = downsample_by_c(im1)
        im2 = downsample_by_c(im2)
        im3 = downsample_by_c(im3)
    return im1, im2, im3, scale_factor

#At first, we draw out a reference rectangle from b channel
#( Cutting off the frame of b will give us the reference rectangle. )
#And then we try to find a similar rectangle in g channel, roll g to make sure
#two rectangles(i.e. the similar one in g and the reference one in b) has the same position.
#Do the same thing to r.
#It is critical for a good result to select an appropriate reference rectangle
#( In other words, to find out the height and width of the 'frame' )
def align_three_channels(image_name, frame_height, frame_width, down_sample_times):
	im = cv.imread(image_name)
	im = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

	height = np.floor(im.shape[0] / 3.0).astype(np.int)
	b = im[:height]
	g = im[height: 2 * height]
	r = im[2 * height: 3 * height]
	
	b_saved, g_saved, r_saved = b.copy(), g.copy(), r.copy()
	
	#downsample
	start = time.time()
	b, g, r, scale_factor = down_sample(b, g, r, down_sample_times)
	print('downsample seconds:', time.time() - start)
	
	#get the infomation of reference rectangle
	start = time.time()
	ref_rect_info = compute_ref_rect(b.shape, frame_height, frame_width)
	print('compute_ref_rect seconds:', time.time() - start)
	
	#align
	start = time.time()
	x_dis, y_dis =dis_from_similar_to_ref(find_similar_rect(b, ref_rect_info, g),ref_rect_info['leftTop'])
	g_saved = roll(g_saved,x_dis, y_dis, scale_factor)
	x_dis, y_dis =dis_from_similar_to_ref(find_similar_rect(b, ref_rect_info, r),ref_rect_info['leftTop'])
	r_saved = roll(r_saved, x_dis, y_dis, scale_factor)
	print('align by rolling seconds:', time.time() - start)

	res = cv.merge( (b_saved, g_saved, r_saved) )
	cv.imwrite(image_name[:-4] + "_processed_ccc.jpg", res)

#image_name = "./pic/settlers.jpg" 30, 30
image_name = "./pic/cathedral.jpg"
#image_name = "./pic/village.tif" 150 150 3

start = time.time()
align_three_channels(image_name, 10, 10, 3)
print('total seconds:', time.time() - start)


