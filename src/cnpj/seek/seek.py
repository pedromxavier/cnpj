import os
import re
import json
import math
import argparse

from ..cnpjlib import open_local

RE_CNPJ = re.compile(r'([0-9]{2})\.([0-9]{3})\.([0-9]{3})\/([0-9]{4})\-([0-9]{2})')

PATH = r'K3241.K032001K.CNPJ.D01120.L000{:02d}'

def find(ifile, keys: set):
    size = int(ifile.read(40).decode('utf-8'))

    i = 1; j = (size + 1) // 2; k = size

    yield from bisect(ifile, i, j, k, keys)

def table(ifile, i: int):
    ifile.seek(40 * i)
    return ifile.read(40).decode('utf-8')

def bisect(ifile, i: int, j: int, k: int, keys: set):
    key_i: str = table(ifile, i)
    key_j: str = table(ifile, j)
    key_k: str = table(ifile, k)

    keys_i = set()
    keys_k = set()

    for key in keys:
        if key == key_i:
            yield (i, True)
        elif key == key_j:
            yield (j, True)
        elif key == key_k:
            yield (k, True)
        elif key_i < key < key_j:
            keys_i.add(key)
        elif key_j < key < key_k:
            keys_k.add(key)
        else:
            yield (key, False)

    if keys_i: yield from bisect(ifile, i, math.floor((i + j) / 2), j, keys_i)
    if keys_k: yield from bisect(ifile, j, math.ceil((j + k) / 2), k, keys_k)

def retrieve(ifile, indices: list):
    global PATH

    found = {}
    missing = []
    for item, code in indices:
        if not code:
            missing.append(item)
        else:
            ifile.seek(40 * item)
            info = ifile.read(40).decode('utf-8')

            cnpj = info[ 0:14]
            fidx = info[14:16]
            seek = info[16:40]

            path = PATH.format(int(fidx))

            with open(path, 'rb') as file:
                file.seek(int(seek))
                block = file.read(1200)

            found[cnpj] = read_block(block)

    return {
        'found': found,
        'missing': missing
    }

def read_block(block: bytes):
    info = block.decode('utf-8')
    return {
        'cnpj': info[3:17],
        'matriz': (info[17] == '1'),
        'nome': info[18:168],
        'fantasia': info[168:223],
        'cnae': info[375:382],
        'cep': info[674:682]
    }

def seek(args: argparse.Namespace):
    global RE_CNPJ

    keys = set()

    with open(args.file, 'r') as file:
        for line in file:
            s = line.rstrip('\n')
            if RE_CNPJ.match(s) is None:
                continue
            else:
                keys.add(RE_CNPJ.sub(r'\1\2\3\4\5', s))

    if not keys:
        return

    with open_local('cnpj.index', path=args.path, mode='rb') as ifile:
        data = retrieve(ifile, list(find(ifile, keys)))

    with open('cnpj.json', 'w') as jfile:
        json.dump(data, jfile)