import numpy as np
import cv2 as cv
import vertical_runs
import morphOps
import horizontal_projection
import utilities_cv
import statistics
import operator


def findStaves(image):
    # This program takes a sheet of music and finds the locations of the stafflines, their thickness, spacing, and ...

    print("Looking for staves...")

    # perform vertical run to find staffline thickness and spacing b/w the lines
    black_histogram, white_histogram = vertical_runs.vertical_runs_calc(image)
    staffline_spacing = find_line_spacing(white_histogram)  # avg space between staff lines

    # find the location of staves and the spacing between staves
    # -- perform morphological ops
    # -- extract staff size and location for each staff. Also get number of staves
    morphed_image = morphOps.performStaffOps(image, staffline_spacing)
    staves = find_staff_locations(morphed_image)

    # add parameters to each staff object
    bin_size = 1  # look at every row
    for staff in staves:
        staff.dis = staffline_spacing
        line_start_locations = horizontal_projection.horizontal_projection_calc(image,
                                                                                   staff.staff_start,
                                                                                   staff.staff_end,
                                                                                   binSize=bin_size,
                                                                                   peaks=0)

        # clean up the staff line locations. fix lines that should be connected together
        staff.line_locations = stitchLinesTogether(line_start_locations, staff)

    # return list of objects. The objects represent a staff and contain staff info. List is sorted from top staff to
    # bottom
    return staves


def stitchLinesTogether(possible_line_locations, staff):
    staff_width = staff.line_length
    start = staff.staff_start
    line_locations = []
    wiggle_room = 0.95

    # put lines together if they are touching
    is_line = False
    new_line_start = 0
    for i in range(0, len(possible_line_locations)):
        # print("Staffline ", i+start, " has a count of ", possible_line_locations[i] )
        if possible_line_locations[i] > staff_width * wiggle_room:
            # Have found a line. It is either:
            #   1. start of new line
            #   2. continuation of line
            if not is_line:
                # 1. Start of a new line
                # print("\t Found start at ", i+start)
                new_line_start = i
                is_line = True

        else:
            # Have found a not line. It is either end of a line or other
            if is_line:
                # terminate line and add location tuple to list
                # print("\t Found end at ", i+start)
                new_line_end = i
                location = (new_line_start + start, new_line_end + start)
                line_locations.append(location)
                is_line = False


    # Check for more than 5 lines.
    five_staff_locations = None
    if len(line_locations) < 6:
        five_staff_locations = line_locations
    else:
        print("UH-OH. There are more than 5 staff lines!")
        fiv_staff_locations = None

    return five_staff_locations


def find_line_thickness(histogram):
    # This function is to be used within vertical_runs.py
    # There will be two peaks: each represent line width (at least to my understanding)
    # This is due to the varying thickness of the lines after binarization
    # Choose the larger pixel thickness of the two.
    thickness = np.argmax(histogram)
    # Check the next bin
    next_thickness = thickness + 1
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

    for row in range(0, height):  # look at each row

        # look for start of staff
        if not is_staff:
            for col in range(0, int(width / 2)):  # look for staff up to half page width. Don't bother looking past this
                if img[row, col] == 0:
                    is_staff = True
                    num_staves += 1  # increase number of staves found
                    staff_start = row
                    if print_Flag:
                        print("Found start of staff ", num_staves)
                        print("Staff starts at ", row)
                    new_staff = utilities_cv.StaffClass(num_staves)  # create staff object
                    new_staff.staff_start = staff_start
                    new_staff.staff_number = num_staves
                    list_of_staves.append(new_staff)  # append new staff object to list
                    break
            # end of for loop
            continue  # skip the next section to avoid going through next if statement

        # look for end of staff
        if is_staff:
            black_pixel_count = 0
            for col in range(0, width):  # look for a completely white row
                if img[row, col] == 0:
                    black_pixel_count += 1  # increase tally of black pixels
            # end of for loop

            # if not an entirely white row, find width of staff
            if black_pixel_count != 0:
                list_of_staves[num_staves - 1].line_length = black_pixel_count

            # end of staff when a white row is found
            if black_pixel_count == 0:
                if print_Flag:
                    print("Found end of a staff at line", row - 1)
                list_of_staves[num_staves - 1].staff_end = row - 1
                is_staff = False
        # end of if
    # end of for loop going over rows

    # Filter out borders
    # -- need to make sure that only the staves are returned.
    # -- issues have come up with borders being counted as staves
    # -- I suspect that big titles or illustrations might pose an issue as well
    list_staff_heights = []
    max_height = 0
    fix_numbering = False  # if false staves are removed, need to fix staff numbering
    for i in range(0, len(list_of_staves)):
        # if there isn't a staff_end, that means the black region is on the bottom, and highly likely not a staff
        if list_of_staves[i].staff_end is None or list_of_staves[i].staff_start is None:
            print("Removed a false staff at top/bottom. Removed staff ", list_of_staves[i].staff_number)
            del list_of_staves[i]  # remove staff from list
            fix_numbering = True
            continue  # move on to next "staff" object

        staff_height = list_of_staves[i].staff_end - list_of_staves[
            i].staff_start  # find height (horizontal distance) of staff
        list_staff_heights.append(staff_height)
        if staff_height > max_height:
            max_height = staff_height  # real staves are much taller than page borders

    # find and delete "staves" whose size is much less than the real staff size
    for i in range(0, len(list_staff_heights)):
        if list_staff_heights[i] < 0.8 * max_height:
            print("Removed a false staff. Too short. Removed staff ", list_of_staves[i].staff_number)
            del list_of_staves[i]  # remove bogus staff object
            fix_numbering = True
    # DONE filtering out borders

    # possibly fix staff numbering
    if fix_numbering:
        for i in range(0, len(list_of_staves)):
            list_of_staves[i].staff_number = i + 1

    return list_of_staves


def find_staff_size(black_histogram):
    # this function gets the vertical length of the staves.
    # use it as a rough estimation of all staff sizes
    staff_size = np.argmax(black_histogram)
    return staff_size


def main():
    # Use this to use a piece of sample music
    test_img = cv.imread("example_music_3.jpg", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 180, 255, cv.THRESH_BINARY)

    # ---------  Use this to create custom image -------------
    # shape_test_image = (256, 256)
    # test_img = np.ones(shape_test_image)*255
    # test_img[10:100, :] = np.zeros((1, 256))
    # test_img[200:220, :] = np.zeros((1, 256))
    # cv.imshow("Test image", test_img)
    # cv.waitKey(0)

    picked_point = []
    pick_window = "Test Image"
    cv.namedWindow(pick_window, cv.WINDOW_NORMAL)
    cv.setMouseCallback(pick_window, utilities_cv.get_xy, picked_point)
    cv.imshow(pick_window, test_img)
    cv.waitKey(0)

    findStaves(test_img)


if __name__ == '__main__':
    main()
