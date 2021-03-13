#!/usr/bin/env python3
import sys
import os
import re
import time
import argparse

# RE_CNPJ = re.compile(r'([0-9]{2})\.([0-9]{3})\.([0-9]{3})\/([0-9]{4})\-([0-9]{2})')

from ..cnpjlib import open_local

class ReadError(Exception):
    
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

PATH = r'K3241.K032001K.CNPJ.D01120.L000{:02d}'

T_HEADER = sys.intern('0')
T_ENTERP = sys.intern('1')
T_PERSON = sys.intern('2')
T_CNAESC = sys.intern('6')
T_TRAILL = sys.intern('9')

ENDL = sys.intern('\n')

FILE_INDEX = tuple(range(1, 21))

def read_entry(file, ifile, i: int) -> (dict, bool):
    global T_HEADER, T_ENTERP, T_PERSON, T_CNAESC, T_TRAILL, ENDL
    # Entry Type
    c = sys.intern(file.read(1).decode('utf-8'))

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

    c = sys.intern(file.read(1).decode('utf-8'))

    if not c: # trailing endl or EOF
        return None
    elif c is not ENDL:
        raise ReadError(f"Invalid endl <{c}> @ {file.tell()}")
    else:
        return code

def read_header(file):
    # Discard content
    file.seek(1199, os.SEEK_CUR)
    return False

def read_enterp(file, ifile, i: int=0) -> bool:
    # Here things get intersting
    
    # Discard some things
    file.seek(3, os.SEEK_CUR)

    cnpj = sys.intern(file.read(14).decode('utf-8'))

    ifile.write(f"{cnpj}{i:02d}{file.tell() - 17:024d}".encode('utf-8'))

    # Discard some things
    file.seek(1182, os.SEEK_CUR)

    return True


    
def index(args: argparse.Namespace):
    global FILE_INDEX, PATH

    code = None
    size = 0
    with open_local('cnpj.index', path=args.path, mode='wb') as ifile:
        ifile.write(f"{size:040d}".encode('utf-8'))
        for i in FILE_INDEX:
            fname = PATH.format(i)
            print(f"Reading <{fname}>")
            with open_local(fname, path=args.path, mode='rb') as file:
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
            ifile.write(f"{size:040d}".encode('utf-8'))
