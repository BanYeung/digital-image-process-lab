import cv2 as cv
import numpy as np

#return a bottom-up gaussian pyramid of 'image' with the height of 'level'
def gaussian_pyramid(image, level):
    G = image.copy()
    pyramid = [G]
    for i in range(level - 1):
        G = cv.pyrDown(G)
        pyramid.append(G)
    return pyramid
 
#return an informal top-down laplacian pyramid of 'image' with the height of 'level'
#Note that, if the height of gaussian pyramid is n, 
#then the height of corresponding laplacian pyramid is n - 1,
#Here, we add the highest level of gaussian pyramid to in the top of laplacian pyramid
#so that it is has the same height as gaussian pyramid
#	This is critical to create a blending image in mult-color level
def laplacian_pyramid(image, level):
	gaus_pyr = gaussian_pyramid(image, level)
	lpls_pyr = [gaus_pyr[level - 1]]
	level = len(gaus_pyr)
	
	for i in range(level - 1,0,-1):
		expand = cv.pyrUp(gaus_pyr[i])
		expand = cv.resize(expand,gaus_pyr[i - 1].shape[-2::-1])
		L = cv.subtract(gaus_pyr[i-1], expand)
		lpls_pyr.append(L)
	return lpls_pyr



def reconstuct_from_lpls_pyramid(LS):
	ls_ = LS[0]
	for i in range(1,len(LS)):
		ls_ = cv.pyrUp(ls_)
		ls_= cv.resize(ls_, LS[i].shape[-2::-1])
		ls_ = cv.add(ls_, LS[i])
	return ls_

	
def getCenterCol(im):
	cols = len(im[0])	
	center = cols // 2 - 1 if cols % 2 == 0 else cols // 2
	return center
	
def set_left_half_zero(im):

	center = getCenterCol(im) 	
	for row in im:
		for i in range(0, center):
			row[i] = 0
			
def set_right_half_zero(im):
	
	center = getCenterCol(im) 
	cols = len(im[0])
	for row in im:
		for i in range(center + 1, cols):
			row[i] = 0

def average_center(im):
	
	center = getCenterCol(im) 	
	for row in im:
		row[center] = row[center] // 2


	
def combine_lpls_pyramid(left_pyramid, right_pyramid):
	assert(len(left_pyramid) == len(right_pyramid))
	length = len(left_pyramid)
	combine_pyramid = []
	for level in range(0, length):
		assert(left_pyramid[level].shape == right_pyramid[level].shape)
		
		left = left_pyramid[level].copy()
		right = right_pyramid[level].copy()
		
		#if num of column is even, ignore the last column
		#That is saying, consider the cols // 2 - 1 as the center column
		#center column stay still
		set_left_half_zero(right)
		set_right_half_zero(left)
		
		combine = cv.add(left, right)
		average_center(combine)
		
		combine_pyramid.append(combine)
		
	return combine_pyramid
		
    

            
im1 = cv.imread("pic/apple.jpeg")
im2 = cv.imread("pic/orange.jpeg")
cv.imshow("input image1", im1)
cv.imshow("input image2", im2)

im1_lpls_pyramid = laplacian_pyramid(im1, 6)
im2_lpls_pyramid = laplacian_pyramid(im2, 6)

combine_lpls_pyramid = combine_lpls_pyramid(im1_lpls_pyramid, im2_lpls_pyramid)
res = reconstuct_from_lpls_pyramid(combine_lpls_pyramid)

cv.imshow("Result", res)
cv.imwrite("pic/my_orapple.jpg", res )

cv.waitKey(0)
