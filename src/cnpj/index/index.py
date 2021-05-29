#!/usr/bin/env python3
import sys
import os
import re
import time
import argparse

from tqdm import tqdm

# RE_CNPJ = re.compile(r'([0-9]{2})\.([0-9]{3})\.([0-9]{3})\/([0-9]{4})\-([0-9]{2})')

from ..cnpjlib import open_local, ENCODING


class ReadError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg


PATH = r"K3241.K032001K.CNPJ.D01120.L000{:02d}"

T_HEADER = sys.intern("0")
T_ENTERP = sys.intern("1")
T_PERSON = sys.intern("2")
T_CNAESC = sys.intern("6")
T_TRAILL = sys.intern("9")

ENDL = sys.intern("\n")

FILE_INDEX = tuple(range(1, 21))


def read_entry(file, ifile, i: int):
    global T_HEADER, T_ENTERP, T_PERSON, T_CNAESC, T_TRAILL, ENDL
    # Entry Type
    c = sys.intern(file.read(1).decode(ENCODING))

    if c is T_HEADER:
        code = read_header(file)
    elif c is T_ENTERP:
        code = read_enterp(file, ifile, i)
    elif c is T_PERSON:
        code = read_header(file)
    elif c is T_CNAESC:
        code = read_header(file)
    elif c is T_TRAILL:
        code = read_header(file)
    elif not c:
        return None
    else:
        raise ReadError(f"Invalid char <{c} @ {file.tell()}>")

    c = sys.intern(file.read(1).decode(ENCODING))

    if not c:  # trailing endl or EOF
        return None
    elif c is not ENDL:
        raise ReadError(f"Invalid endl <{c}> @ {file.tell()}")
    else:
        return code


def read_header(file):
    # Discard content
    file.seek(1199, os.SEEK_CUR)
    return False


def read_enterp(file, ifile, i: int = 0) -> bool:
    # Get initial position
    seek = file.tell() - 1

    # Discard some things
    file.seek(2, os.SEEK_CUR)

    cnpj = file.read(14).decode(ENCODING)

    ifile.write(f"{cnpj}{i:02d}{seek:024d}".encode(ENCODING))

    # Discard some things
    file.seek(1183, os.SEEK_CUR)

    return True


def index(args: argparse.Namespace):
    global FILE_INDEX, PATH

    code = None
    size = 0
    with open_local("cnpj.index", path=args.path, mode="wb") as ifile:
        ifile.write(f"{size:040d}".encode(ENCODING))
        for i in tqdm(FILE_INDEX, desc="Indexing"):
            fname = PATH.format(i)
            with open_local(fname, path=args.path, mode="rb") as file:
                while True:
                    try:
                        code = read_entry(file, ifile, i)
                    except ReadError as error:
                        print(f"ReadError: {error.msg}")
                        return
                    else:
                        if code is None:
                            break
                        elif code is True:
                            size += 1
                        else:
                            continue
        else:
            ifile.seek(0)
            ifile.write(f"{size:040d}".encode(ENCODING))
    print("All files indexed." + " " * 40)

    print("Sorting Index")
    with open_local("cnpj.index", path=args.path, mode="rb") as ifile:
        size = int(ifile.read(40).decode(ENCODING))
        data = b"".join(sorted((ifile.read(40) for _ in range(size))))

    with open_local("cnpj.index", path=args.path, mode="wb") as ifile:
        ifile.write(f"{size:040d}".encode(ENCODING))
        ifile.write(data)
    print("Finished indexing data.")