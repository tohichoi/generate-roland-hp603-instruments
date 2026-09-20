
import collections
import sys

# Cakewalk is a Windows application and reads these files as CRLF.
# Pin it here so regenerating on Linux does not produce a whole-file diff.
sys.stdout.reconfigure(newline='\r\n')


# Bank texts are subjectively named, not read from the MIDI implementation.
# Kept as pairs rather than a dict literal: a repeated bank id silently shadows
# the earlier name, which is how 15492 'GM E' and 15494 'Effect C' were lost.
_BANK_NAME_PAIRS=(
    (68, 'Piano A'),
    (2115, 'Piano B'),
    (576, 'Piano C'),
    (1090, 'Piano & Orch'),
    (69, 'Piano D'),
    (67, 'Piano E'),
    (70, 'EP & Organ'),
    (1092, 'Belle'),
    (3137, 'EP A'),
    (2114, 'EP B'),
    (1094, 'Organ A'),
    (66, 'Organ B'),
    (1093, 'Organ C'),
    (71, 'Organ & Strings'),
    (4164, 'Bars'),
    (4165, 'Organ D'),
    (2112, 'Organ & Piano'),
    (195, 'Orchestra A'),
    (64, 'Orchestra B'),
    (0, 'Orchestra C'),
    (193, 'Orchestra D'),
    (194, 'Orchestra E'),
    (6081, 'Piano F'),
    (1088, 'Piano G'),
    (65, 'Jazz Scat'),
    (320, 'Forte Piano A'),
    (321, 'Forte Piano B'),
    (322, 'Forte Piano C'),
    (1091, 'Harpsicord'),
    (15360, 'Drums'),
    (15488, 'GM A'),
    (15489, 'GM B'),
    (15490, 'GM C'),
    (15491, 'GM D'),
    (15492, 'GM E'),
    (15493, 'Effect A'),
    (15494, 'Effect B'),
    (15495, 'Effect C'),
    (15496, 'Effect D'),
    (15497, 'Effect E'),
    )

BANK_NAMES=dict(_BANK_NAME_PAIRS)
assert len(BANK_NAMES)==len(_BANK_NAME_PAIRS), \
    'duplicate bank id in _BANK_NAME_PAIRS'


def get_bank_name(bankid):

    return BANK_NAMES.get(bankid, f'Bank#{bankid}')

inst=collections.defaultdict(list)

# The file 'hp603 instruments.txt' came from copy-and-paste of 
# 'Midi_Implementatie_Roland_LX-7.pdf' page 12-14.
# Note that some unicodes such as ' are not properly displayed in Cakewalk.
# Find and replace it manually using an editor. 
with open('hp603 instruments.txt') as fd:
    group=''
    for line in fd.readlines():
        tokens=line.strip().split()
        if len(tokens)==1:
            group=tokens[0]
            continue
        # group, index, name*, msb, lsb, program
        # * since name can have multiple words,
        #   we need to separate those from parsing

        # save msb, lsb, program 
        cval=list(map(int, tokens[-3:]))
        tokens[-3:]=[]

        inst[group].append([int(tokens[0]), ' '.join(tokens[1:])]+cval)
        # print(f'{group}\t{tokens[0]}\t'+' '.join(tokens[1:])+'\t'+'\t'.join(map(str, cval)))

banks=collections.defaultdict(list)
for k, v in inst.items():
    for vv in v:
        bankid=vv[2]*128+vv[3]
        banks[bankid].append([vv[1], vv[4]])

unnamed=sorted(set(banks)-set(BANK_NAMES))
assert not unnamed, f'unnamed banks: {unnamed}'

print(';')
print('; Cakewalk Instrument definition file for the Roland HP603')
print('; Mike Choi, Oct 2019')
print(';\n')
print('.Patch Names')

for k, v in banks.items():
    print(f'\n[{get_bank_name(k)}]')
    for vv in v:
        print(f'{vv[1]}={vv[0]}')

print('\n\n')
print('.Instrument Definitions\n')
print('[Roland HP603]')
for k, v in banks.items():
    print(f'Patch[{k}]={get_bank_name(k)}')

