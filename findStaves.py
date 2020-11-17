import numpy as np
import cv2 as cv
import vertical_runs

def findStaves(image):
    # This program takes a sheet of music and finds the locations of the stafflines, their thickness, spacing, and ...

    print("Looking for staves...")

    # perform vertical run to find staffline thickness and spacing b/w the lines
    black_histogram, white_histogram = vertical_runs(image)

    # find the location of staves and the spacing between staves
    # -- perform morphological ops
    # -- then perform vertical runs


def find_line_thickness(histogram):
    # This function is to be used within vertical_runs.py
    # There will be two peaks: each represent line width (at least to my understanding)
    # This is due to the varying thickness of the lines after binarization
    # Choose the large pixel thickness of the two.
    thickness = np.argmax(histogram)
    # Check the next bin
    next_thickness = thickness+1
    if histogram[next_thickness] >= 0.2 * histogram[thickness]:
        thickness = next_thickness
    return thickness


def find_line_spacing(histogram):
    # This function is to be used within vertical_runs.py
    # There will be two peaks: each represent spacing width (at least to my understanding)
    # This is due to the varying spacing after binarization of the image
    # Choose the large pixel size of the two.
    thickness = np.argmax(histogram)
    # Check the next bin
    next_thickness = thickness + 1
    if histogram[next_thickness] >= 0.2 * histogram[thickness]:
        thickness = next_thickness
    return thickness


#def find_staff_gaps():


#def find_staff_start_end():