import numpy as np
import cv2 as cv
import vertical_runs
import morphOps
import horizontal_projection
import utilities_cv

def findStaves(image):
    # This program takes a sheet of music and finds the locations of the stafflines, their thickness, spacing, and ...

    print("Looking for staves...")


    # perform vertical run to find staffline thickness and spacing b/w the lines
    black_histogram, white_histogram = vertical_runs.vertical_runs_calc(image)
    staffline_thickness = find_line_thickness(black_histogram)
    staffline_spacing = find_line_spacing(white_histogram)

    # find the location of staves and the spacing between staves
    # -- perform morphological ops
    # -- then perform vertical runs
    # -- extract staff size, location, and spacing
    morphed_image = morphOps.performStaffOps(image, staffline_spacing)
    black_histogram, white_histogram = vertical_runs.vertical_runs_calc(morphed_image)



    # return list of objects. The objects represent a staff and contain staff info. List is sorted from top staff to
    # bottom


def find_line_thickness(histogram):
    # This function is to be used within vertical_runs.py
    # There will be two peaks: each represent line width (at least to my understanding)
    # This is due to the varying thickness of the lines after binarization
    # Choose the larger pixel thickness of the two.
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
    # Choose the larger pixel size of the two.
    thickness = np.argmax(histogram)
    # Check the next bin
    next_thickness = thickness + 1
    if histogram[next_thickness] >= 0.2 * histogram[thickness]:
        thickness = next_thickness
    return thickness


def find_staff_locations(img):
    # this function finds the start and stop location for each staff
    # INPUT
    # -- image that has been morph. operated on to only have filled in staves
    # OUTPUT
    # -- list of tuples. each tuple has the start and end of the staff



    return 0

def find_staff_size(black_histogram):
    # this function gets the vertical length of the staves.
    # use it as a rough estimation of all staff sizes
    staff_size = np.argmax(black_histogram)
    return staff_size


def main():
    test_img = cv.imread("example_music_3.jpg", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    findStaves(test_img)


if __name__ == '__main__':
    main()