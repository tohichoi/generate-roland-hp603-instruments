import collections

import toml


def get_bank_name(banks, bankid):
    # bank texts are subjectively named.
    names = {
        68: 'Piano A',
        2115: 'Piano B',
        576: 'Piano C',
        1090: 'Piano & Orch',
        69: 'Piano D',
        67: 'Piano E',
        70: 'EP & Organ',
        1092: 'Belle',
        3137: 'EP A',
        2114: 'EP B',
        1094: 'Organ A',
        66: 'Organ B',
        1093: 'Organ C',
        71: 'Organ & Strings',
        4164: 'Bars',
        4165: 'Organ D',
        2112: 'Organ & Piano',
        195: 'Orchestra A',
        64: 'Orchestra B',
        0: 'Orchestra C',
        193: 'Orchestra D',
        194: 'Orchestra E',
        6081: 'Piano F',
        1088: 'Piano G',
        65: 'Jazz Scat',
        320: 'Piano H',
        320: 'Forte Piano A',
        321: 'Forte Piano B',
        322: 'Forte Piano C',
        1091: 'Harpsicord',
        15360: 'Drums',
        15488: 'GM A',
        15489: 'GM B',
        15490: 'GM C',
        15491: 'GM D',
        15492: 'GM E',
        15492: 'Effect A',
        15493: 'Effect B',
        15494: 'Effect C',
        15494: 'Effect D',
        15495: 'Effect E',
        15496: 'Effect F',
        15497: 'Effect G'
    }

    if bankid in names:
        return names[bankid]

    return f'Bank#{bankid}'


def get_banks(inst_name, data):
    for k, val in data.items():
        group = k
        for v in val:
            inst_info[group].append([v['msb'], v['lsb'], v['prog']])
    return inst_info


class Instrument:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.msb = kwargs.get('msb')
        self.lsb = kwargs.get('lsb')
        self.prog = kwargs.get('prog')

    @property
    def bank_id(self):
        return self.msb * 128 + self.lsb

    @property
    def bank_name(self):
        return f'Bank/{self.bank_id}'

    def __repr__(self):
        return f'Instrument(name={self.name}, msb={self.msb}, lsb={self.lsb}, prog={self.prog})'

    def __str__(self):
        return self.name


class InstrumentGroup:
    def __init__(self, name):
        self.name = name
        self.instruments = []

    def add_instrument(self, inst: Instrument):
        self.instruments.append(inst)

    def __repr__(self):
        return f'InstrumentGroup(name={self.name}, instruments={self.instruments})'

    def __str__(self):
        return self.name


class InstrumentCategory:
    def __init__(self, name):
        self.name = name
        self.groups = {}

    def add_instrument(self, group_name, inst: Instrument):
        if group_name not in self.groups:
            self.groups[group_name] = InstrumentGroup(group_name)
        self.groups[group_name].add_instrument(inst)

    def get_banks(self):
        banks = collections.defaultdict(list)
        for group in self.groups.values():
            for inst in group.instruments:
                banks[inst.bank_name].append(
                    {'category': self.name, 'group': group.name, 'inst': inst})
        for bank in banks:
            banks[bank].sort(key=lambda x: x['inst'].prog)
        return banks

    def __repr__(self):
        return f'InstrumentCategory(name={self.name}, groups={self.groups})'

    def __str__(self):
        return self.name


with open('data/yamaha-clp685-data.toml') as fd:
    data = toml.load(fd)

# cateogries['Preset Voices'].groups['Piano'].instruments[0].bankid
categories = dict()
for category, groups in data.items():
    categories[category] = InstrumentCategory(category)
    for group, insts in groups.items():
        for inst_info in insts:
            i = Instrument(**inst_info)
            categories[category].add_instrument(group, i)

print(';')
print('; Cakewalk Instrument definition file for the Roland HP603')
print('; Mike Choi, Oct 2019')
print(';\n')
print('.Patch Names')

for category_name, category in categories.items():
    banks = categories[category_name].get_banks()
    for bank_name, insts in banks.items():
        print(f'\n[{category_name}/{bank_name}]')
        for inst_info in insts:
            print(f"{inst_info['inst'].prog}={inst_info['inst'].name}")

print('\n\n')
print('.Instrument Definitions\n')
for category_name, category in categories.items():
    print('[Yamaha CLP-685 - {}]'.format(category_name))
    banks = categories[category_name].get_banks()
    for bank_name, insts in banks.items():
        print(f"Patch[{insts[0]['inst'].bank_id}]={category_name}/{insts[0]['inst'].bank_name}")
    print('\n\n')
