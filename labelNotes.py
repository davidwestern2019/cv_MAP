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
    font = cv.LINE_AA
    color_text = (0, 0, 0)

    # go to each staff
    for staff in staves:
        print("Staff number is: ", staff.staff_number)
        # go to to each note
        dis = staff.dis
        vert_coord = staff.staff_end + dis*3    # where the labels go
        font_scale = dis/10        # scale the font
        print("Staff ends at: ", vert_coord)
        print("There are ", len(staff.notes), " notes/rests in this staff.")
        for note in staff.notes:
            # print("Note pitch is: ", note.pitch)
            if note.pitch is not None:
                col = note.x_val
                letter = utilities_cv.midiNum2Letter(note.pitch, accidental=note.accidental)
                cv.putText(image, letter, (col, vert_coord), font, font_scale, color_text, thickness=1)
                image = image

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