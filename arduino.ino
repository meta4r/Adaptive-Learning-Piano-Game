#include “Arduino.h”
#include "PCF8574.h"

uint32_t pressedButtons = 0x00000000;

PCF8574 pcf8574_1(0x20);
PCF8574 pcf8574_2(0x21);
PCF8574 pcf8574_3(0x22);

void setup() {

	for(int i=0;i<8;i++) {

		Pcf8574_1.pinMode(i, INPUT_PULLUP);
		Pcf8574_2.pinMode(i, INPUT_PULLUP);
		Pcf8574_3.pinMode(i, INPUT_PULLUP);
	}

pcf8574_1.begin();
pcf8574_2.begin();
pcf8574_3.begin();

}

void loop() {

PCF8574::DigitalInput statusOfChipOne = pcf8574_1.digitalReadAll();
PCF8574::DigitalInput statusOfChipTwo = pcf8574_2.digitalReadAll();
PCF8574::DigitalInput statusOfChipThree = pcf8574_3.digitalReadAll();

if(statusOfChipj.pi == LOW) {

	bitWrite(pressedButtons, 0, 1);
} else {

	bitWrite(pressedButtons, 1, 1);
}
}


#include "PitchToNote.h”

uint32_t previousButtons = 0x00000000;

const byte notePitches(24] = {pitchF3, ...., Pitch E5);

struct MidiData {

uint8_t Mchannel_Note;
uint8_t Mpitch;
utnt8_t Mvelocity;
}

MidiData noteOn;
MidiData noteOff;

void setup() {
	Serial begin (31250);
	delay (1000);
}


void loop() {

PlagNotes ();

}

void playNotes() {

	for(int i=0;i<24;i++) {

		if(bit(pressedButtons, i) != bit(previousButtons, i)) {

			if(bit(pressedButtons, i)) {

				bitWrite(previousButtons, i, 1);
				noteOnCreate(notePitches[i], 64);

			}

			else {
				bitWrite(previousButtons, i, 0);
				note0ffCreate(notePizches[i], 0);
			}
		}
	}
}


void noteOnCreate(byte pitch, byte velocity) {

	struct MidiData noteOn = {.Mchannel_Note = 0x90, .Mpitch = pitch, .Mvelocity = velocity};
	print_struct_to_serial (&note0n, sizeof(noteOn));
}

void noteOf£Create (byte pitch, byve velocity) (
	struct MidiData noteOff = (.Mchannel_Note = 0x80, Mpitch = pitch, .Mvelocity = velocity};

	print_struct_to_serial(&noteOff, sizeof (noteOff));
}

void print_struct_to_serial(void *data, uint8_t size) {

	uint8_t *d = (uint8_t*) data;
	uint8_t index = 0;

	for (index = 0; index < size; index++) {

		Serial.write(d[index]);
}
}
