import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

def vertical_runs(img):
    # This function performs vertical runs on the entire piece of sheet music (or whatever image is passed to it)
    # This function helps find useful properties like staffline thickness, staffline spacing, spacing between staves,
    # and the height of a staff.
    # OUTPUTS:
    #   histograms of the lengths of black and white runs (uninterrupted lines of a single color)
    # INPUTS:
    #   a binary image of the entire piece of music or just a sliver

    # Image input must be a binary image!!!
    isBinaryImage = checkIfImageIsBinary(img)
    assert (isBinaryImage), "Input argument error: image is not binary!!"

    # Get size of the image
    width = img.shape[1]
    height = img.shape[0]

    white_data = []
    black_data = []
    pixel_count = 0
    for col in range(0, width):
        # set up some stuff here for vertical run
        black_run = 0
        white_run = 0

        for row in range(0, height):
            curr_pixel = img[row, col]
            if curr_pixel == 0:     # check if current pixel is black
                #print("Found black pixel")
                # increase black run. stop and store white run
                black_run += 1  # increase length of black pixel run
                if white_run != 0:                  # reset white run when black pixel if it hasn't been yet
                    white_data.append(white_run)    # store the length of the white pixel run
                    white_run = 0                   # reset length of white run
            elif curr_pixel == 255:
                #print("Found White Pixel")
                # increase white run. stop and store black run
                white_run += 1
                if black_run != 0:
                    black_data.append(black_run)
                    black_run = 0
            else:
                print("Whoops! Something went wrong. Pixel is not 0 or 255")

        # terminate any current runs that aren't zero
        if white_run > 0:
            white_data.append(white_run)
            pixel_count += 1
        if black_run > 0:
            black_data.append(black_run)

    # create histogram for black and white runs.
    hist_black = createHistogram(black_data, height)
    hist_white = createHistogram(white_data, height)
    return hist_black, hist_white


def createHistogram(data, max_val):
    histogram = np.zeros((max_val+1, 1))
    pixel_count = 0
    for value in data:
        if value <= max_val:
            if value !=0:
                #print("Value is: ", value)
                histogram[value] += 1
                pixel_count += value
                #print(histogram.T)
        else:
            print("Error! Run length is longer than the height of the image")
            return None

    #print("Histogram product sum is: ", pixel_count)
    #print("")
    return histogram


def checkIfImageIsBinary(img, valueforWhite=255):
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
            if (img[y][x] != 0) and (img[y][x] != valueforWhite):  # if not a 0 or whatever value white is
                # print("X is ", x, " and y is ", y)
                flag = False
                return flag
    return flag


def main():
    print("Running test...")
    test_img = cv.imread("example_music_3.jpg", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

    # ---------  Use this to create custom image -------------
    # shape_test_image = (256, 256)
    # test_img = np.ones(shape_test_image)*255
    # test_img[10:100, :] = np.zeros((1, 256))
    # test_img[15, :] = np.zeros((1, 256))
    # test_img[20, :] = np.zeros((1, 256))
    # test_img[25, :] = np.zeros((1, 256))
    # test_img[30, :] = np.zeros((1, 256))
    # cv.imshow("Test image", test_img)
    # cv.waitKey(0)

    bh, wh = vertical_runs(test_img)

    cv.imshow("Test Image", test_img)
    cv.waitKey(0)
    plt.plot(bh)
    plt.show()

    # check if histogram got all the pixels
    combined_histogram = np.add(bh, wh)
    width = test_img.shape[1]
    height = test_img.shape[0]
    print("Should see ", width*height, " pixels...")
    print(bh)

    print("Test completed!")


if __name__ == "__main__":
    main()