import cv2 as cv
import numpy as np
import horizontal_projection
import findStaves
import vertical_runs


def performStaffOps(img, dis):
    # get image parameters
    img_height = img.shape[0]
    img_width = img.shape[1]

    # invert image
    img_inv = invertBinaryImage(img)

    # dilate with vertical block
    block_width_dil_1 = 5
    block_height_dil_1 = dis+3
    kernel = np.ones((block_height_dil_1, block_width_dil_1), np.uint8)
    img_dil = cv.dilate(img_inv, kernel=kernel)
    #cv.imshow("Dilated Image", img_dil)

    # erode with horizontal block
    # find the length of the stafflines with horizontal projections
    _, staffline_lengths = horizontal_projection.horizontal_projection_calc(img_dil, start_row=0, end_row=img_height)
    block_width_erod = int(max(staffline_lengths)*0.8)
    #print("Staffline lengths: ", staffline_lengths)
    #print('Image width is: ', img_width)
    block_height_erod = dis
    kernel = np.ones((block_height_erod, block_width_erod), np.uint8)
    img_erode = cv.erode(img_dil, kernel)
    #cv.imshow("Eroded Image", img_erode)

    # dilate with skinny horizontal block
    block_width_dil_1 = block_width_erod - block_width_dil_1
    block_height_dil_1 = 1
    kernel = np.ones((block_height_dil_1, block_width_dil_1), np.uint8)
    img_dil_2 = cv.dilate(img_erode, kernel=kernel)
    #cv.imshow("2nd Dilation Image", img_dil_2)

    # invert image to get back to black text
    img = invertBinaryImage(img_dil_2)
    return img

def invertBinaryImage(img):
    size = img.shape
    invert_img = np.ones(size)*255 - img
    return invert_img


def main():
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

    test_img = cv.imread("example_music_3.jpg", cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(test_img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    black_hist, white_hist = vertical_runs.vertical_runs_calc(test_img)
    dis = findStaves.find_line_spacing(white_hist)

    filtered_img = performStaffOps(test_img, dis)

    #cv.imshow("Staves only", filtered_img)
    #cv.imshow("Original Image", test_img)



    cv.waitKey(0)


if __name__ == '__main__':
    main()