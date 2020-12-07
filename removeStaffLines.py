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
            help_reduce_chop = 1
            # print(top, bottom)
            for col in range(0, width):                                                         
                # count = 0
                # topLeft = False
                # topRight = False
                # bottomLeft = False
                # bottomRight = False
                # # print("Line: ", top, " column ", col)
                # if col-help_reduce_chop>0:
                #     for j in range(1, help_reduce_chop):
                #         if image[top - 1, col - j] == 0:  # true if pixel is black
                #             count += 1
                #     if count == 0:
                #         topLeft = True
                #     if top == 462 and col == 42:
                #         print("\t \t tl count is: ", count, "")
                # else:
                #     topLeft = True
                #
                # count = 0
                # if col+help_reduce_chop<width:
                #     for j in range(1, help_reduce_chop):
                #         if image[top - 1, col+j] == 0:
                #             count += 1
                #     if count == 0:
                #         topRight = True
                #     if top == 462 and col == 42:
                #         print("\t \t tr count is: ", count)
                # else:
                #     topLeft = True
                #
                # count = 0
                # if col-help_reduce_chop>0:
                #     for j in range(1, help_reduce_chop):
                #         if image[bottom+1, col-j] == 0:
                #             count += 1
                #     if count == 0:
                #         bottomLeft = True
                #     if top == 462 and col == 42:
                #         print("\t \t bl count is: ", count)
                # else:
                #     topLeft = True
                #
                # count = 0
                # if col+help_reduce_chop<width:
                #     for j in range(1, help_reduce_chop):
                #         if image[bottom+1, col+j] == 0:
                #             count += 1
                #     if count == 0:
                #         bottomRight = True
                #     if top == 462 and col == 42:
                #         print("\t \t br count is: ", count)
                # else:
                #     topLeft = True
                #
                # no_pieces_of_notes_nearby = topLeft and topRight and bottomLeft and bottomRight
                # if top == 462 and col == 42:
                #     print("\t \t Boolean value is: ", no_pieces_of_notes_nearby)
                if image[top-1, col] != 0 and image[bottom+1, col] != 0: # and no_pieces_of_notes_nearby:
                    image[top:bottom, col] = 255
                    if top == 462 and col == 42:
                        print("\t \t pixel removed")

    return image

def main():
    pass


if __name__ == '__main__':
    main()