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
    staffline_thickness = find_line_thickness(black_histogram)  # max thickness of staff lines
    staffline_spacing = find_line_spacing(white_histogram)      # avg space between staff lines

    # find the location of staves and the spacing between staves
    # -- perform morphological ops
    # -- extract staff size and location for each staff. Also get number of staves
    morphed_image = morphOps.performStaffOps(image, staffline_spacing)
    cv.imshow("Morphed Image", morphed_image)
    cv.waitKey(0)
    staves = find_staff_locations(morphed_image)
    print("Found staves. Adding line thickness and spacing...")

    # add parameters to each staff object
    for staff in staves:
        # print("Doing staff ", staff.staff_number)
        staff.dis = staffline_spacing
        # print("Thickness is: ", staffline_thickness)
        # print("Start: ", staff.staff_start, ", End: ", staff.staff_end)
        line_start_locations, line_lengths = horizontal_projection.horizontal_projection_calc(image,
                                            staff.staff_start, staff.staff_end,
                                            binSize=staffline_thickness)

        staff.line_length = int(max(line_lengths)/staffline_thickness)   # use max value of the various line lengths
        start_line_locations = np.sort(line_start_locations, axis=None)     # sort the array of line starting locations
        staff.line_locations = []
        for line_start in start_line_locations:
            # create list of tuples (start, end) for each staffline
            staff.line_locations.append((line_start, line_start+staffline_thickness))

    # just to check to make sure that the objects are getting the right methods
    for staff in staves:
        print("Staff ", staff.staff_number, " has the following:")
        print("\t Line length: ", staff.line_length)
        print("\t Line Locations", staff.line_locations)



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


def find_staff_locations(img, print_Flag=False):
    # this function finds the start and stop location for each staff
    # INPUT
    # -- image that has been morph. operated on to only have filled in staves
    # OUTPUT
    # -- list of Staff objects

    height = img.shape[0]
    width = img.shape[1]
    list_of_staves = []
    num_staves = 0
    is_staff = False

    for row in range(0, height):        # look at each row

        # look for start of staff
        if not is_staff:
            for col in range(0, int(width/2)):    # look for staff up to half page width. Don't bother looking past this
                if img[row, col] == 0:
                    is_staff = True
                    num_staves += 1     # increase number of staves found
                    staff_start = row
                    if print_Flag:
                        print("Found start of staff ", num_staves)
                        print("Staff starts at ", row)
                    new_staff = utilities_cv.StaffClass(num_staves)     # create staff object
                    new_staff.staff_start = staff_start
                    new_staff.staff_number = num_staves
                    list_of_staves.append(new_staff)        # append new staff object to list
                    break
            # end of for loop
            continue    # skip the next section to avoid going through next if statement

        # look for end of staff
        if is_staff:
            black_pixel_count = 0
            for col in range(0, width):    # look for a completely white row
                if img[row, col] == 0:
                    black_pixel_count += 1  # increase tally of black pixels
            # end of for loop

            # end of staff when a white row is found
            if black_pixel_count == 0:
                if print_Flag:
                    print("Found end of a staff at line", row-1)
                list_of_staves[num_staves-1].staff_end = row-1
                is_staff = False
        # end of if
    # end of for loop going over rows
    return list_of_staves


def find_staff_size(black_histogram):
    # this function gets the vertical length of the staves.
    # use it as a rough estimation of all staff sizes
    staff_size = np.argmax(black_histogram)
    return staff_size


def main():
    # Use this to use a piece of sample music
    test_img = cv.imread("example_music_4.jpg", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    # ---------  Use this to create custom image -------------
    # shape_test_image = (256, 256)
    # test_img = np.ones(shape_test_image)*255
    # test_img[10:100, :] = np.zeros((1, 256))
    # test_img[200:220, :] = np.zeros((1, 256))
    cv.imshow("Test image", test_img)
    cv.waitKey(0)

    findStaves(test_img)

    picked_point = []
    pick_window = "Test Image"
    cv.namedWindow(pick_window, cv.WINDOW_NORMAL)
    cv.setMouseCallback(pick_window, utilities_cv.get_xy, picked_point)
    cv.imshow(pick_window, test_img)
    cv.waitKey(0)

if __name__ == '__main__':
    main()