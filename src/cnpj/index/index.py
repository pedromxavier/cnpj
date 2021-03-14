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

ENDL = '\n'.encode('utf-8')
BLOCK_SIZE = 1200
FILE_INDEX = tuple(range(1, 21))

def read_block(file) -> (str, bytes):
    global BLOCK_SIZE
    block = file.read(BLOCK_SIZE).decode('utf-8')
    s = file.read(1) ## sep
    return (block, s)

def read_entry(file, ifile, seek:int, i: int) -> (dict, bool):
    global T_HEADER, T_ENTERP, T_PERSON, T_CNAESC, T_TRAILL, ENDL

    block, s = read_block(file)

    # Entry Type
    c = sys.intern(block[0])

    if c is T_HEADER:
        return None if not s else False
    elif c is T_ENTERP:
        return read_enterp(block, ifile, seek=seek, i=i)
    elif c is T_PERSON:
        return None if not s else False
    elif c is T_CNAESC:
        return None if not s else False
    elif c is T_TRAILL:
        return None if not s else False
    elif not c:
        return None
    else:
        raise ReadError(f"Invalid char <{c} @ {file.tell()}>")

def read_header(block: str):
    # Discard content
    return False

def read_enterp(block, ifile, seek: int, i: int=0) -> bool:
    # Get initial position
    ifile.write(f"{block[3:17]}{i:02d}{seek:024d}".encode('utf-8'))
    return True
    
def index(args: argparse.Namespace):
    global FILE_INDEX, PATH

    size = 0
    code = None
    with open_local('cnpj.index', path=args.path, mode='wb') as ifile:
        # Reserve space for header BLOCK = 40 bytes
        ifile.write(f"{size:040d}".encode('utf-8'))

        for i in FILE_INDEX:

            fname = PATH.format(i)
            print(f"Indexing <{fname}>", end='\r')
    
            with open_local(fname, path=args.path, mode='rb') as file:
                # We don't know the actual size for all contents.
                while True:
                    try:
                        code = read_entry(file, ifile, file.tell(), i)
                    except ReadError as error:
                        print(f"ReadError: {error.msg}")
                        return

                    if code is None:
                        break
                    elif code is True:
                        size += 1
                    elif code is False:
                        continue
        else:
            ifile.seek(0)
            ifile.write(f"{size:040d}".encode('utf-8'))

    print("All files indexed." + " " * 40)

    print("Sorting Index")
    with open_local('cnpj.index', path=args.path, mode='rb') as ifile:
        size = int(ifile.read(40).decode('utf-8'))
        data = b''.join(sorted((ifile.read(40) for _ in range(size))))

    with open_local('cnpj.index', path=args.path, mode='wb') as ifile:
        ifile.write(f"{size:040d}".encode('utf-8'))
        ifile.write(data)

    print("Finished indexing data.")