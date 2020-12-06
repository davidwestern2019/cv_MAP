# This is where our "main" function is

import cv2 as cv
import numpy as np
import findStaves
import noteDetect
import removeStaffLines
import utilities_cv
import noteDetect


def main():
    # Use this to use a piece of sample music
    test_img = cv.imread("example_music_7.jpg", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 180, 255, cv.THRESH_BINARY)
    # imma try some shit here
    cv.imshow("test_img", test_img)

    # create window to look at test image and click on pixels for verification purposes
    # picked_point = []
    # pick_window = "Test Image"
    # cv.namedWindow(pick_window, cv.WINDOW_NORMAL)
    # cv.setMouseCallback(pick_window, utilities_cv.get_xy, picked_point)
    # cv.imshow(pick_window, test_img)

    # find staves
    staves = findStaves.findStaves(test_img)
    print("Found Staves...")

    # remove staves
    image_no_staff = removeStaffLines.removeLines(test_img, staves)
    print("Removed staves")

    # look at image with no staff lines
    # cv.imshow("Staves Removes", image_no_staff)
    # cv.waitKey(0)



    for staff in staves:
        cropped_image = noteDetect.staffCrop(staff, image_no_staff)
        staff, image_note_detect = noteDetect.noteDetect(staff, cropped_image)
        # find accidentals

    # for running noteDetect on full image (testing and troubleshooting)
    # will run multiple times for no good reason (so we don't have to change stuff in noteDetect to use this)
    #for staff in staves:
        #image_note_detect = noteDetect.noteDetect(staves, staff, image_no_staff)
    print("Detected Notes")




if __name__ == '__main__':
    main()
