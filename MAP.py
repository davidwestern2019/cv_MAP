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
import detectBeams


def main():
    # Use this to use a piece of sample music
    file_name = "o_canada.png"
    orig_img = cv.imread(file_name, cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(orig_img, 180, 255, cv.THRESH_BINARY)
    # imma try some shit here
    # cv.imshow("test_img", test_img)

    # 0.35
    # scale = 0.5
    # img_w = round(orig_img.shape[1] * scale)
    # img_h = round(orig_img.shape[0] * scale)
    # dim = (img_w, img_h)
    # orig_img = cv.resize(orig_img, dim, interpolation=cv.INTER_AREA)
    # _, test_img = cv.threshold(orig_img, 180, 255, cv.THRESH_BINARY)
    # cv.imshow("test_img", test_img)
    # cv.waitKey(0)

    # create window to look at test image and click on pixels for verification purposes
    # picked_point = []
    # pick_window = "Test Image"
    # cv.namedWindow(pick_window, cv.WINDOW_NORMAL)
    # cv.setMouseCallback(pick_window, utilities_cv.get_xy, picked_point)
    # cv.imshow(pick_window, test_img)
    # cv.waitKey(0)

    # find staves
    staves = findStaves.findStaves(test_img)
    print("Found Staves...")

    # remove staves
    image_no_staff = removeStaffLines.removeLines(test_img, staves)
    print("Removed staves")

    # look at image with no staff lines
    # cv.imshow("Staves Removes", image_no_staff)
    # cv.waitKey(0)

    keyFlats = []
    keySharps = []

    for i in range(len(staves)):
        cropped_image = noteDetect.staffCrop(staves[i], image_no_staff)
        staves[i], image_note_detect, height, width, keyFlats, keySharps = noteDetect.noteDetect(staves[i], cropped_image, keyFlats, keySharps)
        keySharpLetters = []
        keyFlatLetters = []
        for sharp in keySharps:
            keySharpLetters.append(utilities_cv.midiNum2Letter(sharp))
        for flat in keyFlats:
            keyFlatLetters.append(utilities_cv.midiNum2Letter(flat))
        print("key sharps: ", )
        staves[i] = detectBeams.detectBeams(staves[i], cropped_image, height, width)
        # for note in staves[i].notes:
        #     print("Displaying the note duration values")
        #     print("\t", note.duration)
        #     print("")
         # find accidentals


    # for running noteDetect on full image (testing and troubleshooting)
    # will run multiple times for no good reason (so we don't have to change stuff in noteDetect to use this)
    #for staff in staves:
        #image_note_detect = noteDetect.noteDetect(staves, staff, image_no_staff)
    print("Detected Notes")

    # # create the music file
    music_file = file_name[:-4]
    print("music_file: ", music_file)
    createMIDI.createMIDI(staves, music_file)
    #

    # label the images
    print("Annotating original image...")
    label_image = labelNotes.labelNotes(orig_img, staves)
    cv.imshow("Annotated Image", label_image)
    cv.waitKey(0)
    print("Annotated image")
    annotated_img_name = file_name[:-4] + "_annotated.png"
    cv.imwrite(annotated_img_name, label_image)
    print("Annotated image saved")

    # # play the music file
    print("Playing MIDI File")
    music_file += ".mid"
    playMIDI.play_music(music_file)
    print("Song completed")
    print("So long for now!")


if __name__ == '__main__':
    main()
