# This  file is a collection of functions and classes that are to be used throughout the project
# functions that are commonly used should be put here to avoid redefinition
# classes that are used across the layers of the project should also be put here to avoid any issues

import cv2 as cv
import sys

class StaffClass:
    staff_number = None     # this represents whether its the 1st, 2nd, 3rd, etc staff encountered when going down the page
    staff_start = None      # pixel/row where the staff begins
    staff_end = None        # pixel/row where the staff ends
    line_locations = []     # list of tuples. Each tuple has the start and end row of the line. List should be sorted
                            # from top line first to bottom line last
    dis = None              # this is the spacing between the staff lines. helps determine font (Roth 1994)
    line_length = None      # length of staff lines. Also is the width of the entire staff
    notes = None            # this is a list of notes in order from left to right. Notes are instances of NoteClass

    def __init__(self, num):
        self.staff_number = num


class NoteClass:
    pitch = None            # pitch of note
    duration = None         # how long the note is held for
    orig_pitch = None       # pitch of note without looking at key signature or accidentals
    orig_dur = None         # duration of note without any modifications (like dots)
    location = None         # tuple (row, column) of the note's location

    def adjustPitch(self, accidental):
        if accidental == 'flat':
            # apply flat to note
            # self.pitch = ...
            pass
        else:
            # apply neutral to note
            # self.pitch = ...
            pass


    def adjustDuration(self, something):
        # adjust duration here
        pass


# Mouse callback function. Appends the x,y location of mouse click to a list.
def get_xy(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(x, y)
        param.append((x, y))