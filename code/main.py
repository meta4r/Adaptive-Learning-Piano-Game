from itertools import count, cycle
from tkinter import IntVar, Label, Frame, Button, Tk, W, ttk
from tkinter import *
from PIL import Image, ImageTk
import os
import threading
import mido
from mido import MidiFile, Message, MidiTrack,MetaMessage
from midi import MidiConnector
import datetime
import pygame
from pygame.locals import *
import sys
from functools import partial
import time
import sys
import accuracyMeasurements
from practice import practiceGame
import RPi.GPIO as GPIO
from datetime import datetime
import json


data = {}
data['attempts'] = []
temp = {}
temp['attempts'] = []
"""
with open('data.txt') as json_file:
    data = json.load(json_file)
    for p in data['attempts']:
        
        date = str(p['date'])
        Song =  str(p['Song'])
        clicks =  str(p['clicks'])
        duration =  str(p['duration'])
        order =  str(p['order'])
        
        temp['attempts'].append({
            'date': date,
            'Song': Song,
            'clicks': clicks,
            'duration': duration,
            'order': order
        })

data = temp
"""
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


parent = os.getcwd() # Getting the parent directory of "src"
resources = os.path.join(parent, "src", "resources")
midi_path = os.path.join(resources, "midi-files") # Specifying the path of the MIDI files inside "resources"
png_path = os.path.join(resources, "sheet-pngs") # Specifying the path of the PNGs for the music sheet inside "resources"
examples_path = os.path.join(resources, "examples") # Specifying the path of the "examples" folder inside "resources"
practice_path = os.path.join(examples_path, "created") # Specifying the path of the "created" folder inside "examples"
piano_sounds_path = os.path.join(resources, "pianosounds") # Specifying the path of the "pianosounds" folder inside "resources"

pygame.mixer.pre_init(44100, -16, 2, 512) #Set up the mixer that will generate our sounds, 512 buffer size for minimal delay
pygame.init() #Initialize the pygame module to be able to use the mixer

NOTE_SOUNDS = [] # Creating an array to hold note sounds

#Appending all note sounds (.ogg files) to to NOTE_SOUNDS
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, 'f3.ogg')))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "gb3.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "g3.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "ab3.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "a3.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "bb3.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "b3.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "c4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "db4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "d4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "eb4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "e4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "f4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "gb4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "g4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "ab4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "a4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "bb4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "b4.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "c5.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "db5.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "d5.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "eb5.ogg")))
NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_sounds_path, "e5.ogg")))

#All midi notes from F3 to E5 in order
MIDI_NOTES = [
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76
]


NOTE_LEDS = {}

for i in range(25):
    GPIO.setup(i, GPIO.OUT)	#Set GPIO i as an output
    GPIO.output(i, False)	#Turn off GPIO i at the start

    NOTE_LEDS[i+53] = i+1



KEY_SOUND = dict(zip(MIDI_NOTES, NOTE_SOUNDS)) #Creating a key-value dictionary for all notes with their respective sounds

IS_RECORDING = False #Value to check whether we are recording or not
RUN = True #Value to control the sound thread

AM_PLAYING = False #Condition to check whether the student is playing music in the Play Mode
IS_PLAYING = False #Condition to check whether Music is playing from the Listen Mode

class ImageLabel(Label):

    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)
 
        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100
 
        if len(frames) == 1:
            self.configure(image=next(self.frames))
        else:
            self.next_frame()
 
    def unload(self):
        self.cronfigure(image=None)
        self.frames = None
 
    def next_frame(self):
        if self.frames:
            self.configure(image=next(self.frames))
            self.after(self.delay, self.next_frame)

#Creating some re-accuring fonts
centgot50 = ('Century Gothic', 50, 'bold')
centgot26 = ('Century Gothic', 26, 'bold')
centgot38 = ('Century Gothic', 38, 'bold')
centgot12 = ('Century Gothic', 12, 'bold') 
centgot20 = ('Century Gothic', 20, 'bold') 

#Quit game method
def quit_game():
    sys.exit()

#Method that generates sounds based on key presses
def soundMaker():
    global conn
    conn = MidiConnector('/dev/ttyUSB0', 31250)
    while RUN:
        if RUN == False:
            break
        msg = conn.read()
        if RUN == False:
            break
        if msg:
            if RUN == False:
                break
            print (msg)
            if msg.status == 144:
                key = msg.note_number
                if (key in KEY_SOUND.keys()):
                    KEY_SOUND[key].play()
                    GPIO.output (NOTE_LEDS[key],True)

            elif msg.status == 128:
                key = msg.note_number
                if key in KEY_SOUND.keys():
                    KEY_SOUND[key].fadeout(500)
                    GPIO.output (NOTE_LEDS[key],False)
    
    print('Out of sound loop')

#List of Songs Frame, includes all songs available
def list_of_songs(mode):
    for w in root.winfo_children():
        if w not in (mainmenu_fr, gif_lbl):
            w.destroy()

    song_list_fr = Frame(root, bg = 'black')
    song_list_fr.grid(row = 0, column = 0)
    Label(song_list_fr, text='Pick a Song', font=centgot38,
        fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=10)
    files = os.listdir(midi_path)

    if mode == 1:
        for name in files:
            Button(song_list_fr, text = os.path.join(os.path.splitext(name)[0]), bd=0, font=centgot20,fg='black', bg='white', width=25,command = partial(play_mode,name)).grid(row= files.index(name)+1, pady=5) 
    elif mode == 2:
        for name in files:
            Button(song_list_fr, text = os.path.join(os.path.splitext(name)[0]), bd=0, font=centgot20,fg='black', bg='white', width=25,command =  partial(practice_mode,os.path.join(os.path.splitext(name)[0]))).grid(row= files.index(name)+1, pady=5)  
    else:
        for name in files:
            Button(song_list_fr, text = os.path.join(os.path.splitext(name)[0]), bd=0, font=centgot20,fg='black', bg='white', width=25,command =  partial(listen_mode, name)).grid(row= files.index(name)+1, pady=5)  
    Button(song_list_fr, text='Back', font=centgot26, bd=0,
        fg='black', bg='white', width=15, command = go_home).grid(row=len(files) + 1, pady=5) 


#Method to save what the student is playing while in the Play Mode    
def playModeMidi():
    global AM_PLAYING
    global conn2
    mid = MidiFile(ticks_per_beat = 384) # Initializing a MidiFile with 384 ticks per beat, this number is the default one of the sheet generation program
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message('program_change', program=0, time=0))
    track.append(MetaMessage('set_tempo', tempo = 1000000))

    conn2 = MidiConnector('/dev/ttyUSB0', 31250)

    a = datetime.now()

    while AM_PLAYING:
        msg = conn2.read()
        if AM_PLAYING == False:
            break
        if msg:

            print (msg.type)
            b = datetime.now()
            c = b - a
            c = c.seconds + c.microseconds / 1000000
            
            
            c = int(mido.second2tick(c, 384, 1000000))
            print(c)

            if msg.status == 144:
                key = msg.note_number
                if (key in KEY_SOUND.keys()):
                    KEY_SOUND[key].play()
                    GPIO.output (NOTE_LEDS[key],True)
                track.append(Message('note_on', note=msg.note_number, velocity=msg.velocity, time = c))
                a = datetime.now()
            elif msg.status == 128:
                key = msg.note_number
                if key in KEY_SOUND.keys():
                    KEY_SOUND[key].fadeout(500)
                    GPIO.output (NOTE_LEDS[key],False)
                track.append(Message('note_off', note=msg.note_number, velocity=msg.velocity, time = c))
                a = datetime.now()
    mid.save('playdemo.mid')
    print('Playing done!')



def results(duration, clicking, order):

    for w in root.winfo_children():
        if w not in (mainmenu_fr, gif_lbl):
            w.destroy()
    dur = "Duration Accuracy: " + str(duration) + "%"
    click = "Clicks Accuracy: " + str(clicking) + "%"
    ordr = "Order Accuracy: " + str(order) + "%"



    results_fr = Frame(root, bg = 'black')
    results_fr.grid(row = 0, column = 0)
    Label(results_fr, text='Results', font=centgot38, fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=10)

    Label(results_fr, text=click, font=centgot20, bd=0,
        fg='black', bg='white', width=40).grid(row=1, pady=5)
         
    Label(results_fr, text=dur, font=centgot20, bd=0,
        fg='black', bg='white', width=40).grid(row=2, pady=5)
    
    Label(results_fr, text=ordr, font=centgot20, bd=0,
        fg='black', bg='white', width=40).grid(row=3, pady=5)
        
    
     
    Button(results_fr, text='Back', font=centgot26, bd=0,
        fg='black', bg='white', width=15, command=partial(list_of_songs, 2)).grid(row=4, pady=5) 


    

#Method to compute the accuracy level of the student after he has finished playing
def computeAccuracies(originalMidi):
    
    dur, click, order = accuracyMeasurements.getAccuracies(originalMidi)
    
    clicks_distance = accuracyMeasurements.getAccuracies(originalMidi)
    #duration_distance = accuracyMeasurements.durationDistance(compareMidi)
    #oder_distance = accuracyMeasurements.orderDistance(compareMidi)
    
    print("Accuracies: ")
    print("Clicks Percentage: ", click)
    print("Duration Percentage: ", dur)
    print("Order Percentage: ", order)
    
    return dur, click, order


#Method to generate and control the threads of the Play Mode
def record_play_mode(originalMidi):

    global AM_PLAYING
    global RUN
    global conn2
    global conn
    global t

    if not AM_PLAYING:
        RUN = False
        AM_PLAYING = True
        conn.close()
        t.join()
        x = threading.Thread(target = playModeMidi)
        x.start()
    elif AM_PLAYING:
        AM_PLAYING = False
        RUN = True
        print('recording false, starting thread')
        conn2.close()

        
        t = threading.Thread(target = soundMaker)
        t.start()
        
        dur, clicks, order = computeAccuracies(originalMidi)
        dura = "Duration Accuracy: " + str(dur) + "%"
        clicksa = "Clicks Accuracy: " + str(clicks) + "%"
        ordera = "Order Accuracy: " + str(order) + "%"
        data['attempts'].append({
            'date': (datetime.today().strftime('%d-%m-%Y - %H:%M')),
            'Song': os.path.splitext(originalMidi)[0],
            'clicks':clicks,
            'duration':dur,
            'order': order
        })
        with open('data.txt', 'w') as outfile:
            json.dump(data, outfile)
        results(dur, clicks, order)

#Play Mode Frame, takes in "midiSong" which is the name of the chosen song with .mid extension
def play_mode(midiSong):
    
    for w in root.winfo_children():
        if w not in (mainmenu_fr, gif_lbl):
            w.destroy()
    
    play_mode_fr = Frame(root, bg = 'black')
    play_mode_fr.grid(row = 0, column = 0)
    Label(play_mode_fr, text='Play Mode', font=centgot38, fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=10)
    
    if os.path.isfile(os.path.join(png_path,os.path.splitext(midiSong)[0] + ".png")):
        png = os.path.join(png_path,os.path.splitext(midiSong)[0] + ".png")

        img = Image.open(png)
        width,height = img.size
        hpercent = (514 / float(height))
        wpercent = (915 / float(width))
        wsize = int((float(width) * float(wpercent)))
        hsize = int (float(height)*float(hpercent))
        img = img.resize((int(wsize), int(hsize)), Image.ANTIALIAS)
        imag = ImageTk.PhotoImage(img)
        label = Label(play_mode_fr, image=imag)
        label.image = imag
        label.grid(row=1, pady = 10)
        Button(play_mode_fr, text = "Start/Stop", bd=0, font=centgot20,fg='black', bg='white', width=25,command = partial(record_play_mode, midiSong)).grid(row= 2, pady=5) 
        Button(play_mode_fr, text='Back', font=centgot26, bd=0,
            fg='black', bg='white', width=15, command=go_home_play).grid(row=3, pady=5) 
    
    else:
        Button(play_mode_fr, text = "Start/Stop", bd=0, font=centgot20,fg='black', bg='white', width=25,command = partial(record_play_mode, midiSong)).grid(row= 1, pady=5) 
        Button(play_mode_fr, text='Back', font=centgot26, bd=0,
            fg='black', bg='white', width=15, command=go_home_play).grid(row=2, pady=5)  
    

    
#Practice Mode Fram Instantiation
def practice_mode(midiSong):
    for w in root.winfo_children():
        if w not in (mainmenu_fr, gif_lbl):
            w.destroy()
    
    practice_mode_fr = Frame(root, bg = 'black')
    practice_mode_fr.grid(row = 0, column = 0)
    Label(practice_mode_fr, text='Practice Mode', font=centgot38,
        fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=10)

    if os.path.isfile(os.path.join(png_path,os.path.splitext(midiSong)[0] + ".png")):
        Button(practice_mode_fr, text = "Left + Right Hand", bd=0, font=centgot20,fg='black', bg='white', width=25,command = partial(left_right_hand, midiSong)).grid(row= 1, pady=5) 
        Button(practice_mode_fr, text='Right Hand', font=centgot26, bd=0,
            fg='black', bg='white', width=15, command=partial(right_hand, midiSong)).grid(row=2, pady=5) 
        Button(practice_mode_fr, text='Left Hand', font=centgot26, bd=0,
            fg='black', bg='white', width=15, command=partial(left_hand, midiSong)).grid(row=3, pady=5) 
        Button(practice_mode_fr, text='Back', font=centgot26, bd=0,
            fg='black', bg='white', width=15, command=partial(list_of_songs, 2)).grid(row=4, pady=5) 
    else:
        Label(practice_mode_fr, text='Song Not Available For This Mode', font=centgot38,
            fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=10)
        Button(practice_mode_fr, text='Back to Song Selection', font=centgot26, bd=0,
            fg='black', bg='white', width=15, command=partial(list_of_songs, 2)).grid(row=4, pady=5) 


def left_right_hand(midiSong):
    global RUN
    RUN = False
    conn.close()

    t.join()

    gem = practiceGame(midiSong, 1, KEY_SOUND)
    gem.play()

def right_hand(midiSong):
    global RUN
    RUN = False
    t.join()
    gem = practiceGame(midiSong, 2, KEY_SOUND)
    gem.play()

def left_hand(midiSong):
    global RUN
    RUN = False
    t.join()
    gem = practiceGame(midiSong, 3, KEY_SOUND)
    gem.play()
    


#Listen Mode Frame Instatiation
def listen_mode(midiSong):
    for w in root.winfo_children():
        if w not in (mainmenu_fr, gif_lbl):
            w.destroy()
    
    listen_mode_fr = Frame(root, bg = 'black')
    listen_mode_fr.grid(row = 0, column = 0)
    Label(listen_mode_fr, text='Listen Mode', font=centgot38,
    fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=10)


    if os.path.isfile(os.path.join(png_path,os.path.splitext(midiSong)[0] + ".png")):
        png = os.path.join(png_path,os.path.splitext(midiSong)[0] + ".png")
        img = Image.open(png)
        width,height = img.size
        hpercent = (514 / float(height))
        wpercent = (915 / float(width))
        wsize = int((float(width) * float(wpercent)))
        hsize = int (float(height)*float(hpercent))
        img = img.resize((int(wsize), int(hsize)), Image.ANTIALIAS)
        #img.save('resized_image.jpg')
        imag = ImageTk.PhotoImage(img)
        label = Label(listen_mode_fr, image=imag)
        label.image = imag
        label.grid(row=1, pady = 10)
        listenMid = MidiFile(os.path.join(midi_path, midiSong), clip = True)
        Button(listen_mode_fr, text = "Start/Stop", bd=0, font=centgot20,fg='black', bg='white', width=25,command = partial(music_thread,listenMid)).grid(row= 2, pady=5) 
        Button(listen_mode_fr, text='Back', font=centgot26, bd=0,
            fg='black', bg='white', width=15, command=go_home_listen).grid(row=3, pady=5) 


    else:
        listenMid = MidiFile(os.path.join(midi_path, midiSong), clip = True)
        Button(listen_mode_fr, text = "Start/Stop", bd=0, font=centgot20,fg='black', bg='white', width=25,command = partial(music_thread,listenMid)).grid(row= 1, pady=5) 
        Button(listen_mode_fr, text='Back', font=centgot26, bd=0,
            fg='black', bg='white', width=15, command=go_home_listen).grid(row=2, pady=5) 

    #print(midiSong)


#Return Home from Listen Mode
def go_home_listen():
    global IS_PLAYING
    IS_PLAYING = False
    start_mainmenu()
    

#Return Home from Play Mode
def go_home_play():
    global AM_PLAYING
    start_mainmenu()
    AM_PLAYING = False

#Play music from the Play Mode: Threaed Instatiation & Management
def music_thread(song):
    global IS_PLAYING
    
    
    if not IS_PLAYING:
        IS_PLAYING = True
        x = threading.Thread(target = music,  args=(song,))
        x.start()
    elif IS_PLAYING:
        IS_PLAYING = False
        print('recording false, starting thread')
#         if x.is_alive():
#             x.join()

#Play Music from the Play Mode: Sound Generation, Thread to be ran
def music(song):
    #print (song)
    global IS_PLAYING

    arrayOfNote = accuracyMeasurements.setTimeStamps(song)
    times = 0
    i = 0
    notesOn = []
    while times < arrayOfNote[-1].time and IS_PLAYING:
        notes = []
        for msg in arrayOfNote:
            if msg.time == times:
                notes.append(msg)
        
        if notes:            
            for msg in notes:
                if msg.type == 'note_on':
                    if msg.velocity == 0:
                        key = msg.note
                        notesOn.remove(key)
                        KEY_SOUND[key].fadeout(500)
                        GPIO.output (NOTE_LEDS[key],False)
                    
                    elif msg.note not in notesOn:
                        notesOn.append(msg.note)
                        print(msg.time)
                        key = msg.note
                        
                        if (key in KEY_SOUND.keys()):
                            KEY_SOUND[key].play()
                        GPIO.output (NOTE_LEDS[key],True)
                        
                    
                elif msg.type == 'note_off':
                    key = msg.note
                    notesOn.remove(key)
                    
                    if key in KEY_SOUND.keys():
                        KEY_SOUND[key].fadeout(500)
                        GPIO.output (NOTE_LEDS[key],False)

                        
        time.sleep(0.002604166667)
        times += 1

#Start Playing Frame
def start_game():
    mainmenu_fr.grid_forget()
    start_game_fr = Frame(root, bg='black')
    start_game_fr.grid(row=0, column=0)
    Label(start_game_fr, text='Start Game', font=centgot38,
          fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=20)

    Button(start_game_fr, text='Play Mode', bd=0, font=centgot26,
           fg='black', bg='white', width=15, command = lambda: list_of_songs(1)).grid(row=1, pady=5)
    Button(start_game_fr, text='Practice Mode', bd=0, font=centgot26,
           fg='black', bg='white', width=15, command = lambda: list_of_songs(2)).grid(row=2, pady=5)

    Button(start_game_fr, text='Listen Mode', bd=0, font=centgot26,
           fg='black', bg='white', width=15, command = lambda: list_of_songs(3)).grid(row=3, pady=5)
    Button(start_game_fr, text='Back', font=centgot26, bd=0,
           fg='black', bg='white', width=15, command = go_home).grid(row=4, pady=5)

#Main Menu Frame
def start_mainmenu():
    for w in root.winfo_children():
        if w not in (mainmenu_fr, gif_lbl):
            w.destroy()
    mainmenu_fr.grid(row = 0, column = 0)

#Go home
def go_home():
    start_mainmenu()

#Record MIDI thread, records what the user is playing in the Enter Piece
def recordMidi():
    global IS_RECORDING
    global conn1
    mid = MidiFile(ticks_per_beat = 384) # Initializing a MidiFile with 384 ticks per beat, this number is the default one of the sheet generation program
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message('program_change', program=0, time=0))
    track.append(MetaMessage('set_tempo', tempo = 1000000))
    mid.ticks_per_beat = 384
    conn1 = MidiConnector('/dev/ttyUSB0', 31250)

    a = datetime.now()

    while IS_RECORDING:
        msg = conn1.read()
        if IS_RECORDING == False:
            break
        if msg:

            print (msg.type)
            b = datetime.now()
            c = b - a
            c = c.seconds + c.microseconds / 1000000
            
            print(c)
            c = int(mido.second2tick(c, 384, 1000000))
            print(c)

            if msg.status == 144:
                key = msg.note_number
                if (key in KEY_SOUND.keys()):
                    KEY_SOUND[key].play()
                    GPIO.output (NOTE_LEDS[key],True)
                track.append(Message('note_on', note=msg.note_number, velocity=msg.velocity, time = c))
                a = datetime.now()
            elif msg.status == 128:
                key = msg.note_number
                if key in KEY_SOUND.keys():
                    KEY_SOUND[key].fadeout(500)
                    GPIO.output (NOTE_LEDS[key],False)
                track.append(Message('note_off', note=msg.note_number, velocity=msg.velocity, time = c))
                a = datetime.now()
    mid.save(os.path.join(midi_path,'Demo.mid'))
    toLilypond = 'sudo midi2ly '+ os.path.join(midi_path,'Demo.mid')
    print(toLilypond)
    os.system(toLilypond)
    print('Recording done!')

#Record MIDI, thread control method, makes sure all threads are properly instatiated
def record_action():

    global IS_RECORDING
    global RUN
    global conn1
    global conn
    global t
    
    if not IS_RECORDING:
        RUN = False
        IS_RECORDING = True
        conn.close()
        t.join()
        x = threading.Thread(target = recordMidi)
        x.start()
    elif IS_RECORDING:
        IS_RECORDING = False
        RUN = True
        print('recording false, starting thread')
        conn1.close()
        time.sleep(1)
        t = threading.Thread(target = soundMaker)
        t.start()
        
#Enter Piece Frame
def enter_piece():
    mainmenu_fr.grid_forget()
    enter_piece_fr = Frame(root, bg='black')
    enter_piece_fr.grid(row=0, column=0)
    Label(enter_piece_fr, text='Enter a Piece', font=centgot26).grid(row=0, column=0,sticky=W, pady=10)
    entry1 = Entry(enter_piece_fr,
          bd=0, width=18).grid(row=2, pady=20)
    Button(enter_piece_fr, text='Start/Stop', font=centgot26,
           fg='black', bg='white', bd=0, width=18, height=2, command = record_action ).grid(row=3, pady=20)
    Button(enter_piece_fr, text='Back', font=centgot26, bd=0,
           fg='black', bg='white', width=15, command=go_home).grid(row=4, pady=5)    


def show_perf():
    perf = [('Date Time', 'Song Name', 'Click Accuracy', 'Duration Accuracy', 'Overall Accuracy')]
    i = 2
    with open('data.txt') as json_file:
        data = json.load(json_file)
        arr = data['attempts']
        for p in arr[::-1]:
            i+=1
            date = str(p['date'])
            Song =  str(p['Song'])
            clicks =  str(p['clicks']) + "%"
            duration =  str(p['duration']) + "%"
            order =  str(p['order']) + "%"
            
            perf.append(
                (date, Song, clicks, duration, order)
            )



    mainmenu_fr.grid_forget()
    trackperf_fr = Frame(root, bg='black')
    Label(trackperf_fr, text='History', font=centgot26).grid(row=0, column=0,sticky=W, pady=10)
    trackperf_fr.grid(row=0, column=0)
    for dt, song, clc, dur, ov in perf:
        row(Label(trackperf_fr, bg='black'),dt, song, clc, dur, ov).grid(columnspan=5, pady=4)
    Button(trackperf_fr, text='Back', font=centgot26, bd=0,
        fg='black', bg='white', width=15, command=go_home).grid(row=i, pady=5) 

def row( label,datetime, songname, click_acc, dur_acc, overall_acc):
    Label(label, text=datetime, bg='white', fg='black', font=centgot12, width=15).grid(row=0, column=0)
    Label(label, text=songname, bg='white', fg='black', font=centgot12, width=40).grid(row=0, column=1)
    Label(label, text=click_acc, bg='white', fg='black', font=centgot12, width=15).grid(row=0, column=2)
    Label(label, text=dur_acc, bg='white', fg='black', font=centgot12, width=18).grid(row=0, column=3)
    Label(label, text=overall_acc, bg='white', fg='black', font=centgot12, width=15).grid(row=0, column=4)
    return label

root = Tk() #Initializing the GUI
root.title('Digital Piano Tutor')#Setting the title of the window
root.geometry('1067x600')#Setting the size of the window
root.config(bg = 'black')#Setting bg color

#Running the gif file as a background for our GUI using the created ImageLabel class
gif_lbl = ImageLabel(root, bd=0, width=1280, height=720, bg='black')
gif_lbl.grid(row=0,column=0)
gif_lbl.load('musical_notes.gif')

title_lbl = Label(root, text = 'Digital Piano tutor', fg = 'white', bg = 'black', font = centgot50)
title_lbl.grid(row=0,column=0)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

t = threading.Thread(target = soundMaker)
t.start()

mainmenu_fr = Frame(root, bg = 'black') #creating the main menu frame
trackperf_fr = Frame(root, bg = 'black')#creating the track performance frame
start_game_fr = Frame(root, bg = 'black')
#Creating the main title label
Label(mainmenu_fr, text='Digital Piano Tutor', font=centgot38,
                  fg='black', bg='white',bd=0, width=18, height=2).grid(row=0, pady=20)

#Creating the necessary buttons in main menu
Button(mainmenu_fr, text='Start Playing',bd=0, font=centgot26,
                  fg='black', bg='white', width=15, command = start_game).grid(row=1, pady=5)
Button(mainmenu_fr, text='Enter a Piece',bd=0, font=centgot26,
                  fg='black', bg='white',  width=15, command = enter_piece).grid(row=2, pady=5)

Button(mainmenu_fr, text='Track Performance', bd=0,font=centgot26,
                  fg='black', bg='white',  width=15, command=show_perf).grid(row=3, pady=5)
Button(mainmenu_fr, text='Quit', font=centgot26,bd=0,
                  fg='black', bg='white', width=15, command=quit_game).grid(row=4, pady=5)

root.bind_all('<Escape>', lambda e: start_mainmenu()) #Whenever Escape is pressed, go back to main menu


def waithere():
    t = IntVar()
    root.after(5000, t.set, 1)
    root.wait_variable(t)
waithere()

if title_lbl in root.winfo_children():    
    start_mainmenu()

root.mainloop()