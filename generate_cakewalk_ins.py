
import collections


def get_bank_name(banks, bankid):
    # bank texts are subjectively named.
    names={
        68:'Piano A',
        2115:'Piano B',
        576:'Piano C',
        1090:'Piano & Orch',
        69:'Piano D',
        67:'Piano E',
        70:'EP & Organ',
        1092:'Belle',
        3137:'EP A',
        2114:'EP B',
        1094:'Organ A',
        66:'Organ B',
        1093:'Organ C',
        71:'Organ & Strings',
        4164:'Bars',
        4165:'Organ D',
        2112:'Organ & Piano',
        195:'Orchestra A',
        64:'Orchestra B',
        0:'Orchestra C',
        193:'Orchestra D',
        194:'Orchestra E',
        6081:'Piano F',
        1088:'Piano G',
        65:'Jazz Scat',
        320:'Piano H',
        320:'Forte Piano A',
        321:'Forte Piano B',
        322:'Forte Piano C',
        1091:'Harpsicord',
        15360:'Drums',
        15488:'GM A',
        15489:'GM B',
        15490:'GM C',
        15491:'GM D',
        15492:'GM E',
        15492:'Effect A',
        15493:'Effect B',
        15494:'Effect C',
        15494:'Effect D',
        15495:'Effect E',
        15496:'Effect F',
        15497:'Effect G'
        }

    if bankid in names:
        return names[bankid]

    return f'Bank#{bankid}'

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

print(';')
print('; Cakewalk Instrument definition file for the Roland HP603')
print('; Mike Choi, Oct 2019')
print(';\n')
print('.Patch Names')

for k, v in banks.items():
    print(f'\n[{get_bank_name(banks, k)}]')
    for vv in v:
        print(f'{vv[1]}={vv[0]}')

print('\n\n')
print('.Instrument Definitions\n')
print('[Roland HP603]')
for k, v in banks.items():
    print(f'Patch[{k}]={get_bank_name(banks, k)}')

