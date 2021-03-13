import argparse
import requests
import threading
import os

from ..cnpjlib import get_data_path

def download(i: int):
    base_url = r'200.152.38.155/CNPJ/DADOS_ABERTOS_CNPJ_{:02d}.zip'
    file_url = r'DADOS_ABERTOS_CNPJ_{:02d}.zip'

    answer = requests.get(base_url.format(i))

    f_path = os.path.join(get_data_path('', 'cnpj_data'), file_url.format(i))

    with open(f_path, 'wb') as file:
        file.write(answer.content)


def load(args: argparse.Namespace):
    threads = []

    for i in range(1, 21):
        thread = threading.Thread(target=download, args=(i,), kwargs={})
        thread.run()
        threads.append(thread)

    for thread in threads: thread.join()
