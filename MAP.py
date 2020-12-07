# This is where our "main" function is

import cv2 as cv
import numpy as np
import findStaves
import noteDetect
import removeStaffLines
import utilities_cv
import noteDetect
import labelNotes
import playMIDI
import createMIDI


def main():
    # Use this to use a piece of sample music
    file_name = "rockin_around.PNG"
    orig_img = cv.imread(file_name, cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(orig_img, 180, 255, cv.THRESH_BINARY)
    # imma try some shit here
    # cv.imshow("test_img", test_img)
    # 0.35
    scale = 0.5
    img_w = round(orig_img.shape[1] * scale)
    img_h = round(orig_img.shape[0] * scale)
    dim = (img_w, img_h)
    orig_img = cv.resize(orig_img, dim, interpolation=cv.INTER_AREA)
    _, test_img = cv.threshold(orig_img, 180, 255, cv.THRESH_BINARY)
    cv.imshow("test_img", test_img)
    cv.waitKey(0)
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



    for i in range(len(staves)):
        cropped_image = noteDetect.staffCrop(staves[i], image_no_staff)
        staves[i], image_note_detect, height, width = noteDetect.noteDetect(staves[i], cropped_image)

        # find accidentals


    # for running noteDetect on full image (testing and troubleshooting)
    # will run multiple times for no good reason (so we don't have to change stuff in noteDetect to use this)
    #for staff in staves:
        #image_note_detect = noteDetect.noteDetect(staves, staff, image_no_staff)
    print("Detected Notes")

    # # create the music file
    music_file = file_name[:-3]
    # createMIDI.createMIDI(staves_2, music_file)
    #
    # # play the music file
    # music_file += "mid"
    # playMIDI.play_music(music_file)

    # label the images
    print("Labeling original image...")
    label_image = labelNotes.labelNotes(orig_img, staves)
    cv.imshow("Labeled Image", label_image)
    cv.waitKey(0)
    print("Labeled image")


if __name__ == '__main__':
    main()
