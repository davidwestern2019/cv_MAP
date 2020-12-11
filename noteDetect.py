import cv2 as cv
import numpy as np
import utilities_cv
import operator


def getPitchValue(staff, value):
    d = staff.dis / 4
    if staff.l1 - 9 * d <= value <= staff.l1 - 7 * d:
        pitch = 84
    if staff.l1 - 7 * d <= value <= staff.l1 - 5 * d:
        pitch = 83
    if staff.l1 - 5 * d <= value <= staff.l1 - 3 * d:
        pitch = 81
    if staff.l1 - 3 * d <= value <= staff.l1 - d:
        pitch = 79
    if staff.l1 - d <= value <= staff.l1 + d:
        pitch = 77
    if staff.l1 + d <= value <= staff.l2 - d:
        pitch = 76
    if staff.l2 - d <= value <= staff.l2 + d:
        pitch = 74
    if staff.l2 + d <= value <= staff.l3 - d:
        pitch = 72
    if staff.l3 - d <= value <= staff.l3 + d:
        pitch = 71
    if staff.l3 + d <= value <= staff.l4 - d:
        pitch = 69
    if staff.l4 - d <= value <= staff.l4 + d:
        pitch = 67
    if staff.l4 + d <= value <= staff.l5 - d:
        pitch = 65
    if staff.l5 - d <= value <= staff.l5 + d:
        pitch = 64
    if staff.l5 + d <= value <= staff.l5 + 3 * d:
        pitch = 62
    if staff.l5 + 3 * d <= value <= staff.l5 + 5 * d:
        pitch = 60
    if staff.l5 + 5 * d <= value <= staff.l5 + 7 * d:
        pitch = 59
    if staff.l5 + 7 * d <= value <= staff.l5 + 9 * d:
        pitch = 57

    return pitch


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
    cv.imshow("staffless", image)
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
        start = staff.staff_start - 6 * staff.dis
        staff.l1 = staff.l1 - start
        staff.l2 = staff.l2 - start
        staff.l3 = staff.l3 - start
        staff.l4 = staff.l4 - start
        staff.l5 = staff.l5 - start

    else:
        print("not cut")
        img = image[staff.staff_start - 6 * staff.dis:staff.staff_end + 6 * staff.dis, :]
        start = staff.staff_start - 6 * staff.dis
        staff.l1 = staff.l1 - start
        staff.l2 = staff.l2 - start
        staff.l3 = staff.l3 - start
        staff.l4 = staff.l4 - start
        staff.l5 = staff.l5 - start

    # cv.imshow("staff crop", img)
    # cv.waitKey(0)
    return img


def noteDetect(staff, img, keyFlats, keySharps):
    print("running noteDetect")

    # read in image manually from directory for testing
    # img = cv.imread('example_music_1.jpg')
    # cv.imshow("image read in", img)
    # cv.waitKey(0)

    filledTemplate = cv.imread('filled_head.png', cv.IMREAD_GRAYSCALE)
    halfTemplate = cv.imread('half_head.png', cv.IMREAD_GRAYSCALE)
    wholeTemplate = cv.imread('whole_head.png', cv.IMREAD_GRAYSCALE)
    wholeTemplateL = cv.imread('whole_head_line.png', cv.IMREAD_GRAYSCALE)

    flag8d = cv.imread('f8thD.png', cv.IMREAD_GRAYSCALE)
    flag8u = cv.imread('f8thU.png', cv.IMREAD_GRAYSCALE)
    flag16d = cv.imread('f16thD.png', cv.IMREAD_GRAYSCALE)
    flag16u = cv.imread('f16thU.png', cv.IMREAD_GRAYSCALE)

    quarterRestTemplate = cv.imread('quarter_rest.png', cv.IMREAD_GRAYSCALE)
    eighthRestTemplate = cv.imread('eighth_rest.png', cv.IMREAD_GRAYSCALE)
    sixteenthRestTemplate = cv.imread('sixteenth_rest.png', cv.IMREAD_GRAYSCALE)
    halfRestTemplate = cv.imread('half_rest.png', cv.IMREAD_GRAYSCALE)

    sharpTemplate = cv.imread('sharp.png', cv.IMREAD_GRAYSCALE)
    flatTemplate = cv.imread('flat.png', cv.IMREAD_GRAYSCALE)
    naturalTemplate = cv.imread('natural.png', cv.IMREAD_GRAYSCALE)

    dotTemplate = cv.imread('dot.png', cv.IMREAD_GRAYSCALE)
    accentTemplate = cv.imread('accent.png', cv.IMREAD_GRAYSCALE)

    tClefTemplate = cv.imread('treble_clef.png', cv.IMREAD_GRAYSCALE)

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

    r_flag8u = resizeTemplate(scale, flag8u)
    r_flag8d = resizeTemplate(scale, flag8d)
    r_flag16u = resizeTemplate(scale, flag16u)
    r_flag16d = resizeTemplate(scale, flag16d)

    r_quarterRest = resizeTemplate(scale, quarterRestTemplate)
    r_eighthRest = resizeTemplate(scale, eighthRestTemplate)
    r_sixteenthRest = resizeTemplate(scale, sixteenthRestTemplate)
    r_halfRest = resizeTemplate(scale, halfRestTemplate)

    r_sharp = resizeTemplate(scale * 1.25, sharpTemplate)
    r_flat = resizeTemplate(scale, flatTemplate)
    r_natural = resizeTemplate(scale, naturalTemplate)

    r_dot = resizeTemplate(scale * 2, dotTemplate)
    r_accent = resizeTemplate(scale, accentTemplate)

    r_tclef = resizeTemplate(scale * 2.85, tClefTemplate)

    # MORPH FOR QUARTER REST
    k = np.ones((1, 2), np.uint8)
    r_quarterRest = cv.morphologyEx(r_quarterRest, cv.MORPH_CLOSE, k)
    # cv.imshow("morphed quarter rest", r_quarterRest)
    # cv.waitKey(0)
    #
    # cv.imshow("resized half rest", r_halfRest)
    # cv.waitKey(0)

    F = cv.matchTemplate(img, r_filled, cv.TM_CCOEFF_NORMED)

    H = cv.matchTemplate(img, r_half, cv.TM_CCOEFF_NORMED)

    W = cv.matchTemplate(img, r_whole, cv.TM_CCOEFF_NORMED)

    # WL = cv.matchTemplate(img, r_wholeL, cv.TM_CCOEFF_NORMED)

    QR = cv.matchTemplate(img, r_quarterRest, cv.TM_CCOEFF_NORMED)
    # cv.imshow("quarter rest scores", QR)
    # cv.waitKey(0)

    ER = cv.matchTemplate(img, r_eighthRest, cv.TM_CCOEFF_NORMED)

    SR = cv.matchTemplate(img, r_sixteenthRest, cv.TM_CCOEFF_NORMED)

    HR = cv.matchTemplate(img, r_halfRest, cv.TM_CCOEFF_NORMED)

    TC = cv.matchTemplate(img, r_tclef, cv.TM_CCOEFF_NORMED)

    # thresh =
    # 0.6
    fMatch = np.where(F >= 0.7)
    hMatch = np.where(H >= 0.5)
    # 0.7
    wMatch = np.where(W >= 0.65)
    # wMatchL = np.where(WL >= 0.7)
    # 0.58
    qrMatch = np.where(QR >= 0.55)
    erMatch = np.where(ER >= 0.65)
    srMatch = np.where(SR >= 0.65)
    hrMatch = np.where(HR >= 0.8)

    tcMatch = np.where(TC >= 0.5)

    fMatch = np.asarray(fMatch)
    hMatch = np.asarray(hMatch)
    wMatch = np.asarray(wMatch)
    # wMatchL = np.asarray(wMatchL)
    qrMatch = np.asarray(qrMatch)
    erMatch = np.asarray(erMatch)
    srMatch = np.asarray(srMatch)
    hrMatch = np.asarray(hrMatch)

    tcMatch = np.asarray(tcMatch)

    fMatch = remove_dupes(fMatch, width, height)
    hMatch = remove_dupes(hMatch, width, height)
    wMatch = remove_dupes(wMatch, width, height)
    # wMatchL = remove_dupes(wMatchL, width, height)
    qrMatch = remove_dupes(qrMatch, width, height)
    erMatch = remove_dupes(erMatch, width, height)
    srMatch = remove_dupes(srMatch, width, height)
    hrMatch = remove_dupes(hrMatch, width, height)

    tcMatch = remove_dupes(tcMatch, width, height)

    # removing quarter rests out of y-bounds
    qrMatch = np.transpose(qrMatch)
    qr_y_thresh = 5
    i = 0
    while i < len(qrMatch):
        if len(qrMatch) != 0:
            if abs(qrMatch[i, 0] + (r_quarterRest.shape[0] / 2) - staff.l3) > qr_y_thresh:
                qrMatch = np.delete(qrMatch, i, 0)
                print("deleted quarter rest out of y-bounds")
                i = i - 1
        i = i + 1
    qrMatch = np.transpose(qrMatch)

    box_img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)

    for i in range(len(fMatch[1])):
        cv.rectangle(box_img, (fMatch[1, i], fMatch[0, i]), (fMatch[1, i] + temp_x, fMatch[0, i] + temp_y), (0, 0, 255))

    for i in range(len(hMatch[1])):
        cv.rectangle(box_img, (hMatch[1, i], hMatch[0, i]), (hMatch[1, i] + temp_x, hMatch[0, i] + temp_y), (0, 255, 0))

    for i in range(len(wMatch[1])):
        cv.rectangle(box_img, (wMatch[1, i], wMatch[0, i]), (wMatch[1, i] + wwidth, wMatch[0, i] + temp_y), (255, 0, 0))

    # for i in range(len(wMatchL[1])):
    #     cv.rectangle(box_img, (wMatchL[1, i], wMatchL[0, i]), (wMatchL[1, i] + wwidth, wMatchL[0, i] + temp_y), (255, 0, 0))

    for i in range(len(qrMatch[1])):
        cv.rectangle(box_img, (qrMatch[1, i], qrMatch[0, i]),
                     (qrMatch[1, i] + r_quarterRest.shape[1], qrMatch[0, i] + r_quarterRest.shape[0]),
                     (0, 152, 255))  # orange

    for i in range(len(erMatch[1])):
        cv.rectangle(box_img, (erMatch[1, i], erMatch[0, i]), (erMatch[1, i] + temp_x, erMatch[0, i] + temp_y),
                     (255, 0, 255))  # pink

    for i in range(len(srMatch[1])):
        cv.rectangle(box_img, (srMatch[1, i], srMatch[0, i]), (srMatch[1, i] + temp_x, srMatch[0, i] + temp_y),
                     (255, 255, 0))  # turquoise

    for i in range(len(hrMatch[1])):
        cv.rectangle(box_img, (hrMatch[1, i], hrMatch[0, i]), (hrMatch[1, i] + temp_x, hrMatch[0, i] + temp_y),
                     (0, 255, 135))  # green turquoise

    for i in range(len(tcMatch[1])):
        cv.rectangle(box_img, (tcMatch[1, i], tcMatch[0, i]),
                     (tcMatch[1, i] + r_tclef.shape[1], tcMatch[0, i] + r_tclef.shape[0]), (128, 128, 128))  # gray

    cv.imshow("img boxed", box_img)
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
        new_note = utilities_cv.NoteClass(whole_dur, wMatch[1, i], wMatch[0, i])
        notes.append(new_note)

    # for i in range(len(wMatchL[1])):
    #     new_note = utilities_cv.NoteClass(whole_dur, wMatchL[1, i], wMatchL[0, i])
    #     notes.append(new_note)

    # Removing false quarter rests detected on note stems by comparing matches to notehead locations
    qrMatch = np.transpose(qrMatch)
    # print("pre process qrMatch: ", qrMatch)
    # while loops used here as to prevent indexing errors when iterating through matrix which is being reduced
    i = 0
    while i < len(qrMatch):
        for note in notes:
            if len(qrMatch) != 0:
                if abs(qrMatch[i, 1] - note.x_val) < width:
                    qrMatch = np.delete(qrMatch, i, 0)
                    i = i - 1
        i = i + 1

    # print("post process qrMatch: ", qrMatch)

    qrMatch = np.transpose(qrMatch)

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
        # MAKE THE Y VALUE NONE AFTER YOU FIGURE OUT IF IT'S A HALF OR WHOLE REST
        new_note = utilities_cv.NoteClass(half_dur, hrMatch[1, i], hrMatch[0, i])
        notes.append(new_note)

    # qrMatch = np.transpose(qrMatch)
    # # while loops used here as to prevent indexing errors when iterating through matrix which is being reduced
    # i = 0
    # while i < len(qrMatch[1]):
    #     for rest in qrMatch:
    #         print("half/whole rest", rest)
    #         for note in notes:
    #             if note.y_val is not None:
    #                 if abs(note.x_val - rest.x_val < width):
    #                     qrMatch = np.delete(rest)

    # print("qrMatch post process: ", qrMatch)

    notes.sort(key=operator.attrgetter('x_val'))

    d = staff.dis / 4

    h = height / 2
    hh = 0

    staff.l1 = staff.l1 - h
    staff.l2 = staff.l2 - h
    staff.l3 = staff.l3 - h
    staff.l4 = staff.l4 - h
    staff.l5 = staff.l5 - h

    # print("staff.l1", staff.l1)

    for note in notes:
        # print("note.y_val", note.y_val)
        if note.y_val is not None:
            # if staff.l1 - 5 * d <= note.y_val <= staff.l1 - 4 * d:
            #     note.orig_pitch = 84
            # if staff.l1 - 4 * d <= note.y_val <= staff.l1 - 3 * d:
            #     note.orig_pitch = 83
            # if staff.l1 - 3 * d <= note.y_val <= staff.l1 - 2 * d:
            #     note.orig_pitch = 81
            # if staff.l1 - 2 * d <= note.y_val <= staff.l1 - d:
            #     note.orig_pitch = 79
            # if staff.l1 - d <= note.y_val <= staff.l1 + d:
            #     note.orig_pitch = 77
            # if staff.l1 + d <= note.y_val <= staff.l2 - d:
            #     note.orig_pitch = 76
            # if staff.l2 - d <= note.y_val <= staff.l2 + d:
            #     note.orig_pitch = 74
            # if staff.l2 + d <= note.y_val <= staff.l3 - d:
            #     note.orig_pitch = 72
            # if staff.l3 - d <= note.y_val <= staff.l3 + d:
            #     note.orig_pitch = 71
            # if staff.l3 + d <= note.y_val <= staff.l4 - d:
            #     note.orig_pitch = 69
            # if staff.l4 - d <= note.y_val <= staff.l4 + d:
            #     note.orig_pitch = 67
            # if staff.l4 + d <= note.y_val <= staff.l5 - d:
            #     note.orig_pitch = 65
            # if staff.l5 - d <= note.y_val <= staff.l5 + d:
            #     note.orig_pitch = 64
            # if staff.l5 + d <= note.y_val <= staff.l5 + 3 * d:
            #     note.orig_pitch = 62
            # if staff.l5 + 3 * d <= note.y_val <= staff.l5 + 5 * d:
            #     note.orig_pitch = 60
            # if staff.l5 + 5 * d <= note.y_val <= staff.l5 + 7 * d:
            #     note.orig_pitch = 59
            # if staff.l5 + 7 * d <= note.y_val <= staff.l5 + 9 * d:
            #     note.orig_pitch = 57
            note.orig_pitch = getPitchValue(staff, note.y_val)

    # fix staff lines
    staff.l1 = staff.l1 + h
    staff.l2 = staff.l2 + h
    staff.l3 = staff.l3 + h
    staff.l4 = staff.l4 + h
    staff.l5 = staff.l5 + h

    for note in notes:
        if note.y_val is not None:
            # print("note.orig_pitch: ", note.orig_pitch)
            note.pitch = note.orig_pitch
            note.duration = note.orig_dur

    img_copy = img.copy()

    for note in notes:
        if note.y_val is not None:
            if note.orig_dur == quarter_dur:
                crop = img_copy[:, note.x_val - 1:note.x_val + width + staff.dis]
                y_range = range(note.y_val, note.y_val + height)
                x_range = range(note.x_val - 1, note.x_val + width + staff.dis)
                for i in y_range:
                    crop[i] = 255
                # cv.imshow("flag crop", crop)
                # cv.waitKey(0)
                F8U = cv.matchTemplate(crop, r_flag8u, cv.TM_CCOEFF_NORMED)
                F8D = cv.matchTemplate(crop, r_flag8d, cv.TM_CCOEFF_NORMED)
                F16U = cv.matchTemplate(crop, r_flag16u, cv.TM_CCOEFF_NORMED)
                F16D = cv.matchTemplate(crop, r_flag16d, cv.TM_CCOEFF_NORMED)

                flagThresh = 0.6
                f8uMatch = np.where(F8U >= flagThresh)
                f8dMatch = np.where(F8D >= flagThresh)
                f16uMatch = np.where(F16U >= flagThresh)
                f16dMatch = np.where(F16D >= flagThresh)

                f8uMatch = np.asarray(f8uMatch)
                f8dMatch = np.asarray(f8dMatch)
                f16uMatch = np.asarray(f16uMatch)
                f16dMatch = np.asarray(f16dMatch)

                if f8uMatch.shape[1] != 0:
                    note.duration = note.orig_dur / 2
                    print("found 8th flag, up")

                if f8dMatch.shape[1] != 0:
                    note.duration = note.orig_dur / 2
                    print("found 8th flag, down")

                if f16uMatch.shape[1] != 0:
                    note.duration = note.orig_dur / 4
                    print("found 16th flag, up")

                if f16dMatch.shape[1] != 0:
                    note.duration = note.orig_dur / 4
                    print("found 16th flag, down")

    LCropDist = 2 * staff.dis
    RCropDist = 3 * staff.dis
    TCropDist = 0
    BCropDist = staff.dis

    for note in notes:
        print('note.orig_pitch: ', note.orig_pitch)

    img_copy2 = img.copy()

    for note in notes:
        if note.y_val is not None:
            crop = img_copy2[round(note.y_val - d):round(note.y_val + 5 * d),
                   round(note.x_val + width + d):round(note.x_val + width + 4 * d)]
            DOT = cv.matchTemplate(crop, r_dot, cv.TM_CCOEFF_NORMED)
            dotMatch = np.where(DOT >= 0.7)
            dotMatch = np.asarray(dotMatch)
            if dotMatch.shape[1] != 0:
                print("dotted note found")
                note.duration = note.orig_dur * 1.5

    clefWidth = r_tclef.shape[1]
    clefStart = tcMatch[1][0]
    print('clefWidth: ', clefWidth)
    print('clefStart: ', clefStart)
    if staff.staff_number == 1:
        keyFlats = []
        keySharps = []
        crop = img[:, round(clefStart + clefWidth):round(clefStart + 3 * clefWidth)]
        if notes[0].x_val - 1.5 * width < clefStart + 3 * clefWidth:
            crop = img[:, clefStart + clefWidth:round(notes[0].x_val - 1.5 * width)]

        FL = cv.matchTemplate(crop, r_flat, cv.TM_CCOEFF_NORMED)
        SH = cv.matchTemplate(crop, r_sharp, cv.TM_CCOEFF_NORMED)
        kFlatMatch = np.where(FL >= 0.65)
        kSharpMatch = np.where(SH >= 0.65)
        kFlatMatch = np.asarray(kFlatMatch)
        kSharpMatch = np.asarray(kSharpMatch)
        kFlatMatch = remove_dupes(kFlatMatch, r_flat.shape[1] / 2, r_flat.shape[0] / 2)
        kSharpMatch = remove_dupes(kSharpMatch, r_sharp.shape[1] / 2, r_sharp.shape[0] / 2)
        # print('kFlatMatch: ', kFlatMatch)
        # print('kSharpMatch: ', kSharpMatch)
        for i in range(len(kFlatMatch[1])):
            cv.rectangle(crop, (kFlatMatch[1, i], kFlatMatch[0, i]),
                         (kFlatMatch[1, i] + r_flat.shape[1], kFlatMatch[0, i] + r_flat.shape[0]), (0, 0, 0))  # gray
            flat_loc = kFlatMatch[0, i] + r_flat.shape[0] * 3 / 4
            # print('loc: ', flat_loc)
            # print('midline: ', staff.l3)
            universalFlat = getPitchValue(staff, flat_loc)
            print('universalFlat: ', universalFlat)
            keyFlats.append(universalFlat)
        for i in range(len(kSharpMatch[1])):
            cv.rectangle(crop, (kSharpMatch[1, i], kSharpMatch[0, i]),
                         (kSharpMatch[1, i] + r_sharp.shape[1], kSharpMatch[0, i] + r_sharp.shape[0]), (156, 156, 156))
            sharp_loc = kSharpMatch[0, i] + r_sharp.shape[0] / 2
            print('sharp_loc: ', sharp_loc)
            print('line 1: ', staff.l1)
            universalSharp = getPitchValue(staff, sharp_loc)
            print('universalSharp: ', universalSharp)
            keySharps.append(universalSharp)

    for note in notes:
        if len(keyFlats) != 0:
            for flat in keyFlats:
                if note.pitch == flat:
                    note.pitch = note.pitch - 1
                    note.accidental = 'flat'
        if len(keySharps) != 0:
            for sharp in keySharps:
                if note.pitch == sharp:
                    note.pitch = note.pitch + 1
                    note.accidental = 'sharp'

    accidentalsImgCopy = img.copy()

    # print('natural.shape: ', r_natural.shape)
    # print('flat.shape: ', r_flat.shape)
    # print('sharp.shape: ', r_sharp.shape)
    # cv.imshow('r_natural', r_natural)
    # cv.waitKey(0)
    # cv.imshow('r_flat', r_flat)
    # cv.waitKey(0)
    # cv.imshow('r_sharp', r_sharp)
    # cv.waitKey(0)

    for note in notes:
        if note.y_val is not None:
            crop = accidentalsImgCopy[round(note.y_val - 1.5 * height):round(note.y_val + 1.5 * height),
                   round(note.x_val - 2 * staff.dis):round(note.x_val)]
            # cv.imshow('accidentalsCrop', crop)
            # cv.waitKey(0)
            AF = cv.matchTemplate(crop, r_flat, cv.TM_CCOEFF_NORMED)
            AS = cv.matchTemplate(crop, r_sharp, cv.TM_CCOEFF_NORMED)
            AN = cv.matchTemplate(crop, r_natural, cv.TM_CCOEFF_NORMED)
            aFlatMatch = np.where(AF >= 0.65)
            aSharpMatch = np.where(AS >= 0.65)
            aNaturalMatch = np.where(AN >= 0.75)
            aFlatMatch = np.asarray(aFlatMatch)
            aSharpMatch = np.asarray(aSharpMatch)
            aNaturalMatch = np.asarray(aNaturalMatch)
            if aFlatMatch.shape[1] != 0:
                print('accidental flat')
                note.pitch = note.pitch - 1
                note.accidental = 'flat'
            if aSharpMatch.shape[1] != 0:
                print('accidental sharp')
                note.pitch = note.pitch + 1
                note.accidental = 'sharp'
            if aNaturalMatch.shape[1] != 0:
                print('accidental natural')
                if note.accidental == 'sharp':
                    note.pitch = note.pitch - 1
                    note.accidental = 'natural'
                if note.accidental == 'flat':
                    note.pitch = note.pitch + 1
                    note.accidental = 'natural'

    staff.notes = []
    staff.notes = notes

    return staff, img, height, width, keyFlats, keySharps


def main():
    imageout = noteDetect()
    return imageout


if __name__ == "__main__":
    main()
