# Cakewalk instrument definition generator for digital pianos

Roland HP603 과 Yamaha CLP-685 의 악기 정의 파일(`.ins`)을 생성합니다.

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

## 재생성 방법

의존성을 설치합니다. 스크립트별로 필요한 모듈이 다릅니다.

| 스크립트 | 필요한 모듈 |
| :--- | :--- |
| `generate_cakewalk_ins.py` | 없음 (표준 라이브러리만) |
| `generate_cakewalk_yamaha_ins.py` | `toml` |
| `make_toml.py` | `tomli`, `rich` |
| `find_instruments.py` | `streamlit`, `toml`, `pandas` |
| `find_roland_gm_inst.py` | `mido` |
| `test_program_change.py` | `python-rtmidi` |

`requirements.txt` 는 UTF-16 으로 저장되어 있어 `pip install -r` 은 동작하지만, UTF-8 을 가정하는 편집기나 도구로는 읽히지 않습니다. 또한 환경 전체를 덤프한 목록이므로 `python-rtmidi` 가 빠져 있습니다.

Roland 산출물은 다음 한 줄로 재생성됩니다. 데이터는 `hp603 instruments.txt` 입니다.

```bash
python3 generate_cakewalk_ins.py > "Roland HP603.ins"
```

Yamaha 산출물은 데이터 변환이 한 단계 앞에 있습니다. `data/yamaha-clp685-data.txt` 를 먼저 TOML 로 바꾼 뒤 생성합니다.

```bash
python3 make_toml.py                              # -> data/yamaha-clp685-data.toml
python3 generate_cakewalk_yamaha_ins.py > "Yamaha CLP-685.ins"
```

`data/yamaha-clp685-data.toml` 은 저장소에 포함되어 있으므로, 생성기만 다시 돌릴 때는 `make_toml.py` 를 건너뛰어도 됩니다. 데이터 리스트(`.txt`)를 고쳤을 때만 다시 변환하면 됩니다.

## How to

### CLP 685 지원 MIDI 형식

- GM System Level 2
- XG
- GS

### 기본 개념 

악기 선택은 다음 형태로 전송된다

`CC#0 BankSelect-MSB  CC#32 BankSelect-LSB  PC`

예를 들어 clp685 의 CFX Grand 는 아래와 같이 정의된다.

`CFX Grand 108 0 1`

이 때 bank number 는 `128*108+0=13824` 이고 patch 는 `1` 이다.

비슷한 예로 Bösendorfer 는 아래와 같다.

`Bösendorfer 108 6 1`

bank number 는 `128*108+6=13830` 이고 patch 는 `1` 이다.

> 참고: 이 절에는 원래 CLP-685 화면 캡처가 있었으나 저장소에 포함되어 있지 않습니다.

### Cakewalk ins 파일 생성 로직

`.ins` 파일은 다음과 같은 챕터로 구성된다.

```
.Patch Names

[<BANK_NAME#1>]
<PATCH#1>=<INSTRUMENT_NAME#1>
<PATCH#2>=<INSTRUMENT_NAME#2>

[<BANK_NAME#2>]
<PATCH#1>=<INSTRUMENT_NAME#1>
<PATCH#2>=<INSTRUMENT_NAME#2>

.Instrument Definitions

[<INSTRUMENT_NAME>]
Patch[<BANK_NUMBER#1>]=<BANK_NAME#1>
Patch[<BANK_NUMBER#2>]=<BANK_NAME#2>
```

먼저 `.Instrument Definitions` 을 정의한다.

CFX Grand 를 정의해보자.
CFX Grand 의 bank number 는 위에서 구한 13824 이고 아래와 같이 정의한다.

```
[Yamaha CLP-685]
Patch[XXXXX]=YYYYY
```

여기서 xxxxx 는 bank number 인 13824 이고 YYYYY 는 bank 이름이다.
이게 좀 헷갈리는데 `Patch[XXXXX]` 는 실제로 bank number 의미이고 악기를 나타내지 않는다.

이름을 정할 때 제조사의 매뉴얼을 확인하면 좋다.

> 참고: 이 절에는 원래 CLP-685 데이터 리스트 화면 캡처가 있었으나 저장소에 포함되어 있지 않습니다.

위와 같이 CFX Grand 의 Voice Group 은 Piano 로 정의했으나 실제로 MSB/LSB 가 다른 악기들이 포함되어있다.

편하게 Bank#13824 정도로 지으면 좋다.

```
[Yamaha CLP-685]
Patch[13824]=Bank#13824
```

그런 다음 `Bank#13824` 섹션을 `.Patch Names` 에서 정의한다

```
.Patch Names

[Bank#13824]
1=CFX Grand
2=Bright Grand
3=Rock Grand
```

위에서 2, 3 은 동일한 bank number 를 가지는 악기이므로 해당 섹션에 포함한다.

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
