# This is where our "main" function is

import cv2 as cv
import numpy as np
import findStaves
import removeStaffLines
import utilities_cv

def main():
    # Use this to use a piece of sample music
    test_img = cv.imread("example_music_3.jpg", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 200, 255, cv.THRESH_BINARY)

    # create window to look at test image and click on pixels for verification purposes
    picked_point = []
    pick_window = "Test Image"
    cv.namedWindow(pick_window, cv.WINDOW_NORMAL)
    cv.setMouseCallback(pick_window, utilities_cv.get_xy, picked_point)
    cv.imshow(pick_window, test_img)

    staves = findStaves.findStaves(test_img)
    print(" Found Staves")
    image_no_staff = removeStaffLines.removeLines(test_img, staves)
    print("Removed staves")

    # look at image with no staff lines
    cv.imshow("Staves Removes", image_no_staff)


    cv.waitKey(0)

if __name__ == '__main__':
    main()

