import cv2 as cv
import numpy as np

def vertical_runs(img):
    # This function performs vertical runs on the entire piece of sheet music (or whatever image is passed to it)
    # This function finds useful properties like staff spacing, staffline thickness, staffline spacing, and


    # Image input must be a binary image!!!
    isBinaryImage = checkIfImageIsBinary(img)
    assert (isBinaryImage), "Input argument error: image is not binary!!"

    # Get size of the image
    width = img.shape[1]
    height = img.shape[0]

    


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
    test_img = cv.imread("test_staff_img_1.png", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 150, 255, cv.THRESH_BINARY)
    vertical_runs(test_img)


    print("Test completed!")

if __name__ == "__main__":
    main()