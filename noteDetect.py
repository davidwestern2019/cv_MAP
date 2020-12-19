import cv2 as cv
import numpy as np
import utilities_cv
import operator


# # used to get (x, y) locations from mouse click for troubleshooting
# def get_xy(event, x, y, flags, param):
#     if event == cv.EVENT_LBUTTONDOWN:
#         print(x, y)
#         param.append((x, y))
#     return param


# find staff line midpoints by averaging their top and bottom row of black pixels from 'line_locations'
def lineLoc(i, staff):
    lx = (staff.line_locations[i][0] + staff.line_locations[i][1]) / 2
    return lx


# crop the staffless image into sections as defined by each staff
def staffCrop(staff, image):
    # define midpoint of each staff line
    staff.l1 = lineLoc(0, staff)
    staff.l2 = lineLoc(1, staff)
    staff.l3 = lineLoc(2, staff)
    staff.l4 = lineLoc(3, staff)
    staff.l5 = lineLoc(4, staff)
    # define the average number of pixels between the midpoint of each staff line
    staff.line_dis = (staff.l5 - staff.l1) / 4

    # each staff crop needs to leave ample space above and below to detect features
    # check to make sure the standard staff crop doesn't go higher than the start of a page
    if staff.staff_start - 6 * staff.line_dis < 0:
        # if so, crop the top end to the start of the page
        img = image[0:round(staff.staff_end + 6 * staff.line_dis), :]
    # check to make sure the standard staff crop doesn't go lower than the end of a page
    elif staff.staff_end + 6 * staff.line_dis > image.shape[0]:
        # if so, crop to the end of the page
        img = image[round(staff.staff_start - 6 * staff.line_dis):round(image.shape[0]), :]
        # redefine staff line locations relative to the location of the staff crop
        start = staff.staff_start - 6 * staff.line_dis
        staff.l1 = staff.l1 - start
        staff.l2 = staff.l2 - start
        staff.l3 = staff.l3 - start
        staff.l4 = staff.l4 - start
        staff.l5 = staff.l5 - start

    else:
        # staff can be cropped to one staff height above and below the staff location
        img = image[round(staff.staff_start - 6 * staff.line_dis):round(staff.staff_end + 6 * staff.line_dis), :]
        # redefine staff line locations relative to the location of the staff crop
        start = staff.staff_start - 6 * staff.line_dis
        staff.l1 = staff.l1 - start
        staff.l2 = staff.l2 - start
        staff.l3 = staff.l3 - start
        staff.l4 = staff.l4 - start
        staff.l5 = staff.l5 - start

    return img


# resize templates to fit images based on staff size
def resizeTemplate(scale, template):
    width = int(template.shape[1] * scale)
    height = int(template.shape[0] * scale)
    dim = (width, height)
    scaleTemplate = cv.resize(template, dim, interpolation=cv.INTER_AREA)
    return scaleTemplate


# remove duplicate template matches within a given space
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


# find and remove measure lines, save x-location as staff attribute
def findMeasure(img, r_measure_line, staff, notes, width):
    measureCopy = img.copy()
    # template matching to find measure lines
    ML = cv.matchTemplate(measureCopy, r_measure_line, cv.TM_CCOEFF_NORMED)
    lineMatch = np.where(ML >= 0.6)
    lineMatch = np.asarray(lineMatch)
    # delete measure lines that don't line up with staff
    # while loop to make sure each line natch is checked
    i = 0
    while i < len(lineMatch[1]):
        # measure line should begin very near to top staff line
        if staff.l1 - staff.dis > lineMatch[0, i] > staff.l1 + staff.dis:
            np.delete(lineMatch, i, 1)
            # iterate backwards after deletion to check every line match
            i = i - 1
        i = i + 1

    # remove duplicate matches that can occur within the same small area
    lineMatch = remove_dupes(lineMatch, r_measure_line.shape[1] * 3, r_measure_line.shape[0])

    # # code for visually checking measure lines
    # measureCopy = cv.cvtColor(measureCopy, cv.COLOR_GRAY2BGR)
    # numLines = len(lineMatch[1])
    # for i in range(numLines):
    #     cv.rectangle(measureCopy, (lineMatch[1, i], lineMatch[0, i]),
    #                  (lineMatch[1, i] + r_measure_line.shape[1], lineMatch[0, i] + r_measure_line.shape[0]),
    #                  (0, 0, 256), -1)  # red
    # cv.imshow("boxed lines", measureCopy)
    # cv.waitKey(0)

    # delete false measure lines detected in note stems
    for note in notes:
        i = 0
        while i < len(lineMatch[1]):
            # delete any line match that occurs in the immediate x-vicinity of a notehead
            if note.x_val - staff.dis / 2 < lineMatch[1, i] < note.x_val + width + staff.dis / 2:
                lineMatch = np.delete(lineMatch, i, 1)
                i = i - 1
            i = i + 1

    # white out measure lines to reduce template matching errors
    numLines = len(lineMatch[1])
    for i in range(numLines):
        cv.rectangle(img, (lineMatch[1, i] - r_measure_line.shape[1], lineMatch[0, i]),
                     (lineMatch[1, i] + r_measure_line.shape[1], lineMatch[0, i] + r_measure_line.shape[0]),
                     (255, 255, 255), -1)  # white, filled

    # save measure line x-locations as a staff attribute
    staff.measure_lines = lineMatch[1]
    staff.measure_lines.sort()

    # # show image with measure lines removed for troubleshooting
    # cv.imshow("measure lines removed", img)
    # cv.waitKey(0)

    # return image with measure lines removed
    return img


# get the MIDI number pitch of a notehead or sharp/flat
def getPitchValue(staff, y_val):
    # define 'd' as 1/4 the space between each line
    d = (staff.l5 - staff.l1) / 16
    # initialize pitch for function
    pitch = None
    # quantize notehead (or key signature sharp/flat) to their general location on the staff to define pitch
    if staff.l1 - 9 * d <= y_val <= staff.l1 - 7 * d:
        pitch = 84
    if staff.l1 - 7 * d <= y_val <= staff.l1 - 5 * d:
        pitch = 83
    if staff.l1 - 5 * d <= y_val <= staff.l1 - 3 * d:
        pitch = 81
    if staff.l1 - 3 * d <= y_val <= staff.l1 - d:
        pitch = 79
    if staff.l1 - d <= y_val <= staff.l1 + d:
        pitch = 77
    if staff.l1 + d <= y_val <= staff.l2 - d:
        pitch = 76
    if staff.l2 - d <= y_val <= staff.l2 + d:
        pitch = 74
    if staff.l2 + d <= y_val <= staff.l3 - d:
        pitch = 72
    if staff.l3 - d <= y_val <= staff.l3 + d:
        pitch = 71
    if staff.l3 + d <= y_val <= staff.l4 - d:
        pitch = 69
    if staff.l4 - d <= y_val <= staff.l4 + d:
        pitch = 67
    if staff.l4 + d <= y_val <= staff.l5 - d:
        pitch = 65
    if staff.l5 - d <= y_val <= staff.l5 + d:
        pitch = 64
    if staff.l5 + d <= y_val <= staff.l5 + 3 * d:
        pitch = 62
    if staff.l5 + 3 * d <= y_val <= staff.l5 + 5 * d:
        pitch = 60
    if staff.l5 + 5 * d <= y_val <= staff.l5 + 7 * d:
        pitch = 59
    if staff.l5 + 7 * d <= y_val <= staff.l5 + 9 * d:
        pitch = 57

    return pitch


def noteDetect(staff, img, keyFlats, keySharps):
    print("Running noteDetect...")

# # READ TEMPLATE IMAGES FROM FILE AS GREYSCALE IMAGES # # -------------------------------------------------------------
    # noteheads
    filledTemplate = cv.imread('filled_head.png', cv.IMREAD_GRAYSCALE)
    halfTemplate = cv.imread('half_head.png', cv.IMREAD_GRAYSCALE)
    wholeTemplate = cv.imread('whole_head.png', cv.IMREAD_GRAYSCALE)
    # flags for eights notes
    flag8d = cv.imread('f8thD.png', cv.IMREAD_GRAYSCALE)
    flag8u = cv.imread('f8thU.png', cv.IMREAD_GRAYSCALE)
    # rests
    eighthRestTemplate = cv.imread('eighth_rest.png', cv.IMREAD_GRAYSCALE)
    quarterRestTemplate = cv.imread('quarter_rest.png', cv.IMREAD_GRAYSCALE)
    halfRestTemplate = cv.imread('half_rest2.png', cv.IMREAD_GRAYSCALE)
    # sharps, flats, and naturals
    sharpTemplate = cv.imread('sharp.png', cv.IMREAD_GRAYSCALE)
    flatTemplate = cv.imread('flat.png', cv.IMREAD_GRAYSCALE)
    naturalTemplate = cv.imread('natural.png', cv.IMREAD_GRAYSCALE)
    # dot
    dotTemplate = cv.imread('dot2.png', cv.IMREAD_GRAYSCALE)
    # treble clef
    tClefTemplate = cv.imread('treble_clef.png', cv.IMREAD_GRAYSCALE)

# # INITIAL TEMPLATE SCALING # # ---------------------------------------------------------------------------------------
    # define variable for scaling templates based on staff line spacing
    scale = (staff.line_dis / filledTemplate.shape[0]) * 1.3

    # define width and height as the correctly scaled sizing of filled notehead template
    width = int(filledTemplate.shape[1] * scale)
    height = int(filledTemplate.shape[0] * scale)
    dim = (width, height)
    # sizing for whole notes
    wwidth = int(wholeTemplate.shape[1] * scale)
    wdim = (wwidth, height)

    # resize notehead templates
    r_filled = cv.resize(filledTemplate, dim, interpolation=cv.INTER_AREA)
    r_half = cv.resize(halfTemplate, dim, interpolation=cv.INTER_AREA)
    r_whole = cv.resize(wholeTemplate, wdim, interpolation=cv.INTER_AREA)

# # RESIZE ALL TEMPLATES WITH CUSTOM SCALING FOR OPTIMUM FUNCTIONALITY # # ---------------------------------------------
    # noteheads
    r_filled = resizeTemplate(.9, r_filled)
    r_half = resizeTemplate(.9, r_half)
    r_whole = resizeTemplate(.9, r_whole)
    # rests
    r_eighthRest = resizeTemplate(scale, eighthRestTemplate)
    r_quarterRest = resizeTemplate(scale, quarterRestTemplate)
    r_halfRest = resizeTemplate(scale * 1.1 * 432 / 452, halfRestTemplate)
    # flags for eighth notes
    r_flag8u = resizeTemplate(scale, flag8u)
    r_flag8d = resizeTemplate(scale, flag8d)
    # sharps, flats, and naturals
    r_sharp = resizeTemplate(scale * 1.25, sharpTemplate)
    r_flat = resizeTemplate(scale * 0.9, flatTemplate)
    r_natural = resizeTemplate(scale * 1, naturalTemplate)
    # dot
    r_dot = resizeTemplate(scale * 15 / 16, dotTemplate)
    # treble clef
    r_tclef = resizeTemplate(scale * 2.3, tClefTemplate)

    # morph quarter rest template to better match common rests used in different music fonts
    k = np.ones((1, 2), np.uint8)
    r_quarterRest = cv.morphologyEx(r_quarterRest, cv.MORPH_CLOSE, k)

    # manually create template for measure line based on staff parameters
    # create image size
    y_range = staff.line_dis * 5 - staff.dis + 8
    x_range = (staff.line_dis * 5 - staff.dis) * 0.03
    y_range = round(y_range)
    x_range = round(x_range)
    # create white image
    measureLineImg = np.ones((y_range, x_range), dtype=np.uint8) * 255
    # make pixels black, except 4 rows of vertical pixels on top and bottom
    # this helps the template to pick up vertical lines of the correct length
    for i in range(0, y_range):
        for j in range(0, x_range):
            if 3 < i < y_range - 4:
                measureLineImg[i][j] = 0
    # set as measure line template
    r_measureLine = measureLineImg

# # TEMPLATE MATCHING # # ----------------------------------------------------------------------------------------------
    # noteheads
    F = cv.matchTemplate(img, r_filled, cv.TM_CCOEFF_NORMED)
    H = cv.matchTemplate(img, r_half, cv.TM_CCOEFF_NORMED)
    W = cv.matchTemplate(img, r_whole, cv.TM_CCOEFF_NORMED)
    # rests
    ER = cv.matchTemplate(img, r_eighthRest, cv.TM_CCOEFF_NORMED)
    QR = cv.matchTemplate(img, r_quarterRest, cv.TM_CCOEFF_NORMED)
    HR = cv.matchTemplate(img, r_halfRest, cv.TM_CCOEFF_NORMED)
    # treble clef
    TC = cv.matchTemplate(img, r_tclef, cv.TM_CCOEFF_NORMED)

# # RETRIEVE MATCHES ABOVE CUSTOM THRESHOLD # # ------------------------------------------------------------------------
    # noteheads
    fMatch = np.where(F >= 0.69)
    hMatch = np.where(H >= 0.5)
    wMatch = np.where(W >= 0.65)
    # rests
    erMatch = np.where(ER >= 0.65)
    qrMatch = np.where(QR >= 0.55)
    hrMatch = np.where(HR >= 0.6)
    # treble clef
    tcMatch = np.where(TC >= 0.4)

# # CHANGE MATCHES TO ARRAY # # ----------------------------------------------------------------------------------------
    # noteheads
    fMatch = np.asarray(fMatch)
    hMatch = np.asarray(hMatch)
    wMatch = np.asarray(wMatch)
    # rests
    erMatch = np.asarray(erMatch)
    qrMatch = np.asarray(qrMatch)
    hrMatch = np.asarray(hrMatch)
    # treble clef
    tcMatch = np.asarray(tcMatch)

# # USE FUNCTION TO REMOVE MULTIPLE ERRONEOUS NEARBY MATCHES # # -------------------------------------------------------
    # noteheads
    fMatch = remove_dupes(fMatch, width, height)
    hMatch = remove_dupes(hMatch, width, height)
    wMatch = remove_dupes(wMatch, width, height)
    # rests
    erMatch = remove_dupes(erMatch, width, height)
    qrMatch = remove_dupes(qrMatch, width, height)
    hrMatch = remove_dupes(hrMatch, width, height)
    # treble clef
    tcMatch = remove_dupes(tcMatch, width, height)
    clefWidth = r_tclef.shape[1]
    clefStart = tcMatch[1][0]

    # remove quarter rest matches that aren't centered vertically on the staff
    qrMatch = np.transpose(qrMatch)
    qr_y_thresh = 5
    i = 0
    while i < len(qrMatch):
        if len(qrMatch) != 0:
            if abs(qrMatch[i, 0] + (r_quarterRest.shape[0] / 2) - staff.l3) > qr_y_thresh:
                qrMatch = np.delete(qrMatch, i, 0)
                i = i - 1
        i = i + 1
    qrMatch = np.transpose(qrMatch)

# # CREATE IMAGE WITH COLOR CODED BOXED TEMPLATE MATCHES FOR TESTING # # -----------------------------------------------
    # create separate color image
    box_img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    # noteheads
    for i in range(len(fMatch[1])):
        cv.rectangle(box_img, (fMatch[1, i], fMatch[0, i]), (fMatch[1, i] + width, fMatch[0, i] + height),
                     (0, 0, 255))  # red

    for i in range(len(hMatch[1])):
        cv.rectangle(box_img, (hMatch[1, i], hMatch[0, i]), (hMatch[1, i] + width, hMatch[0, i] + height),
                     (0, 255, 0))  # green

    for i in range(len(wMatch[1])):
        cv.rectangle(box_img, (wMatch[1, i], wMatch[0, i]), (wMatch[1, i] + wwidth, wMatch[0, i] + height),
                     (255, 0, 0))  # blue
    # rests
    for i in range(len(erMatch[1])):
        cv.rectangle(box_img, (erMatch[1, i], erMatch[0, i]),
                     (erMatch[1, i] + r_eighthRest.shape[1], erMatch[0, i] + r_eighthRest.shape[0]),
                     (255, 0, 255))  # pink
    for i in range(len(qrMatch[1])):
        cv.rectangle(box_img, (qrMatch[1, i], qrMatch[0, i]),
                     (qrMatch[1, i] + r_quarterRest.shape[1], qrMatch[0, i] + r_quarterRest.shape[0]),
                     (0, 152, 255))  # orange
    # treble clef
    for i in range(len(tcMatch[1])):
        cv.rectangle(box_img, (tcMatch[1, i], tcMatch[0, i]),
                     (tcMatch[1, i] + r_tclef.shape[1], tcMatch[0, i] + r_tclef.shape[0]),
                     (128, 128, 128))  # gray

    # # show image with colored boxes to manually check matches
    # cv.imshow("img boxed", box_img)
    # cv.waitKey(0)

# # ADD MATCHES AS NOTES CLASS OBJECTS WITH ATTRIBUTES, AND APPEND TO NOTES ARRAY # # ----------------------------------
    # create empty array for notes objects to be stored
    notes = []

    # set relative durations
    quarter_dur = 1
    half_dur = 2 * quarter_dur
    whole_dur = 4 * quarter_dur
    eighth_dur = quarter_dur / 2

    # noteheads
    for i in range(len(fMatch[1])):
        new_note = utilities_cv.NoteClass(quarter_dur, fMatch[1, i], fMatch[0, i])
        notes.append(new_note)

    for i in range(len(hMatch[1])):
        new_note = utilities_cv.NoteClass(half_dur, hMatch[1, i], hMatch[0, i])
        notes.append(new_note)

    for i in range(len(wMatch[1])):
        new_note = utilities_cv.NoteClass(whole_dur, wMatch[1, i], wMatch[0, i])
        notes.append(new_note)

    # rests
    # (y_values are set as 'None' in class attributes to make rests easier to decipher from notes in notes list)
    for i in range(len(erMatch[1])):
        new_note = utilities_cv.NoteClass(eighth_dur, erMatch[1, i], None)
        notes.append(new_note)

    # remove false quarter rests detected on note stems
    qrMatch = np.transpose(qrMatch)
    # while loops used here as to prevent indexing errors when iterating through matrix which is being reduced
    i = 0
    while i < len(qrMatch):
        for note in notes:
            if len(qrMatch) != 0:
                if abs(qrMatch[i, 1] - note.x_val) < width * 0.8:
                    # delete quarter rest match if it is within a given horizontal distance from a located notehead
                    qrMatch = np.delete(qrMatch, i, 0)
                    # label any removed quarter rests on box_img
                    cv.putText(box_img, "-qr-", (qrMatch[i, 1], qrMatch[i, 0]), cv.FONT_HERSHEY_SIMPLEX, 1,
                               (128, 128, 128))  # grey
                    # iterate backwards by one if an item is removed
                    i = i - 1
        i = i + 1
    qrMatch = np.transpose(qrMatch)
    # add true quarter rest matches as class objects to notes array
    for i in range(len(qrMatch[1])):
        new_note = utilities_cv.NoteClass(quarter_dur, qrMatch[1, i], None)
        notes.append(new_note)

    # skip false half/whole rests matches, and classify whether matches are half or whole rests based on y-location
    for i in range(len(hrMatch[1])):
        # add potential match as object
        new_note = utilities_cv.NoteClass(half_dur, hrMatch[1, i], hrMatch[0, i])
        skip = False
        # remove false half/whole rest match detected on beams above/below noteheads
        for note in notes:
            if note.x_val - staff.line_dis < new_note.x_val < note.x_val + width:
                # skip match if within a given x-distance from detected notehead
                skip = True
        # determine if is whole rest
        if staff.l2 - staff.line_dis / 5 <= new_note.y_val <= staff.l2 + staff.line_dis / 6:
            # if rest is just below staff line 2 in expected location, add as whole rest
            if not skip:
                new_note.y_val = None
                new_note.orig_dur = whole_dur
                # add whole rest to notes list
                notes.append(new_note)
                # add text to box_img to notate matched whole rests
                cv.putText(box_img, "whole", (hrMatch[1, i], hrMatch[0, i]), cv.FONT_HERSHEY_SIMPLEX, 1,
                           (128, 128, 128))  # grey
        elif staff.l2 + staff.line_dis * 1 / 6 <= new_note.y_val <= staff.l3 - staff.line_dis / 4:
            # if rest is above staff line 2 in expected location, add as half rest
            if not skip:
                new_note.y_val = None
                # add half rest to notes list
                notes.append(new_note)
                # add text to box_img to notate matches half rests
                cv.putText(box_img, "half", (hrMatch[1, i], hrMatch[0, i]), cv.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128))
        # if half/whole rest match is not within y-bounds to be half or whole rest, it is not appended to the notes list

    # sort notes array by x-value to get notes and rests into correct order
    notes.sort(key=operator.attrgetter('x_val'))


# # GET PITCH OF NOTES # # ---------------------------------------------------------------------------------------------
    # temporarily shift stored staff line location values to account for the height of noteheads
    # this makes it easier to match the notehead y-location to its attributed pitch
    # because the template matches have stored x and y-values at the top left corner of the match, not the center
    h = height / 2
    staff.l1 = staff.l1 - h
    staff.l2 = staff.l2 - h
    staff.l3 = staff.l3 - h
    staff.l4 = staff.l4 - h
    staff.l5 = staff.l5 - h

    # get pitch using function, adjusted staff line locations, and y-values of notehead matches
    for note in notes:
        # (exclude rests, which have a 'y_val' of 'None'
        if note.y_val is not None:
            note.orig_pitch = getPitchValue(staff, note.y_val)

    # fix staff line location values back to represent their actual location
    staff.l1 = staff.l1 + h
    staff.l2 = staff.l2 + h
    staff.l3 = staff.l3 + h
    staff.l4 = staff.l4 + h
    staff.l5 = staff.l5 + h

    # assign original pitch and duration values to actual pitch and duration values before making adjustments
    # this ensures all notes and rests have values in 'notes.pitch' and 'notes.duration'
    # and allows changes to be made to the final values without losing the data that was originally detected
    for note in notes:
        if note.y_val is not None:
            note.pitch = note.orig_pitch
            note.duration = note.orig_dur


# # DETECT EIGHTH NOTE FLAGS # # ---------------------------------------------------------------------------------------
    # create image copy used for detecting flags
    flag_copy = img.copy()
    # use statements to narrow search to filled notes (the only type with flags)
    for note in notes:
        if note.y_val is not None:
            if note.orig_dur == quarter_dur:
                # create bounds for making a crop for each relevant note
                y_min = note.y_val - round(r_flag8d.shape[0]) - round(staff.line_dis / 2)
                y_max = note.y_val + round(height + r_flag8d.shape[0] + staff.line_dis)
                x_min = round(note.x_val - 1)
                x_max = round(note.x_val + width + staff.line_dis)
                # cropped image contains the note and space above and below where a flag may be
                crop = flag_copy[y_min:y_max, x_min:x_max]
                # set bounds that cover only the notehead
                y_range = range(round(note.y_val), round(note.y_val + height))
                x_range = range(round(note.x_val - 1), round(note.x_val + width + staff.line_dis))
                # white out the notehead, which can cause false matches
                for i in y_range:
                    for j in x_range:
                        flag_copy[i][j] = 255
                # match templates for upward, and downward facing eighth note flags
                F8U = cv.matchTemplate(crop, r_flag8u, cv.TM_CCOEFF_NORMED)
                F8D = cv.matchTemplate(crop, r_flag8d, cv.TM_CCOEFF_NORMED)
                # get matches above given threshold
                flagThresh = 0.6
                f8uMatch = np.where(F8U >= flagThresh)
                f8dMatch = np.where(F8D >= flagThresh)
                # change to array
                f8uMatch = np.asarray(f8uMatch)
                f8dMatch = np.asarray(f8dMatch)
                # if a match is found, change the duration to reflect, and write on box_img to notate
                if f8uMatch.shape[1] != 0:
                    note.duration = note.orig_dur / 2
                    cv.putText(box_img, "8th", (note.x_val, note.y_val), cv.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128))
                if f8dMatch.shape[1] != 0:
                    note.duration = note.orig_dur / 2
                    cv.putText(box_img, "8th", (note.x_val, note.y_val), cv.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128))


# # DETECT DOTTED NOTES # # ------------------------------------------------------------------------------------
    # create image copy used for detecting dotted notes
    dot_copy = img.copy()

    # white out eighth rests from dot_copy (they commonly cause false dot detections)
    for i in range(len(erMatch[1])):
        cv.rectangle(dot_copy, (erMatch[1, i], erMatch[0, i]),
                     (erMatch[1, i] + r_eighthRest.shape[1], erMatch[0, i] + r_eighthRest.shape[0]),
                     (255, 255, 255), -1)  # red

    # define 'd' as 1/4 the distance between the midpoint of subsequent staff lines
    # used for creating precise image crop
    d = staff.line_dis / 4

    # look at all notes (not rests)
    for note in notes:
        if note.y_val is not None:
            # create cropped image for each note, looking just to the right and slightly above (where dots are located)
            crop = dot_copy[round(note.y_val - d):round(note.y_val + 5 * d),
                            round(note.x_val + width):round(note.x_val + width + 4 * d)]
            if note.orig_dur == whole_dur:
                # whole notes crop: accounts for larger width of whole notes
                crop = dot_copy[round(note.y_val - d):round(note.y_val + 5 * d),
                                round(note.x_val + r_whole.shape[1]):round(note.x_val + r_whole.shape[1] + 4 * d)]
            # match dot template in each crop
            DOT = cv.matchTemplate(crop, r_dot, cv.TM_CCOEFF_NORMED)
            # get matches over threshold
            dotMatch = np.where(DOT >= 0.65)
            # change to array
            dotMatch = np.asarray(dotMatch)
            # if dot detected, change note duration, and add text on box_img to notate
            if dotMatch.shape[1] != 0:
                cv.putText(box_img, "dot", (note.x_val, note.y_val), cv.FONT_HERSHEY_SIMPLEX, 1, (126, 126, 126))
                note.duration = note.orig_dur * 1.5


# # DETECT KEY SIGNATURE # # -------------------------------------------------------------------------------------------
    # only search for key signature in first staff
    if staff.staff_number == 1:
        # initialize blank sharps and flats lists
        keyFlats = []
        keySharps = []
        # set y-bounds for a cropped image to look for sharps and flats
        # prevents tempo and other text from being falsely detected as containing sharps or flats
        max_height = staff.l1 - r_flat.shape[0] * 3 / 4
        max_height = round(max_height)
        min_height = staff.l5
        min_height = round(min_height)
        # check if the first note is far enough from the staff to avoid picking up an accidental instead of key sig.
        if notes[0].x_val - 1.5 * width >= clefStart + 3 * clefWidth:
            # create cropped image with wider scope (to detect potentially more objects in the key signature)
            crop = img[max_height:min_height, round(clefStart + clefWidth):round(clefStart + 3 * clefWidth)]
        if notes[0].x_val - 1.5 * width < clefStart + 3 * clefWidth:
            # if first note is too close for wider search...
            if round(notes[0].x_val) - round(1.5 * width) - clefStart - clefWidth < round(r_sharp.shape[1]):
                # if first note is too close, create minimum cropped image
                crop = img[max_height:min_height,
                           clefStart + clefWidth:round(clefStart + clefWidth + r_sharp.shape[1]) + 1]
            else:
                # otherwise, crop up to just before the first note
                crop = img[max_height:min_height, clefStart + clefWidth:round(notes[0].x_val) - round(1.5 * width)]

        # template match in the cropped image for sharps and flats
        FL = cv.matchTemplate(crop, r_flat, cv.TM_CCOEFF_NORMED)
        SH = cv.matchTemplate(crop, r_sharp, cv.TM_CCOEFF_NORMED)
        # find matches above given threshold
        key_thresh = 0.55
        kFlatMatch = np.where(FL >= key_thresh)
        kSharpMatch = np.where(SH >= key_thresh)
        # change to array
        kFlatMatch = np.asarray(kFlatMatch)
        kSharpMatch = np.asarray(kSharpMatch)
        # use function to remove possible duplicate matches
        # (allows for some objects closer than usual as key signature can have slightly overlapping sharps and flats)
        kFlatMatch = remove_dupes(kFlatMatch, r_flat.shape[1] / 2, r_flat.shape[0] / 2)
        kSharpMatch = remove_dupes(kSharpMatch, r_sharp.shape[1] / 2, r_sharp.shape[0] / 2)

        # process detected flats
        for i in range(len(kFlatMatch[1])):
            # box detected flats for troubleshooting
            cv.rectangle(crop, (kFlatMatch[1, i], kFlatMatch[0, i]),
                         (kFlatMatch[1, i] + r_flat.shape[1], kFlatMatch[0, i] + r_flat.shape[0]),
                         (0, 0, 0)) # black
            # adjust 'flat_loc' to account for the height of the template
            flat_loc = kFlatMatch[0, i] + r_flat.shape[0] * 3 / 4 + max_height
            # find the correlating natural MIDI pitch
            universalFlat = getPitchValue(staff, flat_loc)
            print('Key signature Flat: ', universalFlat)
            # include the found flat, and the values for one octave up and down, as universal flats for the key
            keyFlats.append(universalFlat)
            keyFlats.append(universalFlat + 12)
            keyFlats.append(universalFlat - 12)
        # process detected sharps
        for i in range(len(kSharpMatch[1])):
            # box detected sharps for troubleshooting
            cv.rectangle(crop, (kSharpMatch[1, i], kSharpMatch[0, i]),
                         (kSharpMatch[1, i] + r_sharp.shape[1], kSharpMatch[0, i] + r_sharp.shape[0]),
                         (156, 156, 156)) # grey
            # adjust 'sharp_loc' to account for the height of the template
            sharp_loc = kSharpMatch[0, i] + r_sharp.shape[0] / 2 + max_height
            # find the correlating natural MIDI pitch
            universalSharp = getPitchValue(staff, sharp_loc)
            print('Key signature sharp: ', universalSharp)
            # include the found sharp, and the values for one octave up and down, as universal sharps for the key
            keySharps.append(universalSharp)
            keySharps.append(universalSharp + 12)
            keySharps.append(universalSharp - 12)
        # # print all covered octaves of the found sharps and flats
        # print('key sharps: ', keySharps)
        # print('key flats: ', keyFlats)

    # apply key signature sharps and flats to any/all corresponding notes
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


# # DETECT AND APPLY ACCIDENTALS # # -----------------------------------------------------------------------------------
    # use function to generate image without measure lines, and detect measure line locations
    # (measure lines in image can cause false flats to be detected)
    img = findMeasure(img, r_measureLine, staff, notes, width)
    # create image copy for accidentals
    accidentals_copy = img.copy()

    # store a list of measure lines to be altered as iteration progresses
    nextLine = staff.measure_lines

    for note in notes:
        if note.y_val is not None:
            # look at all notes (not rests)

            # keep track of the next line using the array, and the x-positions of the measure lines and notes
            i = 0
            while i < len(nextLine):
                if nextLine[i] < note.x_val:
                    nextLine = np.delete(nextLine, i)
                    i = i - 1
                i = i + 1

            # create a crop for each note just to the left where accidentals are expected
            crop = accidentals_copy[round(note.y_val - 1.5 * height):round(note.y_val + 2 * height),
                                    round(note.x_val - 2 * staff.line_dis):round(note.x_val + staff.line_dis / 6)]

            # template match sharps, flats, and naturals within cropped image
            AF = cv.matchTemplate(crop, r_flat, cv.TM_CCOEFF_NORMED)
            AS = cv.matchTemplate(crop, r_sharp, cv.TM_CCOEFF_NORMED)
            AN = cv.matchTemplate(crop, r_natural, cv.TM_CCOEFF_NORMED)
            # get matches above given threshold
            accidentalThresh = 0.55
            aFlatMatch = np.where(AF >= accidentalThresh)
            aSharpMatch = np.where(AS >= accidentalThresh)
            aNaturalMatch = np.where(AN >= accidentalThresh)
            # change to array
            aFlatMatch = np.asarray(aFlatMatch)
            aSharpMatch = np.asarray(aSharpMatch)
            aNaturalMatch = np.asarray(aNaturalMatch)

            found = False
            # keeps track if an accidental was found yet
            # naturals are often detected where sharps and flats are
            # so by searching in intelligent order, and flagging when an accidental is found
            # this error is prevented

            # if a flat is detected
            if aFlatMatch.shape[1] != 0:
                note.pitch = note.pitch - 1
                note.accidental = 'flat'
                found = True
                # search for other notes of the same pitch in the same measure, and if found, apply the flat to those
                for note2 in notes:
                    if note.pitch + 1 == note2.pitch:
                        if note.x_val < note2.x_val < nextLine[0]:
                            note2.pitch = note2.pitch - 1
                            note2.accidental = 'flat'

            # if a sharp is detected
            if aSharpMatch.shape[1] != 0:
                note.pitch = note.pitch + 1
                note.accidental = 'sharp'
                found = True
                # search for other notes of the same pitch in the same measure, and if found, apply the sharp to those
                for note2 in notes:
                    if note.pitch - 1 == note2.pitch:
                        if note.x_val < note2.x_val < nextLine[0]:
                            note2.pitch = note2.pitch + 1
                            note2.accidental = 'sharp'

            # if a natural is detected
            if aNaturalMatch.shape[1] != 0:
                # if other accidental was not found in the same space
                if not found:

                    # if the affected note was previously a sharp, decrease pitch
                    if note.accidental == 'sharp':
                        note.pitch = note.pitch - 1
                        note.accidental = 'natural'
                        # look for other notes of same pitch in measure to update
                        for note2 in notes:
                            if note.pitch + 1 == note2.pitch:
                                if note.x_val < note2.x_val < nextLine[0]:
                                    note2.pitch = note2.pitch - 1
                                    note2.accidental = 'natural'

                    # if the affected note was previously a flat, increase pitch
                    if note.accidental == 'flat':
                        note.pitch = note.pitch + 1
                        note.accidental = 'natural'
                        # look for other notes of same pitch in measure to update
                        for note2 in notes:
                            if note.pitch - 1 == note2.pitch:
                                if note.x_val < note2.x_val < nextLine[0]:
                                    note2.pitch = note2.pitch + 1
                                    note2.accidental = 'natural'

            # use same technique from flag detection to white out each note in the accidentals copy after it is observed
            # this prevents noteheads that are close together from being falsely detected as accidentals
            y_range = range(0, accidentals_copy.shape[0])
            x_range = range(note.x_val, note.x_val + width)
            for i in y_range:
                for j in x_range:
                    accidentals_copy[i][j] = 255


# # ADD LOCAL NOTES LIST OBJECTS TO THE STAFF OBJECT NOTES LIST # # ----------------------------------------------------
    staff.notes = []
    staff.notes = notes

    # # show box_img for testing and detection accuracy check
    # cv.imshow("accuracy check img", box_img)
    # cv.waitKey(0)

    return staff, img, height, width, keyFlats, keySharps


def main():
    imageout = noteDetect()
    return imageout


if __name__ == "__main__":
    main()
