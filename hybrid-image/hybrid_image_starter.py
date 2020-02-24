import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

'''
	all operations below(except fft()) is for int16, because there maybe negative value
'''

def pyramid(image, level):
    down = image.copy()
    for i in range(level):
        down = cv.pyrDown(down)
    return down

def overlap(im1, im2):
    return im1 + im2

def visualize_high_frequency(im):
    return im + 127

def low_pass(im, width, sigma):
    return cv.GaussianBlur(im,(width,width),sigma)

def high_pass(im, width, sigma):
    return  im - low_pass(im, width, sigma)

def hybrid_image(im1, im2, width, sigma):
    low = low_pass(im1, width, sigma)   
    high = high_pass(im2, width, sigma)
    # cv.imshow('low.jpg', low)
    # cv.imshow('high.jpg', visualize_high_frequency(high))
    return overlap(low, high)
	

#return a spectrogram of 'image'
#Note that spectrogram is in grey level(which means it is a 2D array)
def fft(image):
    float_img = np.array(image).astype(np.float32)
	
	#This will make a 2D array from a 3D array
    grey_img = cv.cvtColor(float_img,cv.COLOR_BGR2GRAY)
	
    frequency = np.fft.fft2(grey_img)
    frequency_shift = np.fft.fftshift(frequency)
	
    res = np.log(np.abs(frequency_shift))
    
    return res
	

# root_path = './group3/'
# im1_name = root_path + 'marilyn.bmp'
# im2_name = root_path + 'einstein.bmp'
# root_path = './group2/'
# im1_name = root_path + 'dog.jpg'
# im2_name = root_path + 'cat.jpg'
root_path = './group4/'
im1_name = root_path + 'motorcycle.bmp' 
im2_name = root_path + 'bicycle.bmp'


# high sf
im1 = cv.imread(im1_name)
plt.imshow(fft(im1),'gray')
plt.title('spectrogram of' + im1_name)
plt.show()
im1 = np.int16(im1)

# low sf
im2 = cv.imread(im2_name)
plt.imshow(fft(im2),'gray')
plt.title('spectrogram of' + im2_name)
plt.show()
im2 = np.int16(im2)

#cat & dog 43, 7
#einstein & marilyn 19 3
#motorcycle & bicycle 43, 7
hybrid = hybrid_image(im1, im2, 43, 7)
plt.imshow(fft(im2),'gray')
plt.title('spectrogram of hybrid')
plt.show()

cv.imwrite(root_path + 'hybrid.jpg', hybrid)
cv.imwrite(root_path + 'pyramid.jpg', pyramid(hybrid, 3))

cv.waitKey(0)

