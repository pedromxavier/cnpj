import os
import re
import sys
import json
import math
import argparse

from ..cnpjlib import open_local, ENCODING

RE_CNPJ = re.compile(r"([0-9]{2})\.([0-9]{3})\.([0-9]{3})\/([0-9]{4})\-([0-9]{2})")

PATH = r"K3241.K032001K.CNPJ.D01120.L000{:02d}"

T_HEADER = sys.intern("0")
T_ENTERP = sys.intern("1")
T_PERSON = sys.intern("2")
T_CNAESC = sys.intern("6")
T_TRAILL = sys.intern("9")


def find(ifile, keys: set, algorithm: str = "bisect") -> list:
    size = int(ifile.read(40).decode(ENCODING))
    if algorithm == "bisect":
        print("Running bisection Algorithm on seek...")
        return list(bisect(ifile, 1, size, keys))
    elif algorithm == "naive":
        print("Running naïve Algorithm on seek...")
        return list(naive(ifile, 1, size, keys))
    else:
        raise NameError(f"Unknown algorithm {algorithm}.")


def table(ifile, i: int) -> str:
    ifile.seek(40 * i)
    return ifile.read(14).decode(ENCODING)


def naive(ifile, i: int, n: int, keys: set):
    missing = keys.copy()
    for j in range(i, n + 1):
        key = table(ifile, j)
        if key in missing:
            missing.remove(key)
            yield (j, True)
    else:
        for key in missing:
            yield (key, False)


def bisect(ifile, i: int, k: int, keys: set):
    if i >= k:
        return

    j: int = math.floor((i + k) / 2)

    key_i: str = table(ifile, i)
    key_j: str = table(ifile, j)
    key_k: str = table(ifile, k)

    if (k - i) == 1:
        for key in keys:
            if key == key_i:
                yield (i, True)
            elif key == key_j:
                yield (j, True)
            elif key == key_k:
                yield (k, True)
            else:
                yield (key, False)
    else:
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

        if keys_i:
            yield from bisect(ifile, i, j, keys_i)
        if keys_k:
            yield from bisect(ifile, j, k, keys_k)


def retrieve(ifile, indices: list):
    global PATH
    global T_CNAESC, T_ENTERP, T_HEADER, T_PERSON, T_TRAILL

    found = {}
    missing = []
    for item, code in indices:
        if not code:
            missing.append(item)
        else:
            ifile.seek(40 * item)
            info = ifile.read(40).decode(ENCODING)

            cnpj = info[0:14]
            fidx = info[14:16]
            seek = info[16:40]

            path = PATH.format(int(fidx))

            with open(path, "rb") as file:
                file.seek(int(seek))
                main_block = file.read(1200).decode(ENCODING)

                blocks = []
                while True:
                    # skip
                    s = file.read(1).decode(ENCODING)
                    if s == "\n" or s == "":
                        block = file.read(1200).decode(ENCODING)
                    else:
                        raise ValueError(f"Invalid sep <{s}>")

                    c = sys.intern(block[0])
                    if c is T_ENTERP or c is T_HEADER or c is T_TRAILL:
                        break
                    elif c is T_PERSON:
                        pass
                    elif c is T_CNAESC:
                        blocks.append(block)

                    if s == "":
                        break

            found[cnpj] = {**read_block(main_block), **read_blocks(blocks)}

    return {"found": found, "missing": missing}


def read_block(block: str):
    return {
        "cnpj": block[3:17],
        "matriz": (block[17] == "1"),
        "nome": block[18:168].rstrip(" \n\t"),
        "fantasia": block[168:223].rstrip(" \n\t"),
        "cnae": block[375:382].rstrip(" \n\t"),
        "cep": block[674:682].rstrip(" \n\t"),
    }


def read_blocks(blocks: list):
    cnaes = []
    for block in blocks:
        for i in range(17, 710, 7):
            cnae = block[i : i + 7]
            if cnae == "0000000":
                continue
            else:
                cnaes.append(cnae)
    return {"cnaesec": cnaes}


def seek(args: argparse.Namespace):
    global RE_CNPJ

    keys = set()

    with open(args.file, "r") as file:
        for line in file:
            s = line.rstrip(" \n\t")
            if RE_CNPJ.match(s) is None:
                continue
            else:
                keys.add(RE_CNPJ.sub(r"\1\2\3\4\5", s))

    if not keys:
        return
    else:
        print(f"Searching for {len(keys)} keys.")

    with open_local("cnpj.index", path=args.path, mode="rb") as ifile:
        data = retrieve(ifile, find(ifile, keys, algorithm=args.algorithm))

    fname, *_ = os.path.splitext(os.path.basename(args.file))

    print(f"Writing seek results to {fname}.json")

    with open(f"{fname}.json", "w") as jfile:
        json.dump(data, jfile)