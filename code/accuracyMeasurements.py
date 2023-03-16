from mido import MidiFile, Message, MidiTrack, MetaMessage
import numpy
import os
import math


parent = os.getcwd()

#mid1 = MidiFile("rami.mid", clip = True)
midi_path = os.path.join(parent, "midi-files")

#midStudent = MidiFile("Au Claire De La Lune.mid",clip = True)

#################################################################### Helper Methods ########################################################################
 
#Storing the notes of a MIDI file in an array and returning it
def getNotes(mid):
    notesArray = []
    for j in range (0,len(mid.tracks)):
        for msg in mid.tracks[j]:
            if msg.type == 'note_on' and msg.velocity != 0:
                notesArray.append(msg.note) 
    #print (notesArray)
    return notesArray
 
#Storing the notes of a MIDI file in an array and returning it
def getNote(mid):
    notesArray = []

    for msg in mid:
        if msg.type == 'note_on' and msg.velocity != 0:
            notesArray.append(msg.note) 
    #print (notesArray)
    return notesArray


#Getting the occurrences of each note in a MIDI file
def getNoteOccurences(mid): 
    notesArray = getNotes(mid)
    values, counts = numpy.unique(notesArray, return_counts = True)

    notesDictionary = {values[i]:counts[i] for i in range (len (values))}
    return notesDictionary

#Return an array of the MIDI messages with time element being representend in timestamps
def setTimeStamps(mid):
    noteCollection = []
    #print(mid.tracks)
    
    for j in range (0, len(mid.tracks)):
        time = 0       
        for msg in mid.tracks[j]:
            #print (msg)
            time+=msg.time
            tempMsg = msg
            tempMsg.time = time
            noteCollection.append(tempMsg)

        
    return noteCollection

#Return a dictionary containing the total duration of each note present throughout the piece
#Takes the output of setTimeStamps as parameter
def setDuration(notesCollection):
    #print (len(notesCollection))
    #notesCollection = setTimeStamps(notesCollection)
    
    incompleteNotes = {}
    durationNotes = {}
    

    length = notesCollection[-1].time

    duration = 0

    for msg in notesCollection:
        if msg.type == 'note_on':
            if msg.velocity == 0:
                if msg.note in incompleteNotes.keys():
                    duration = msg.time - incompleteNotes[msg.note]
                    if msg.note not in durationNotes:
                        durationNotes[msg.note] = duration
                    else:    
                        durationNotes[msg.note] = durationNotes[msg.note] + duration
            else:
                incompleteNotes[msg.note] = msg.time
        elif msg.type == 'note_off':
            if msg.note in incompleteNotes.keys():
                    duration = msg.time - incompleteNotes[msg.note]
                    if msg.note not in durationNotes:
                        durationNotes[msg.note] = duration
                    else:    
                        durationNotes[msg.note] = durationNotes[msg.note] + duration
    return durationNotes, length



######################################################################### Accuracy Measurement Methods #######################################################################

#Returns the difference between the total duration of each note
def durationDistance(notes1,notes2):
    
    difference = {}
    notes1, length1 = setDuration(setTimeStamps(notes1)) #Setting timestamps of each MIDI note in first MIDI file
    notes2, length2 = setDuration(setTimeStamps(notes2))#Setting timestamps of each MIDI note in second MIDI file
    
    numerator = 0
    sum1 = 0
    sum2 = 0

    
    #Getting the difference between each note's total playtime in first MIDI file   
    for key in notes1.keys(): 
        sum1 += pow(notes1[key], 2)
        if key in notes2.keys():
            mult = notes1[key] * notes2[key]
            numerator += mult
            diff = abs(notes1[key] - notes2[key])
        else:
            diff = notes1[key]
        difference[key] = diff
    
    #Getting the difference between each note's total playtime in second MIDI file
    for key in notes2.keys(): 
        diff = 0
        sum2 += pow(notes2[key], 2)
        if key not in difference.keys():
            diff = notes2[key]
            difference[key] = diff

    similarityCos =  numerator / math.sqrt((sum1 * sum2))
    print (similarityCos)
    return similarityCos

#Returns the difference between total amount of each note's presses
def clicksDistance(notes1, notes2): 
    
    difference = {}

    sum = 0

    notesDictionary1 = getNoteOccurences(notes1) #Getting the occurence of each note in MIDI file 1
    notesDictionary2 = getNoteOccurences(notes2) #Getting the occurence of each note in MIDI file 2
    
    #print(notesDictionary1)
    #print(notesDictionary2)
    
    original = 0
    
    for msg in notes1:
        if msg.type == 'note_on' and  msg.velocity != 0:
            original += 1

    #Getting the difference between each note's total clicks in first MIDI file
    for key in notesDictionary1.keys():
        diff = 0
        if key in notesDictionary2.keys():
            diff = abs(notesDictionary1[key] - notesDictionary2[key])
        else:
            diff = notesDictionary1[key]
        difference[key] = diff

    #Getting the difference between each note's total clicks in second MIDI file
    for key in notesDictionary2.keys():
        diff = 0
        if key not in difference.keys():
            diff = notesDictionary2[key]
            difference[key] = diff

    #Summing all differences to get a single measure
    for key in difference.keys(): 
        sum += difference[key]
    return (original - sum) / original


#Returns the distance between the original piece and what the user played
def orderDistance(mid1, mid2):
    
    orderedNotesArray1 = setTimeStamps(mid1)
    orderedNotesArray2 = setTimeStamps(mid2)

    orderedNotesArray1.sort(key = lambda x: x.time)
    orderedNotesArray2.sort(key = lambda x: x.time)


    notesArray1 = getNote(orderedNotesArray1)
    notesArray2 = getNote(orderedNotesArray2)


    print(notesArray1)
    print(notesArray2)



    

    m = len(orderedNotesArray1)
    n = len(orderedNotesArray2)

    return 1-edit_distance(notesArray1, notesArray2)/(m+n)

    #If either of the arrays is empty, meaning the midi file is empty,
    #Return the size of the other 
 
def edit_distance(s1, s2):
    m=len(s1)+1
    n=len(s2)+1

    tbl = {}
    for i in range(m): tbl[i,0]=i
    for j in range(n): tbl[0,j]=j
    for i in range(1, m):
        for j in range(1, n):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)

    print (tbl[i,j])

    return tbl[i,j]

def getAccuracies(midOriginal):
    #print(os.path.join(midi_path, midOriginal))
    midStudent = MidiFile("rami.mid",clip = True)
    midiOriginal = MidiFile(os.path.join(midi_path, midOriginal), clip = True)
    #midiOriginal = MidiFile("Au Claire De La Lune.mid", clip = True)
    #print(midOriginal)
    order = orderDistance(midiOriginal, midStudent) * 100
    dur = durationDistance(midiOriginal, midStudent) * 100
    click = clicksDistance(midiOriginal, midStudent) * 100
    
    
    return ("%.2f" % dur), ("%.2f" % click), ("%.2f" % order)


"""
#
#setDuration(setTimeStamps(MidiFile("Au Claire De La Lune.mid", clip = True)))
#print(editDistance("sunday", "saturday", len("sunday"),len("saturday")))
midStudent = MidiFile("rami.mid",clip = True)
mid = MidiFile(os.path.join(midi_path, "Au Claire De La Lune.mid"), clip = True)
dur, click, order = getAccuracies("Au Claire De La Lune.mid")
print("Duration: " , dur)
print("Clicks: " , click)
print("Order: " , order)
noteCollection = []
#print(mid.tracks)
time = 0
for msg in mid.tracks[1]:
    #print (msg)
    time+=msg.time
    tempMsg = msg
    tempMsg.time = time
    if msg.type == 'note_on':
        if msg.velocity != 0:
            noteCollection.append(tempMsg)
    
print(noteCollection)
"""