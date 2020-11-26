# This function labels the notes of the original sheet of music

import cv2 as cv
import numpy as np
import utilities_cv

def labelNotes(image, staves):
    # INPUT
    #   image   =   the original image of music. Don't need to binarize
    #   staves  =   list of staff objects.
    # OUTPUT
    #   img_ann =   annotated image. Each note has its pitch labeled

    # Parameters
    #   adjust the following parameters to get desirable labeling
    font_scale = 1
    font = cv.FONT_HERSHEY_SIMPLEX

    # go to each staff
    for staff in staves:
        # go to to each note
        for note in staff.notes:
