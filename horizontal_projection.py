import cv2 as cv
import numpy as np



def horizontal_projection_calc(img, start_row, end_row, binSize=1, peaks=5):
    #
    # You MUST choose a horizontal slice that has only 1 (ONE) staff in it. Any more leads to erroneous results
    # Note: the difference between start_row and end_row must be a factor of binSize. In case its not, this program uses
    # end_row = end_row+x, where x is needed to make the difference a multiple of binSize
    #
    # INPUTS
    #   img             = image of sheet music. MUST be binary
    #   start_row       = beginning of horizontal slice of img
    #   end_row         = second to last row of horizontal slice
    #   binSize         = size of bins for histogram.
    # OUTPUTS
    #   peakLocations   = the row coordinates where the stafflines are. Returns 5 locations.
    #   peakHeights     = the height of the peaks (length of staff lines)

    # Image input must be a binary image!!!
    isBinaryImage = checkIfImageIsBinary(img)
    assert (isBinaryImage), "Input argument error: image is not binary!!"

    # Get size of the image
    width = img.shape[1]
    height = img.shape[0]

    # Adjust start and end row such that each bin has same amount of rows in it (and none are skipped)
    start_row, end_row = adjustBounds(start_row, end_row, binSize, height)

    # Loop over each row
    count_for_each_row = []
    pixel_check = 0
    for BIN in range(start_row, end_row, binSize):
        # print("Bin count is:", BIN)
        count = 0
        # Look at each row within the binSize
        for i in range(0, binSize):
            # count the # of black pixels in the row
            for column in range(0, width):
                row = BIN + i   # bin is the start row of the bin and "i" is the number of rows beyond start in bin
                pixel_check += 1
                if img[row, column] == 0:
                    count += 1
        # append the count of black pixels
        count_for_each_row.append(count)

    # print(count_for_each_row)
    # print("Pixel count is ", pixel_check)
    # print((end_row-start_row)*width)
    assert (pixel_check == (end_row-start_row)*width), "Error! Not every pixel was counted"

    # find locations of peaks and their heights. This is equivalent to finding the staffline locations and the length
    # of the staff lines
    # peaks = 5 # was a default value. now its a possible
    peakLocations, peakHeights = findTopPeaks(count_for_each_row, peaks)
    peakLocations *= binSize
    peakLocations += start_row
    return peakLocations, peakHeights


def adjustBounds(start, end, dividend, max_end_value):
    remainder = (end-start) % dividend
    while remainder != 0:
        end = end+1
        remainder = (end - start) % dividend
        assert end < max_end_value, "Uh-oh. Ran out of room to add to end row. Check bin size"
    return start, end


def findTopPeaks(histogram, numPeaks=5):
    # print(histogram)
    # find the five largest peaks. This assumes user includes only one staff per horizontal slice
    peakLocations = np.zeros((numPeaks, 1))
    peakHeights = np.zeros((numPeaks, 1))

    assert (len(histogram) >= numPeaks)

    for i in range(0, numPeaks):
        #print(i)
        a_peak = np.argmax(histogram)
        peak_height = max(histogram)
        peakLocations[i] = a_peak
        peakHeights[i] = peak_height
        histogram[int(a_peak)] = 0
    return peakLocations, peakHeights


def checkIfImageIsBinary(img, valueforWhite = 255):
    # Set flag
    flag = True

    # test if there are color channels
    sizeOfImage = img.shape
    if len(sizeOfImage) > 2:
        flag = False
        # print("Whoops! Image is not two-dimensional")
        return flag

    # test if there are any non-binary numbers in each pixel
    for x in range(0, img.shape[1]):
        for y in range(0, img.shape[0]):
            # print(x)
            if (img[y][x] != 0) and (img[y][x] != valueforWhite):   # if not a 0 or whatever value white is
                # print("X is ", x, " and y is ", y)
                flag = False
                return flag
    return flag


def main():
    # This function is just for testing the functions in this file


    # shape_test_image = (256, 256)
    # test_img = np.ones(shape_test_image)*255
    # test_img[10, :] = np.zeros((1, 256))
    # test_img[15, :] = np.zeros((1, 256))
    # test_img[20, :] = np.zeros((1, 256))
    # test_img[25, :] = np.zeros((1, 256))
    # test_img[30, :] = np.zeros((1, 256))
    # horizontal_projection_calc(test_img, start_row=5, end_row=50)

    test_img = cv.imread("example_music_3.jpg", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 150, 255, cv.THRESH_BINARY)
    # cv.imshow("Test image", test_img)
    # cv.waitKey(0)
    img_width = test_img.shape[1]
    img_height = test_img.shape[0]
    # print(img_width)
    # print(img_height)
    staff_locations, staffline_lengths = horizontal_projection_calc(test_img, start_row=578, end_row=619, binSize=2)
    print("Locations are \n", staff_locations)
    print("Staff lengths are: \n", staffline_lengths)
    #test_img_color =np.zeros((img_height, img_width, 3))
    #cv.cvtColor(test_img, test_img_color, cv.COLOR_GRAY2BGR)
    for i in range(0, len(staff_locations)):
        staff_loc = (10, staff_locations[i])
        cv.drawMarker(test_img, staff_loc,(0,0,255), cv.MARKER_STAR)
    cv.imshow("Annotated image", test_img)
    cv.waitKey(0)


if __name__ == "__main__":
    main()
