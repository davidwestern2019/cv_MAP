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
    for BIN in range(start_row, end_row, binSize):
        count = 0

        # Look at each row within the binSize
        for i in range(0, binSize):
            # count the # of black pixels in the row
            for column in range(0, width):
                row = BIN + i # bin is the start row of the bin and "i" is the number of rows beyond start in bin
                if img[row, column] == 0:
                    count += 1

        # append the count of black pixels
        count_for_each_row.append(count)

    # find locations of peaks
    peaks = 5




def findTopPeaks(numPeaks=5, histogram ):
    # find the five largest peaks. This assumes user includes only one staff per horizontal slice
    copy_count = self.count
    self.peakLocations = np.zeros((5, 1))

    assert (len(copy_count) >= numPeaks)

    for i in range(0, numPeaks):
        a_peak = np.argmax(copy_count)
        print(a_peak)
        self.peakLocations[i] = a_peak
        del copy_count[int(a_peak)]


class h_projection_class:
    "This object is to store the information for horizontal projections"
    count = []
    peakLocations = []

    # def __init__(self):
    #     count =[]

    def findTopPeaks(self, numPeaks = 5, ):
        # find the five largest peaks. This is naive method to find staff lines
        copy_count = self.count
        self.peakLocations = np.zeros((5, 1))

        assert (len(copy_count) >= numPeaks)

        for i in range(0, numPeaks):
            a_peak = np.argmax(copy_count)
            print(a_peak)
            self.peakLocations[i] = a_peak
            del copy_count[int(a_peak)]
        return self.peakLocations


def checkIfImageIsBinary(img, valueforWhite = 255):
    # Set flag
    flag = True

    # test if there are color channels
    sizeOfImage = img.shape
    if len(sizeOfImage) > 2:
        flag = False
        return flag

    # test if there are any non-binary numbers in each pixel
    for x in range(0, img.shape[1]):
        for y in range(0, img.shape[0]):
            if (img[x][y] != 0) or ( img[x][y] != valueforWhite):   # if not a 0 or whatever value white is
                flag = False
                return flag
    return flag


if __name__ == "__main__":
    shape_test_image = (256, 256)
    test_img = np.zeros(shape_test_image)
    horizontal_projection_calc(test_img)