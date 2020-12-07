# This function labels the notes of the original sheet of music

import cv2 as cv
import numpy as np
import utilities_cv
import createMIDI

def labelNotes(image, staves):
    # INPUT
    #   image   =   the original image of music. Don't need to binarize
    #   staves  =   list of staff objects.
    # OUTPUT
    #   image   =   annotated image. Each note has its pitch labeled

    # Parameters
    #   adjust the following parameters to get desirable labeling
    font_scale = 1
    font = cv.FONT_HERSHEY_SIMPLEX
    color_text = (0, 0, 0)

    # go to each staff
    for staff in staves:
        # go to to each note
        dis = staff.dis
        vert_coord = staff.staff_end + dis*2
        for note in staff.notes:
            if note.pitch is not None:
                col = note.x_val
                letter = utilities_cv.midiNum2Letter(note.pitch, accidental=note.accidental)
                print(letter)
                cv.putText(image, letter, (col, vert_coord), font, font_scale, color_text, thickness=2)

    return image

def main():
    # test the label notes function
    file = "test_music_1.png"
    image = cv.imread(file)
    staves = createMIDI.testStaves()
    label_image = labelNotes(image, staves)
    cv.imshow("Test Image", label_image)
    cv.waitKey(0)



if __name__ == '__main__':
    main()