import cv2 as cv
import numpy as np



def horizontal_projection_calc(img, start_row, end_row, binSize=1):
    #
    # You MUST choose a horizontal slice that has only 1 (ONE) staff in it. Any more leads to erroneous results
    #
    # INPUTS
    #   img             = image of sheet music. Must be binary
    #   start_row       = beginning of horizontal slice of img
    #   end_row         = second to last row of horizontal slice
    #   binSize         = size of bins for histogram.
    # OUTPUTS

    # Image input must be a binary image!!!
    isBinaryImage = checkIfImageIsBinary(img)
    assert (isBinaryImage), "Input argument error: image is not binary!!"

    # Get size of the image
    width = img.shape[1]
    height = img.shape[0]

    # Loop over each row
    count_for_each_row = []
    pixel_check = 0
    for BIN in range(start_row, end_row, binSize):
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

    #print(count_for_each_row)
    assert (pixel_check == (end_row-start_row)*width), "Error! Not every pixel was counted"

    # find locations of peaks
    peaks = 5
    peakLocations = findTopPeaks(count_for_each_row, peaks)
    peakLocations += start_row
    return peakLocations



def findTopPeaks(histogram, numPeaks=5):
    #print(histogram)
    # find the five largest peaks. This assumes user includes only one staff per horizontal slice
    peakLocations = np.zeros((5, 1))

    assert (len(histogram) >= numPeaks)

    for i in range(0, numPeaks):
        #print(i)
        a_peak = np.argmax(histogram)
        # print(a_peak)
        peakLocations[i] = a_peak
        histogram[int(a_peak)] = 0
    return peakLocations


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
    # shape_test_image = (256, 256)
    # test_img = np.ones(shape_test_image)*255
    # test_img[10, :] = np.zeros((1, 256))
    # test_img[15, :] = np.zeros((1, 256))
    # test_img[20, :] = np.zeros((1, 256))
    # test_img[25, :] = np.zeros((1, 256))
    # test_img[30, :] = np.zeros((1, 256))
    # horizontal_projection_calc(test_img, start_row=5, end_row=50)

    test_img = cv.imread("test_staff_img_1.png", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 150, 255, cv.THRESH_BINARY)
    # cv.imshow("Test image", test_img)
    # cv.waitKey(0)
    img_width = test_img.shape[1]
    img_height = test_img.shape[0]
    print(img_width)
    print(img_height)
    staff_locations = horizontal_projection_calc(test_img, start_row=0, end_row=img_height)
    print(staff_locations)
    #test_img_color =np.zeros((img_height, img_width, 3))
    #cv.cvtColor(test_img, test_img_color, cv.COLOR_GRAY2BGR)
    for i in range(0, len(staff_locations)):
        staff_loc = (10, staff_locations[i])
        cv.drawMarker(test_img,staff_loc,(0,0,255), cv.MARKER_STAR)
    cv.imshow("Annotated image", test_img)
    cv.waitKey(0)


if __name__ == "__main__":
    main()
