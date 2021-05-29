#!/usr/bin/env python3
"""
"""
import argparse

from .seek import seek
from .load import load
from .index import index
from .table import table


def main() -> int:
    params = {"description": __doc__}
    parser = argparse.ArgumentParser(**params)
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers()

    seek_parser = subparsers.add_parser("seek")
    seek_parser.add_argument(
        "file", type=str, action="store", help="Arquivo contendo os CNPJ's desejados."
    )
    seek_parser.add_argument("-p", "--path", dest="path", type=str, action="store")
    seek_parser.add_argument(
        "-a", "--algorithm", dest="algorithm", type=str, action="store"
    )
    seek_parser.set_defaults(func=seek, algorithm="bisect")

    load_parser = subparsers.add_parser("load")
    load_parser.add_argument("-p", "--path", dest="path", type=str, action="store")
    load_parser.set_defaults(func=load)

    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("-p", "--path", dest="path", type=str, action="store")
    index_parser.set_defaults(func=index)

    table_parser = subparsers.add_parser("table")
    table_parser.add_argument("file", type=str, action="store", help="Arquivo JSON.")
    table_parser.add_argument(
        "--format", dest="cnpj_format", action="store_true", help="Formatar cnpj."
    )
    table_parser.set_defaults(func=table)

    args = parser.parse_args()
    if args.func is not None:
        args.func(args)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    exit(main())
