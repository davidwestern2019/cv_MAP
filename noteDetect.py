import cv2 as cv
import numpy as np


def remove_dupes(match):
    temp_x = 16.2
    temp_y = 13.5
    # while loops used here as to prevent indexing errors when iterating through matrix which is being reduced
    i = 0
    while i < len(match[1]):
        j = 0
        while j < len(match[1]):
            if j != i:
                # compare each match against all other matches to see if it is within a distance of other matches
                # the distance used here is actually the template size
                if abs(match[1, i] - match[1, j]) < temp_x:
                    if abs(match[0, i] - match[0, j]) < temp_y:
                        # delete any duplicate matches
                        match = np.delete(match, j, 1)

                        # roll the 'j' index back one, because otherwise, a value would be skipped after deletion
                        j = j - 1
            j = j + 1
        i = i + 1
    return match


def get_xy(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(x, y)
        param.append((x, y))
    return param


def noteDetect(staves, img):
    print("running noteDetect")

    # read in image manually from directory for testing
    # img = cv.imread('example_music_1.jpg')
    cv.imshow("image read in", img)
    cv.waitKey(0)

    filledTemplate = cv.imread('filled_head.png')
    halfTemplate = cv.imread('half_head.png')
    wholeTemplate = cv.imread('whole_head.png')

    scale = 0.021
    width = int(filledTemplate.shape[1] * scale)
    height = int(filledTemplate.shape[0] * scale)
    dim = (width, height)
    wwidth = int(wholeTemplate.shape[1] * scale)
    wdim = (wwidth, height)
    temp_x = width
    temp_y = height
    print(0.9 * temp_x)
    print(0.9 * temp_y)

    r_filled = cv.resize(filledTemplate, dim, interpolation=cv.INTER_AREA)
    r_half = cv.resize(halfTemplate, dim, interpolation=cv.INTER_AREA)
    r_whole = cv.resize(wholeTemplate, wdim, interpolation=cv.INTER_AREA)

    F = cv.matchTemplate(img, r_filled, cv.TM_CCOEFF_NORMED)
    cv.imshow("filled scores", F)
    cv.waitKey(0)
    print(F)

    H = cv.matchTemplate(img, r_half, cv.TM_CCOEFF_NORMED)
    cv.imshow("half scores", H)
    cv.waitKey(0)

    W = cv.matchTemplate(img, r_whole, cv.TM_CCOEFF_NORMED)
    cv.imshow("whole scores", W)
    cv.waitKey(0)

    thresh = 0.75
    fMatch = np.where(F >= thresh)
    print(fMatch)
    hMatch = np.where(H >= 0.5)
    wMatch = np.where(W >= thresh)

    fMatch = np.asarray(fMatch)
    print(fMatch)
    hMatch = np.asarray(hMatch)
    wMatch = np.asarray(wMatch)

    fMatch = remove_dupes(fMatch)
    hMatch = remove_dupes(hMatch)
    wMatch = remove_dupes(wMatch)

    for i in range(len(fMatch[1])):
        cv.rectangle(img, (fMatch[1, i], fMatch[0, i]), (fMatch[1, i] + temp_x, fMatch[0, i] + temp_y), (0, 0, 255), 0)

    for i in range(len(hMatch[1])):
        cv.rectangle(img, (hMatch[1, i], hMatch[0, i]), (hMatch[1, i] + temp_x, hMatch[0, i] + temp_y), (0, 255, 0), 1)

    for i in range(len(wMatch[1])):
        cv.rectangle(img, (wMatch[1, i], wMatch[0, i]), (wMatch[1, i] + wwidth, wMatch[0, i] + temp_y), (255, 0, 0), 1)

    cv.imshow("img box", img)
    cv.waitKey(0)

    return staves


def main():
    imageout = noteDetect()
    return imageout


if __name__ == "__main__":
    main()
