import json
import tomli
from pathlib import Path
import re
from rich import print

fr = Path("data/yamaha-clp685-data.txt")
fw = Path("data/yamaha-clp685-data.toml")

rfd = open(fr, "rt", encoding='utf-8')
wfd = open(fw, "wt", encoding='utf-8')
array_header = None
subarray_header = None
wdata = []

for line in rfd.readlines():
    # print(line.strip())
    rline = line.strip()
    if len(rline) == 0 or rline[0] == '#':
        wdata.append(rline+'\n')
        continue
    m = re.match(r'^\[([^\[]+)\]$', rline)
    if m:
        array_header = m.groups(1)[0]
        continue
    m = re.search(r'^\[\[(.+)\]\]$', rline)
    if m:
        subarray_header = m.groups(1)[0]
        continue
    
    tokens = line.strip().split()
    n = len(tokens)
    l = []
    l.insert(0, f'prog={tokens.pop()}')
    l.insert(0, f'lsb={tokens.pop()}')
    l.insert(0, f'msb={tokens.pop()}')
    l.insert(0, f'name=\"{" ".join(tokens)}\"')
    s = '[["{}"."{}"]]\n{}\n'.format(array_header, subarray_header, '\n'.join(l))
    # s = subarray_header + '\n' + '\n'.join(l) + '\n'
    wdata.append(s)
    
wfd.writelines(wdata)
wfd.close()
rfd.close()

# check toml
data = tomli.loads(fw.read_text(encoding='utf-8'))
print(data)

json.dump(data, open(fw.with_suffix('.json'), 'wt', encoding='utf-8'), indent=2)