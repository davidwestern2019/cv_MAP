import cv2 as cv
import numpy as np
import utilities_cv


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


def resizeTemplate(scale, template):
    width = int(template.shape[1] * scale)
    height = int(template.shape[0] * scale)
    dim = (width, height)
    scaleTemplate = cv.resize(template, dim, interpolation=cv.INTER_AREA)
    return scaleTemplate


def staffCrop(staff, image):
    cv.imshow("image", image)
    cv.waitKey(0)
    img = image[staff.staff_start:staff.staff_end + 6 * staff.dis, 0:630]
    cv.imshow("staff crop", img)
    cv.waitKey(0)
    #staff.staff_start - 6 * staff.dis       (this should be the first y dimension for crop)
    # add buffer white space to top and bottom of input sheet music so staff crop has room to work?
    # how to maintain width? my code sucks here
    return img


def noteDetect(staves, staff, img):
    print("running noteDetect")

    # read in image manually from directory for testing
    # img = cv.imread('example_music_1.jpg')
    cv.imshow("image read in", img)
    cv.waitKey(0)

    filledTemplate = cv.imread('filled_head.png', cv.IMREAD_GRAYSCALE)
    halfTemplate = cv.imread('half_head.png', cv.IMREAD_GRAYSCALE)
    wholeTemplate = cv.imread('whole_head.png', cv.IMREAD_GRAYSCALE)
    wholeTemplateL = cv.imread('whole_head_line.png', cv.IMREAD_GRAYSCALE)

    quarterRestTemplate = cv.imread('quarter_rest.png', cv.IMREAD_GRAYSCALE)
    eighthRestTemplate = cv.imread('eighth_rest.png', cv.IMREAD_GRAYSCALE)
    sixteenthRestTemplate = cv.imread('sixteenth_rest.png', cv.IMREAD_GRAYSCALE)

    scale = (staves[0].dis + 3) / filledTemplate.shape[0]

    width = int(filledTemplate.shape[1] * scale)
    height = int(filledTemplate.shape[0] * scale)
    dim = (width, height)
    wwidth = int(wholeTemplate.shape[1] * scale)
    wdim = (wwidth, height)
    temp_x = width
    temp_y = height
    # print(0.9 * temp_x)
    # print(0.9 * temp_y)

    r_filled = cv.resize(filledTemplate, dim, interpolation=cv.INTER_AREA)
    r_half = cv.resize(halfTemplate, dim, interpolation=cv.INTER_AREA)
    r_whole = cv.resize(wholeTemplate, wdim, interpolation=cv.INTER_AREA)
    r_wholeL = cv.resize(wholeTemplateL, wdim, interpolation=cv.INTER_AREA)

    r_quarterRest = resizeTemplate(scale, quarterRestTemplate)
    r_eighthRest = resizeTemplate(scale, eighthRestTemplate)
    r_sixteenthRest = resizeTemplate(scale, sixteenthRestTemplate)

    cv.imshow("resized filled", r_filled)
    cv.waitKey(0)

    cv.imshow("resized quarter rest", r_quarterRest)
    cv.waitKey(0)



    #k = np.ones((1, 2), np.uint8)
    #r_quarterRest = cv.morphologyEx(r_quarterRest, cv.MORPH_CLOSE, k)
    cv.imshow("morphed quarter rest", r_quarterRest)
    cv.waitKey(0)

    F = cv.matchTemplate(img, r_filled, cv.TM_CCOEFF_NORMED)
    #cv.imshow("filled scores", F)
    #cv.waitKey(0)

    H = cv.matchTemplate(img, r_half, cv.TM_CCOEFF_NORMED)
    #cv.imshow("half scores", H)
    #cv.waitKey(0)

    W = cv.matchTemplate(img, r_whole, cv.TM_CCOEFF_NORMED)
    #cv.imshow("whole scores", W)
    #cv.waitKey(0)

    WL = cv.matchTemplate(img, r_wholeL, cv.TM_CCOEFF_NORMED)
    #cv.imshow("whole L scores", WL)
    #cv.waitKey(0)

    QR = cv.matchTemplate(img, r_quarterRest, cv.TM_CCOEFF_NORMED)

    ER = cv.matchTemplate(img, r_eighthRest, cv.TM_CCOEFF_NORMED)

    SR = cv.matchTemplate(img, r_sixteenthRest, cv.TM_CCOEFF_NORMED)

    #thresh =
    fMatch = np.where(F >= 0.6)
    hMatch = np.where(H >= 0.45)
    wMatch = np.where(W >= 0.7)
    wMatchL = np.where(WL >= 0.7)

    qrMatch = np.where(QR >= 0.58)
    erMatch = np.where(ER >= 0.65)
    srMatch = np.where(SR >= 0.65)

    fMatch = np.asarray(fMatch)
    hMatch = np.asarray(hMatch)
    wMatch = np.asarray(wMatch)
    wMatchL = np.asarray(wMatchL)
    qrMatch = np.asarray(qrMatch)
    erMatch = np.asarray(erMatch)
    srMatch = np.asarray(srMatch)

    fMatch = remove_dupes(fMatch)
    hMatch = remove_dupes(hMatch)
    wMatch = remove_dupes(wMatch)
    wMatchL = remove_dupes(wMatchL)
    qrMatch = remove_dupes(qrMatch)
    erMatch = remove_dupes(erMatch)
    srMatch = remove_dupes(srMatch)

    img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)

    for i in range(len(fMatch[1])):
        cv.rectangle(img, (fMatch[1, i], fMatch[0, i]), (fMatch[1, i] + temp_x, fMatch[0, i] + temp_y), (0, 0, 255))

    for i in range(len(hMatch[1])):
        cv.rectangle(img, (hMatch[1, i], hMatch[0, i]), (hMatch[1, i] + temp_x, hMatch[0, i] + temp_y), (0, 255, 0))

    for i in range(len(wMatch[1])):
        cv.rectangle(img, (wMatch[1, i], wMatch[0, i]), (wMatch[1, i] + wwidth, wMatch[0, i] + temp_y), (255, 0, 0))

    for i in range(len(wMatchL[1])):
        cv.rectangle(img, (wMatchL[1, i], wMatchL[0, i]), (wMatchL[1, i] + wwidth, wMatchL[0, i] + temp_y), (255, 0, 0))

    for i in range(len(qrMatch[1])):
        cv.rectangle(img, (qrMatch[1, i], qrMatch[0, i]), (qrMatch[1, i] + temp_x, qrMatch[0, i] + temp_y), (0, 152, 255)) # yellow

    for i in range(len(erMatch[1])):
        cv.rectangle(img, (erMatch[1, i], erMatch[0, i]), (erMatch[1, i] + temp_x, erMatch[0, i] + temp_y), (255, 0, 255)) # pink

    for i in range(len(srMatch[1])):
        cv.rectangle(img, (srMatch[1, i], srMatch[0, i]), (srMatch[1, i] + temp_x, srMatch[0, i] + temp_y), (255, 255, 0)) # turquoise

    cv.imshow("img box", img)
    cv.waitKey(0)

    for j in range(len(staves)):
        for i in range(len(fMatch[1])):
            if staves[j].staff_start - 6 * staves[j].dis < fMatch[0, i] < staves[0].staff_end + 6 * staves[0].dis:
                new_note = utilities_cv.StaffClass(j).notes



    return staves


def main():
    imageout = noteDetect()
    return imageout


if __name__ == "__main__":
    main()
