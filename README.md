# Cakewalk instrument definition generator for HP603 digital piano

## Motivation

After Roland HP603 came into my house, I felt the internet has no instrument definition file for it.
Since the user manual is lack of information about MIDI, I've tried bank/patching manually in Cakewalk. 

However, it was not easy to know how it works. 

By digging into MIDI and Cakewalk instrument definition file structure, I've made what I want; changing instruments with a couple of clicks.
Here is Roland HP603 instrument definition file.
I hope someone could save his /her time for producing music with HP603.
If you want to make an ins file, I'll give you my tools for reference(some python scripts).


## Installation:

1. Download `Roland HP603.ins` to your computer.
2. Open Cakewalk by BandLab.
3. Go to Edit -> Preferences.
4. In the left side find 'Instruments' under MIDI section.
5. Your instrument will be shown in the Output/Channel if it was connected.
6. Click 'Define...' button.
7. Another dialogbox will be shown. Click 'Import...' button.
8. Choose saved file (C:\Users\user\Downloads\Roland HP603.ins).
9. Click 'Roland HP603' and 'OK' button.
10. Click 'Close' button.
11. Select your instrument from channel 1 to 16 on the left hand side.
12. Click 'Roland HP603' on the right hand side.
13. Click 'Apply' and 'OK'.


## Simplifying Cakewalk .ins file structure:

```
.Patch Names

[BankName-A]

ProgramNumber=ProgramName

...

[BankName-B]

ProgramNumber=ProgramName

...



.Instrument Definitions

[InstrumentName]

Patch[BankNumber1]=BankName-A

Patch[BankNumber2]=BankName-B

...



BankNumber = CC#0 * 128 + CC#32

ProgramNumber = PC
```

## Caveats

1. Feel free to change whatever you need.
2. Drum patch is not tested(my holiday is over!)


## References

### MIDI Specification
https://www.midi.org/specifications
http://www.music-software-development.com/midi-tutorial.html


### MIDI Programming(python, c#)
https://www.pygame.org/
https://pypi.org/project/python-rtmidi/
https://mido.readthedocs.io/en/latest/index.html
https://docs.microsoft.com/en-us/windows/win32/multimedia/musical-instrument-digital-interface--midi

### HP603 MIDI Implementation
http://cms.rolandus.com/assets/media/pdf/INFOCUS01_MIDI.pdf
https://static.roland.com/assets/media/pdf/LX_HP_KF-10_GP_DP_RP102_FP-10_MIDI_Imple_eng04_W.pdf

### Cakewalk ins file
https://www.cakewalk.com/Documentation?product=SONAR%20X2&language=3&help=Instrument_Defs.07.html
http://www.raisedbar.co.uk/InsDef.htm
http://www.heikoplate.de/mambo/index.php?option=com_content&task=view&id=426&Itemid=63