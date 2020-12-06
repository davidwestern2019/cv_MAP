from midiutil import MIDIFile
import utilities_cv


def testMIDI():
    # this function is pretty much for just playing around with the midi file creation module called midiUtil
    print("Creating midi")
    degrees  = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number
    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1/2    # In beats
    tempo    = 120   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                          # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i/2, duration, volume)

    with open("major-scale.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)


def addNotestoMIDI(list_notes, music_name):
    # set midi parameters
    track = 0
    channel = 0
    time = 0
    tempo = 120  # In BPM
    volume = 100  # 0-127, as per the MIDI standard

    # initialize midi object
    music_midi = MIDIFile(1)
    music_midi.addTempo(track, time, tempo)

    # add notes to list
    for note in list_notes:
        music_midi.addNote(track, channel, pitch=note.pitch, time=time, duration=note.duration, volume=volume)
        time += note.duration

    # write file
    out_file_name = music_name + ".mid"
    with open(out_file_name, "wb") as output_file:
        music_midi.writeFile(output_file)


def addNotesToMidiList(staves):
    # This function adds notes to a list to make it easier to create the MIDI files with midiUtil
    # INPUT: list of StaffClass objects, where the StaffClass.notes list is not None
    # OUTPUT: list of notes.
    notesList_for_MIDI = []
    for staff in staves:
        if staff.notes is None:
            print("Error! Staff does not have notes in its notes member")
        else:
            for note in staff.notes:
                if note.duration is None:
                    note.duration = note.orig_dur
                    notesList_for_MIDI.append(note)
                else:
                    notesList_for_MIDI.append(note)

    return notesList_for_MIDI


def createMIDI(staves, music_name):
    notes_list = addNotesToMidiList(staves)
    addNotestoMIDI(notes_list, music_name)


def testStaves():
    staves = []

    # staff 1
    staff1 = utilities_cv.StaffClass(1)
    staff1.notes = []
    staff1.staff_end = 50
    staff1.dis = 4
    for i in range(4):
        note = utilities_cv.NoteClass(1, 0, 0)
        note.pitch = 60
        # note.duration = 1
        staff1.notes.append(note)

    # staff 2
    staff2 = utilities_cv.StaffClass(2)
    staff2.notes = []
    staff2.staff_end = 150
    staff2.dis = 4
    for i in range(8):
        note = utilities_cv.NoteClass(1/2, 0, 0)
        note.pitch = 68
        # note.duration = 1/2
        staff2.notes.append(note)

    # append staff
    staves.append(staff1)
    staves.append(staff2)

    return staves
