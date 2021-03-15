import os
import csv
import json
import argparse


def table(args: argparse.Namespace):
    with open(args.file, "r") as jfile:
        data: dict = json.load(jfile)

    fname, *_ = os.path.splitext(os.path.basename(args.file))

    with open(f"{fname}.csv", "w") as cfile:
        fields = ["cnpj", "matriz", "nome", "fantasia", "cnae", "cep", "cnaesec"]
        writer = csv.DictWriter(cfile, fields)

        for entry in data["found"]:
            writer.writerow(
                {
                    "cnpj": entry["cnpj"],
                    "matriz": "S" if entry["matriz"] else "N",
                    "nome": entry["nome"],
                    "fantasia": entry["fantasia"],
                    "cnae": entry["cnae"],
                    "cep": entry["cep"],
                    "cnaesec": ";".join(entry["cnaesec"]),
                }
            )

        for cnpj in data["missing"]:
            writer.writerow(
                {
                    "cnpj": cnpj,
                    "matriz": "",
                    "nome": "",
                    "fantasia": "",
                    "cnae": "",
                    "cep": "",
                    "cnaesec": "",
                }
            )
