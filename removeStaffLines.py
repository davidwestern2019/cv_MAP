import cv2 as cv
import numpy as np
import utilities_cv

# This file holds functions for removing the stafflines

def removeLines(img, staves):
    # Purpose: Remove staff lines for each staff
    # Input:
    # -- a list of staff objects
    # -- binary image of music
    # Output:
    # -- an image without stafflines

    image = img.copy()
    width = image.shape[1]
    height = image.shape[0]

    for staff in staves:
        for line in staff.line_locations:
            # check above and below line to see if there are any black pixels (musical features)
            top = int(line[0])
            bottom = int(line[1])
            # print(top, bottom)
            for col in range(0, width):
                if image[top-1, col] != 0 and image[bottom+1, col] != 0:
                    image[top:bottom, col] = 255
    return image

def main():
    pass


if __name__ == '__main__':
    main()