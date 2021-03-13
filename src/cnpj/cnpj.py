#!/usr/bin/env python3
import sys
import os
import re
import time
import argparse

RE_CNPJ = re.compile(r'([0-9]{2})\.([0-9]{3})\.([0-9]{3})\/([0-9]{4})\-([0-9]{2})')


class CNPJ_READER:

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

    @classmethod
    def read_entry(cls, file) -> (dict, bool):
        # Entry Type
        c = sys.intern(file.read(1).decode('utf-8'))

        if c is cls.T_HEADER:
            data, code = cls.read_header(file)
        elif c is cls.T_ENTERP:
            data, code = cls.read_enterp(file)
        elif c is cls.T_PERSON:
            data, code = cls.read_person(file)
        elif c is cls.T_CNAESC:
            data, code = cls.read_header(file)
        elif c is cls.T_TRAILL:
            data, code = cls.read_header(file)
        elif not c:
            return (None, None)
        else:
            raise cls.ReadError(f"Invalid char <{c} @ {file.tell()}>")

        c = sys.intern(file.read(1).decode('utf-8'))

        if not c: # trailing endl or EOF
            return (data, None)
        elif c is not cls.ENDL:
            raise cls.ReadError(f"Invalid endl <{c}> @ {file.tell()}")
        else:
            return (data, code)

    @classmethod
    def read_header(cls, file):
        # Discard content
        file.seek(1199, os.SEEK_CUR)
        return (None, False)

    @classmethod
    def read_enterp(cls, file) -> (dict, bool):
        # Here things get intersting
        
        # Discard some things
        file.seek(3, os.SEEK_CUR)

        cnpj = sys.intern(file.read(14).decode('utf-8'))

        cls.index.write(f"{cnpj}\t{cls.findex}\t{file.tell() - 17}\n")

        file.seek(1182, os.SEEK_CUR)
        return (None, False)

    @classmethod
    def write_data(cls, data):
        if data is None:
            return
        else:
            return

    @classmethod
    def read_person(cls, file) -> (dict, bool):
        # Discard too
        file.seek(1199, os.SEEK_CUR)
        return (None, False)

    @classmethod
    def cli(cls) -> argparse.Namespace:
        params = {
            "description": __doc__
        }
        parser = argparse.ArgumentParser(**params)
    
        parser.add_argument('file', type=str, action='store', help="Arquivo contendo os CNPJ's desejados.")
    
        args = parser.parse_args()

        return args

    @classmethod
    def main(cls):
        args = cls.cli()

        cls.keys = set()

        with open(args.file, 'r') as file:
            for line in file:
                s =  line.rstrip('\n')
                if RE_CNPJ.match(s) is None:
                    continue
                else:
                    cls.keys.add(RE_CNPJ.sub(r'\1\2\3\4\5', s))

        code = None

        with open('cnpj.index', 'w') as index:
            cls.index = index

            for i in cls.FILE_INDEX:
                cls.findex = i
                fname = cls.PATH.format(cls.findex)
                print(f"Reading <{fname}>")
                with open(fname, 'rb') as file:
                    while True:
                        try:
                            data, code = cls.read_entry(file)
                        except cls.ReadError as error:
                            print(f"ReadError: {error.msg}")
                            return
                        else:
                            if code is True:
                                cls.write_data(data)
                            elif code is False:
                                continue
                            elif code is None:
                                break
                            else:
                                print(f"Invalid code <{code}>.")
                                return

        

if __name__ == '__main__':
    CNPJ_READER.main()
