# This is where our "main" function is

import cv2 as cv
import findStaves
import removeStaffLines
import noteDetect
import labelNotes
import playMIDI
import createMIDI
import detectBeams
import time

# Use this to get runtime
start_time = time.time()


def main():
    # Use this to use a piece of sample music
    file_name = "deck_the_halls_sax.png"
    orig_img = cv.imread(file_name, cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(orig_img, 180, 255, cv.THRESH_BINARY)

    # find staves
    staves = findStaves.findStaves(test_img)
    print("Found staves...")

    # remove staves
    image_no_staff = removeStaffLines.removeLines(test_img, staves)
    print("Removed staves...")

    keyFlats = []
    keySharps = []

    for i in range(len(staves)):
        cropped_image = noteDetect.staffCrop(staves[i], image_no_staff)
        staves[i], image_note_detect, height, width, keyFlats, keySharps = noteDetect.noteDetect(staves[i],
                                                                                                 cropped_image,
                                                                                                 keyFlats, keySharps)
        staves[i] = detectBeams.detectBeams(staves[i], cropped_image, height, width)

    print("Detected notes...")

    # create the music file
    music_file = file_name[:-4]
    createMIDI.createMIDI(staves, music_file)
    print("MIDI file created...")

    cv.destroyAllWindows()

    # label the images
    print("Annotating original image...")
    label_image = labelNotes.labelNotes(orig_img, staves)
    print("Annotated image...")
    annotated_img_name = file_name[:-4] + "_annotated.png"
    cv.imwrite(annotated_img_name, label_image)
    print("Annotated image saved...")
    cv.namedWindow("Annotated Image", cv.WINDOW_NORMAL)
    cv.imshow("Annotated Image", label_image)

    # print runtime
    print("Runtime: %s seconds" % (time.time() - start_time))

    cv.waitKey(0)

    # # play the music file
    print("Playing MIDI file...")
    music_file += ".mid"
    playMIDI.play_music(music_file)
    print("Playback completed")
    print("So long for now!")


if __name__ == '__main__':
    main()
