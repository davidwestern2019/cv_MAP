# This  file is a collection of functions and classes that are to be used throughout the project
# functions that are commonly used should be put here to avoid redefinition
# classes that are used across the layers of the project should also be put here to avoid any issues

import cv2 as cv
import sys


class StaffClass:
    l1 = None
    l2 = None
    l3 = None
    l4 = None
    l5 = None
    line_dis = None
    staff_number = None     # this represents whether its the 1st, 2nd, 3rd, etc staff encountered when going down the page
    staff_start = None      # pixel/row where the staff begins
    staff_end = None        # pixel/row where the staff ends
    line_locations = []     # list of tuples. Each tuple has the start and end row of the line. List should be sorted
                            # from top line first to bottom line last
    dis = None              # this is the spacing between the staff lines. helps determine font (Roth 1994)
    line_length = None      # length of staff lines. Also is the width of the entire staff
    notes = None            # this is a list of notes in order from left to right. Notes are instances of NoteClass
    measure_lines = None

    def __init__(self, num):
        self.staff_number = num


class NoteClass:
    x_val = None
    y_val = None
    pitch = None            # pitch of note. use MIDI note system. refer to MIDIutil for info
    duration = None         # how long the note is held for
    orig_pitch = None       # pitch of note without looking at key signature or accidentals
    orig_dur = None         # duration of note without any modifications (like dots)
    accidental = None       # Either None, 'sharp', or 'flat'. The latter two being strings
                            # put a flag here to signify that a note is sharp or flat.
                            # this is for labeling the notes correctly (MIDI doesn't know sharp vs flat)
    beam_flag = False
    # rando


    def __init__(self, dur, x, y):
        self.orig_dur = dur
        self.x_val = x
        self.y_val = y

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


# function to turn MIDI note number into letter
def midiNum2Letter(note_num, accidental=None):
    # INPUT
    # -- note_num   =   this is a number in MIDI numbering that corresponds to a note
    # OUTPUT
    # -- letter     =   letter of the note. Does NOT include the number of the note

    # this array of strings has the note letters and whether they're sharp or flat
    array_letters = ('C', 'C#Db', 'D', 'D#Eb', 'E', 'F', 'F#Gb', 'G','G#Ab', 'A', 'A#Bb', 'B')

    index = note_num % 12
    note = array_letters[index] # there are only 12 notes in an octave. midi numbers start at A = 1
    letter = ''
    if accidental == 'sharp':   # note is sharp
        letter = note[0:1]
    elif accidental == 'flat':
        letter = note[2:]       # note is flat
    else:
        if len(note) == 4:
            letter = note[0:2]  # by default, use sharp if no indication is given
        else:
            letter = note       # just a plain letter. No sharp or flat
    return letter

def main():
    # test the functions
    letter = midiNum2Letter(61)
    print(letter)

if __name__ == '__main__':
    main()

