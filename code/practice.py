import pygame
import os
import os.path
import threading
from mido import MidiFile, Message, MidiTrack,MetaMessage
from midi import MidiConnector
import RPi.GPIO as GPIO

NOTE_LEDS = {}
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for i in range(25):
    GPIO.setup(i, GPIO.OUT)	#Set GPIO i as an output
    GPIO.output(i, False)	#Turn off GPIO i at the start

    NOTE_LEDS[i+53] = i+1

conn3 = MidiConnector('/dev/ttyUSB0', 31250)

parent = os.getcwd() #Getting the working directory path
practice_path = os.path.join(os.path.join(parent,"examples"),"created")

class practiceGame(object):
    def __init__(self, midiSong, mode, sounds):
        self.midiSong = midiSong
        if mode == 1:
            self.mode = os.path.join(os.path.join(practice_path,midiSong), "hands_left_right")
        elif mode == 2:
            self.mode = os.path.join(os.path.join(practice_path,midiSong), "hands_right")
        elif mode == 3:
            self.mode = os.path.join(os.path.join(practice_path,midiSong), "hands_left")
        self.KEY_SOUND = sounds
        self.correct_notes = 60
        self.perform_initialization()


    def perform_initialization(self):
        self.init_pygame()
        self.load_notes()
        self.load_images()
        self.is_running = True
        self.current_step = -2
        self.update_step()

    def load_notes(self):
        self.note_names = []
        with open(os.path.join(self.mode, "midi_notes.txt")) as infile:
            for line in infile.read().split("\n"):
                if line != "":
                    data = [int(n) for n in line.split(" ")]
                    self.note_names.append(data)
        self.note_names.append([])
        print(len(self.note_names))


    def load_images(self):
        self.images = []    
        filename = os.path.join(self.mode, "presentation_mode_start.png")
        

        files = [f for f in os.listdir(self.mode) if os.path.isfile(os.path.join(self.mode, f))]
        files = sorted(files)
        for f in files:
            extension = os.path.splitext(f)[1]
            if extension == ".png" and f != "presentation_mode_start.png":
                filename = os.path.join(self.mode, f)
                self.images.append(pygame.image.load(filename))
        #filename = os.path.join(self.mode, "presentation_mode_start.png")
        #self.images.append(pygame.image.load(filename))
        self.images.append(pygame.image.load(os.path.join(self.mode, "presentation_mode_start.png")))
        no_of_steps = len(self.images)
        print(str(no_of_steps) + " images loaded.")

    def update_step(self, direction="forward"):
        if direction == "forward":
            self.current_step = (self.current_step + 1) % len(self.images)
        elif direction == "backward":
            self.current_step = (self.current_step - 1)
            if self.current_step == -1:
                self.current_step = len(self.images) - 1
        
        self.current_activations = []
        if not isinstance(self.correct_notes,int):
            for led in self.correct_notes:
                GPIO.output (NOTE_LEDS[led],False)
        else :
            GPIO.output (NOTE_LEDS[self.correct_notes],False)
        self.correct_notes = self.note_names[self.current_step]
        
        for led in self.correct_notes:
            GPIO.output (NOTE_LEDS[led],True)
        white = (255,255,255)
        self.display.fill(white)
        self.images[self.current_step].convert()
        rect = self.images[self.current_step].get_rect()
        rect.center = 1920/2, 1080/2
        self.display.blit(pygame.transform.scale(self.images[self.current_step], (1280,720)), (0,0))
        pygame.display.update()

    def reaction_note_on(self,note):
        pitch = note.note_number
        velocity = note.velocity
        if velocity > 0:
            if pitch in self.correct_notes:
                if not pitch in self.current_activations:
                    self.current_activations.append(note)
                    if len(self.current_activations) == len(self.correct_notes):
                        self.update_step()
            elif self.current_step == len(self.images)-1:
                self.update_step()

    
    def notesThread(self):
        global conn3

        print("in thread")

        while self.is_running:
            msg = conn3.read()
            if self.is_running == False:
                break
            if msg:
                print(msg)
                if msg.status == 144:
                    key = msg.note_number
                    self.reaction_note_on(msg)
                    if (key in self.KEY_SOUND.keys()):
                        self.KEY_SOUND[key].play()
                    

                elif msg.status == 128:
                    key = msg.note_number
                    
                    self.reaction_note_on(msg)
                    if key in self.KEY_SOUND.keys():
                        self.KEY_SOUND[key].fadeout(500)

    
    
    def init_pygame(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        pygame.init()

        info = pygame.display.Info()
        self.display = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
       
    def play(self):
        global conn3
        n = threading.Thread(target = self.notesThread)
        n.start()
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                    if event.key == pygame.K_RIGHT:
                        self.update_step()
                    if event.key == pygame.K_LEFT:
                        self.update_step(direction="backward")
                elif event.type == pygame.QUIT:
                    self.is_running = False
        conn3.close()
        pygame.quit()