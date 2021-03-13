#!/usr/bin/env python3
import argparse

from .seek import seek
from .load import load
from .index import index

def main() -> int:
    params = {
            "description": __doc__
    }
    parser = argparse.ArgumentParser(**params)

    subparsers = parser.add_subparsers()

    seek_parser = subparsers.add_parser('seek')
    seek_parser.add_argument('file', type=str, action='store', help="Arquivo contendo os CNPJ's desejados.")
    seek_parser.add_argument('-p', '--path', dest='past', type=str, action='store')
    seek_parser.set_defaults(func=seek)

    load_parser = subparsers.add_parser('load')
    load_parser.add_argument('-p', '--path', dest='past', type=str, action='store')
    load_parser.set_defaults(func=load)

    index_parser = subparsers.add_parser('index')
    index_parser.add_argument('-p', '--path', dest='past', type=str, action='store')
    index_parser.set_defaults(func=index)

    args = parser.parse_args()
    args.func(args)

    return 0

if __name__ == '__main__':
    exit(main())