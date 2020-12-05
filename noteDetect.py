import cv2 as cv
import numpy as np
import utilities_cv
import operator


def remove_dupes(match, width, height):
    # while loops used here as to prevent indexing errors when iterating through matrix which is being reduced
    i = 0
    while i < len(match[1]):
        j = 0
        while j < len(match[1]):
            if j != i:
                # compare each match against all other matches to see if it is within a distance of other matches
                # the distance used here is actually the template size
                if abs(match[1, i] - match[1, j]) < width:
                    if abs(match[0, i] - match[0, j]) < height:
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


def lineLoc(i, staff):
    l = (staff.line_locations[i][0] + staff.line_locations[i][1]) / 2
    return l


def staffCrop(staff, image):
    cv.imshow("image", image)
    cv.waitKey(0)
    staff.l1 = lineLoc(0, staff)
    staff.l2 = lineLoc(1, staff)
    staff.l3 = lineLoc(2, staff)
    staff.l4 = lineLoc(3, staff)
    staff.l5 = lineLoc(4, staff)

    if staff.staff_start - 6 * staff.dis < 0:
        print("cut beginning")
        img = image[0:staff.staff_end + 6 * staff.dis, :]

    elif staff.staff_end + 6 * staff.dis > image.shape[0]:
        print("cut end")
        img = image[staff.staff_start - 6 * staff.dis:image.shape[0], :]

    else:
        print("not cut")
        img = image[staff.staff_start - 6 * staff.dis:staff.staff_end + 6 * staff.dis, :]

    cv.imshow("staff crop", img)
    cv.waitKey(0)
    return img


def noteDetect(staff, img):
    print("running noteDetect")

    # read in image manually from directory for testing
    # img = cv.imread('example_music_1.jpg')
    # cv.imshow("image read in", img)
    # cv.waitKey(0)

    filledTemplate = cv.imread('filled_head.png', cv.IMREAD_GRAYSCALE)
    halfTemplate = cv.imread('half_head.png', cv.IMREAD_GRAYSCALE)
    wholeTemplate = cv.imread('whole_head.png', cv.IMREAD_GRAYSCALE)
    wholeTemplateL = cv.imread('whole_head_line.png', cv.IMREAD_GRAYSCALE)

    quarterRestTemplate = cv.imread('quarter_rest.png', cv.IMREAD_GRAYSCALE)
    eighthRestTemplate = cv.imread('eighth_rest.png', cv.IMREAD_GRAYSCALE)
    sixteenthRestTemplate = cv.imread('sixteenth_rest.png', cv.IMREAD_GRAYSCALE)
    halfRestTemplate = cv.imread('half_rest.png', cv.IMREAD_GRAYSCALE)

    sharpTemplate = cv.imread('sharp.png', cv.IMREAD_GRAYSCALE)
    flatTemplate = cv.imread('flat.png', cv.IMREAD_GRAYSCALE)
    naturalTemplate = cv.imread('natural.png', cv.IMREAD_GRAYSCALE)

    dotTemplate = cv.imread('dot.png', cv.IMREAD_GRAYSCALE)
    accentTemplate = cv.imread('accent.png', cv.IMREAD_GRAYSCALE)

    scale = (staff.dis + 3) / filledTemplate.shape[0]

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
    r_halfRest = resizeTemplate(scale, halfRestTemplate)

    r_sharp = resizeTemplate(scale, sharpTemplate)
    r_flat = resizeTemplate(scale, flatTemplate)
    r_natural = resizeTemplate(scale, naturalTemplate)

    r_dot = resizeTemplate(scale, dotTemplate)
    r_accent = resizeTemplate(scale, accentTemplate)

    cv.imshow("resized filled", r_filled)
    cv.waitKey(0)

    cv.imshow("resized quarter rest", r_quarterRest)
    cv.waitKey(0)



    k = np.ones((1, 2), np.uint8)
    r_quarterRest = cv.morphologyEx(r_quarterRest, cv.MORPH_CLOSE, k)
    cv.imshow("morphed quarter rest", r_quarterRest)
    cv.waitKey(0)

    cv.imshow("resized half rest", r_halfRest)
    cv.waitKey(0)

    F = cv.matchTemplate(img, r_filled, cv.TM_CCOEFF_NORMED)

    H = cv.matchTemplate(img, r_half, cv.TM_CCOEFF_NORMED)

    W = cv.matchTemplate(img, r_whole, cv.TM_CCOEFF_NORMED)

    WL = cv.matchTemplate(img, r_wholeL, cv.TM_CCOEFF_NORMED)

    QR = cv.matchTemplate(img, r_quarterRest, cv.TM_CCOEFF_NORMED)
    cv.imshow("quarter rest scores", QR)
    cv.waitKey(0)

    ER = cv.matchTemplate(img, r_eighthRest, cv.TM_CCOEFF_NORMED)

    SR = cv.matchTemplate(img, r_sixteenthRest, cv.TM_CCOEFF_NORMED)

    HR = cv.matchTemplate(img, r_halfRest, cv.TM_CCOEFF_NORMED)

    #thresh =
    fMatch = np.where(F >= 0.6)
    hMatch = np.where(H >= 0.5)
    wMatch = np.where(W >= 0.7)
    wMatchL = np.where(WL >= 0.7)

    qrMatch = np.where(QR >= 0.58)
    erMatch = np.where(ER >= 0.65)
    srMatch = np.where(SR >= 0.65)
    hrMatch = np.where(HR >= 0.8)

    fMatch = np.asarray(fMatch)
    hMatch = np.asarray(hMatch)
    wMatch = np.asarray(wMatch)
    wMatchL = np.asarray(wMatchL)
    qrMatch = np.asarray(qrMatch)
    erMatch = np.asarray(erMatch)
    srMatch = np.asarray(srMatch)
    hrMatch = np.asarray(hrMatch)

    fMatch = remove_dupes(fMatch, width, height)
    hMatch = remove_dupes(hMatch, width, height)
    wMatch = remove_dupes(wMatch, width, height)
    wMatchL = remove_dupes(wMatchL, width, height)
    qrMatch = remove_dupes(qrMatch, width, height)
    erMatch = remove_dupes(erMatch, width, height)
    srMatch = remove_dupes(srMatch, width, height)
    hrMatch = remove_dupes(hrMatch, width, height)

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
        cv.rectangle(img, (qrMatch[1, i], qrMatch[0, i]), (qrMatch[1, i] + r_quarterRest.shape[1], qrMatch[0, i] + r_quarterRest.shape[0]), (0, 152, 255)) # orange

    for i in range(len(erMatch[1])):
        cv.rectangle(img, (erMatch[1, i], erMatch[0, i]), (erMatch[1, i] + temp_x, erMatch[0, i] + temp_y), (255, 0, 255)) # pink

    for i in range(len(srMatch[1])):
        cv.rectangle(img, (srMatch[1, i], srMatch[0, i]), (srMatch[1, i] + temp_x, srMatch[0, i] + temp_y), (255, 255, 0)) # turquoise

    for i in range(len(hrMatch[1])):
        cv.rectangle(img, (hrMatch[1, i], hrMatch[0, i]), (hrMatch[1, i] + temp_x, hrMatch[0, i] + temp_y), (0, 255, 135)) # green turquoise

    cv.imshow("img box", img)
    cv.waitKey(0)

    notes = []
    quarter_dur = 1
    half_dur = 2 * quarter_dur
    whole_dur = 4 * quarter_dur
    eighth_dur = quarter_dur / 2
    sixteenth_dur = quarter_dur / 4

    for i in range(len(fMatch[1])):
        new_note = utilities_cv.NoteClass(quarter_dur, fMatch[1, i], fMatch[0, i])
        notes.append(new_note)

    for i in range(len(hMatch[1])):
        new_note = utilities_cv.NoteClass(half_dur, hMatch[1, i], hMatch[0, i])
        notes.append(new_note)

    for i in range(len(wMatch[1])):
        new_note = utilities_cv.NoteClass(whole_dur, wMatch[1, i], wMatch[1, i])
        notes.append(new_note)

    for i in range(len(wMatchL[1])):
        new_note = utilities_cv.NoteClass(whole_dur, wMatchL[1, i], wMatchL[1, i])
        notes.append(new_note)

    for i in range(len(qrMatch[1])):
        new_note = utilities_cv.NoteClass(quarter_dur, qrMatch[1, i], None)
        notes.append(new_note)

    for i in range(len(erMatch[1])):
        new_note = utilities_cv.NoteClass(eighth_dur, erMatch[1, i], None)
        notes.append(new_note)

    for i in range(len(srMatch[1])):
        new_note = utilities_cv.NoteClass(sixteenth_dur, srMatch[1, i], None)
        notes.append(new_note)

    for i in range(len(hrMatch[1])):
        new_note = utilities_cv.NoteClass(half_dur, hrMatch[1, i], None)
        notes.append(new_note)

    notes.sort(key=operator.attrgetter('x_val'))

    LCropDist = 2 * staff.dis
    RCropDist = 4 * staff.dis

    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imshow('dot', r_dot)
    cv.waitKey(0)

    d = staff.dis / 4

    print("staff.l1", staff.l1)

    for note in notes:
        print("note.y_val", note.y_val)
        if note.y_val is not None:
            if staff.l1 - d < note.y_val < staff.l1 + d:
                note.pitch = 77
            if staff.l1 + d < note.y_val < staff.l2 - d:
                note.pitch = 76
            if staff.l2 - d < note.y_val < staff.l2 + d:
                note.pitch = 74
            if staff.l2 + d < note.y_val < staff.l3 - d:
                note.pitch = 72
            if staff.l3 - d < note.y_val < staff.l3 + d:
                note.pitch = 71
            if staff.l3 + d < note.y_val < staff.l4 - d:
                note.pitch = 69
            if staff.l4 - d < note.y_val < staff.l4 + d:
                note.pitch = 67
            if staff.l4 + d < note.y_val < staff.l5 - d:
                note.pitch = 65
            if staff.l5 - d < note.y_val < staff.l5 + d:
                note.pitch = 64

    for note in notes:
        if note.y_val is not None:
            print(note.pitch)
    # for note in notes:
    #     crop = img[:, note.x_val - LCropDist:note.x_val + RCropDist]
    #     D = cv.matchTemplate(crop, r_dot, cv.TM_CCOEFF_NORMED)
    #     dMatch = np.where(D >= 0.8)
    #     dMatch = np.asarray(dMatch)
    #     dMatchT = dMatch.transpose()
    #     print("dMatchT", dMatch)
    #     if dMatch is not None:
    #         for match in dMatchT:
    #             print("match", match)
    #         #     if abs(note.y_val - match[0])
    #         # note.duration = 1.5 * note.orig_dur
    #         print("dot found")

        # cv.imshow('crop', crop)
        # cv.waitKey(0)

    # constant = #something scaled by dis
    #
    # for note in notes:
    #     # crop
    #     crop = img[:, note.x_val - constant, note.x_val + constant]
    #     if note.orig_dur == quarter_dur:
    #         # template match flags
    #         if flagmatch > thresh:
    #             note.duration = note.orig_dur / 2
            # assign new duration
        # look for dots



    #for i in range(len(hMatch[1])):


    # look for flags and beams

    # add rests DON'T CHECK DOTS UNTIL AFTER THIS

    # if connected components covers more than one x_val in notesclass



    return staff, img


def main():
    imageout = noteDetect()
    return imageout


if __name__ == "__main__":
    main()
