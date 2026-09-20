import collections
import sys

import toml

# Cakewalk is a Windows application and reads these files as CRLF.
# Pin it here so regenerating on Linux does not produce a whole-file diff.
sys.stdout.reconfigure(newline='\r\n')


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
        return f'Bank#{self.bank_id}'

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
print('; Cakewalk Instrument definition file for the Yamaha CLP-685')
print('; Mike Choi')
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
