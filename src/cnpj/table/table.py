import os
import csv
import json
import argparse

def excel_str(s: object):
    return f'="{s}"'

def cnpj_str(s: object, cnpj: bool=True):
    if cnpj:
        return r"{0}{1}.{2}{3}{4}.{5}{6}{7}/{8}{9}{10}{11}-{12}{13}".format(*s)
    else:
        return excel_str(s)

def table(args: argparse.Namespace):
    with open(args.file, "r") as jfile:
        data: dict = json.load(jfile)

    fname, *_ = os.path.splitext(os.path.basename(args.file))

    with open(f"{fname}.csv", "w") as cfile:
        fields = ["cnpj", "matriz", "nome", "fantasia", "cnae", "cep", "cnaesec"]
        writer = csv.DictWriter(cfile, fields)
        writer.writeheader()

        for key in data["found"]:
            entry = data["found"][key]
            writer.writerow(
                {
                    "cnpj": cnpj_str(entry["cnpj"], cnpj=args.cnpj_format),
                    "matriz": "S" if entry["matriz"] else "N",
                    "nome": excel_str(entry["nome"]),
                    "fantasia": excel_str(entry["fantasia"]),
                    "cnae": excel_str(entry["cnae"]),
                    "cep": excel_str(entry["cep"]),
                    "cnaesec": excel_str(";".join(entry["cnaesec"])),
                }
            )

        for cnpj in data["missing"]:
            writer.writerow(
                {
                    "cnpj": excel_str(cnpj),
                    "matriz": "",
                    "nome": "",
                    "fantasia": "",
                    "cnae": "",
                    "cep": "",
                    "cnaesec": "",
                }
            )
