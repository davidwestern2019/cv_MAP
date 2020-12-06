import pygame
import createMIDI

def play_music_file(music_file):
    """
    stream music with mixer.music module in blocking manner
    this will stream the sound from disk while playing
    """
    pygame.mixer.music.load(music_file)
    clock = pygame.time.Clock()
    pygame.mixer.music.play()
    # check if playback has finished
    while pygame.mixer.music.get_busy():
        clock.tick(30)


def play_music(music_file):
    # this function takes in a string MIDI filename and plays it.
    # initialize pygame mixer
    pygame.mixer.init()

    # optional volume 0 to 1.0
    pygame.mixer.music.set_volume(0.9)

    # use the midi file you just saved
    play_music_file(music_file)


def main():
    createMIDI.testMIDI()
    music_file = "major-scale.mid"
    play_music(music_file)



if __name__ == '__main__':
    main()