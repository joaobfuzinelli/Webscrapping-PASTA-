import zipfile
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib3.exceptions import InsecureRequestWarning
import time
import sqlite3
import json

# Desativar os avisos relacionados à solicitação não segura
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def download_zip(url_to_check, headers, download_folder):
    try:
        response = requests.get(url_to_check, headers=headers, verify=False)
        response.raise_for_status()  # Verifica se houve algum erro na resposta
    except requests.exceptions.RequestException as e:
        print(f"Falha na requisição para {url_to_check}: {e}")
        return

    if response.status_code == 200:
        # Obtém o nome do arquivo do cabeçalho de resposta
        content_disposition = response.headers.get('content-disposition')
        if content_disposition and 'attachment' in content_disposition:
            filename = content_disposition.split("filename=")[1].strip('";')
        else:
            # Se o cabeçalho de resposta não contiver o nome do arquivo, gera um nome com base na URL
            filename = os.path.basename(url_to_check)

        # Caminho completo para salvar o arquivo ZIP
        file_path = os.path.join(download_folder, filename)

        # Salva o arquivo ZIP
        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"Arquivo ZIP baixado: {file_path}")
    else:
        print(f"Falha ao baixar o arquivo ZIP. Status code: {response.status_code}")

def extract_links(url_to_check, headers):
    # Código para extrair links de uma página web
    pass

def fix_url(base_url, url):
    # Adicione aqui o código para corrigir URLs, se necessário
    return urljoin(base_url, url)

def create_table_if_not_exists(connection):
    # Cria a tabela se ela não existir
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_tabela (
            Coluna1 TEXT,
            Coluna2 INTEGER,
            Coluna3 TEXT
        )
    ''')
    connection.commit()

def insert_data_into_table(connection, data):
    # Insere os dados na tabela
    cursor = connection.cursor()
    cursor.executemany('INSERT INTO dados_tabela (Coluna1, Coluna2, Coluna3) VALUES (?, ?, ?)', data)
    connection.commit()

def read_config_from_json(file_path='config.json'):
    # Leitura das configurações do JSON
    with open(file_path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    # Leitura das configurações do JSON
    config = read_config_from_json()

    # Conexão com o banco de dados
    if config['database']['type'] == 'sqlite':
        db_connection = sqlite3.connect(config['database']['name'])
    else:
        # Adapte aqui para outros tipos de banco de dados
        pass

    # Garante que a pasta de download exista ou cria se não existir
    os.makedirs(config['download_folder'], exist_ok=True)

    try:
        while True:
            novas_pastas = set()

            for url_to_check in url_list:
                novas_pastas.update(extract_links(url_to_check, config['headers']))

            links_adicionados = novas_pastas - set(url_list)

            if links_adicionados:
                print("Novas pastas adicionadas:")
                for link_adicionado in links_adicionados:
                    full_url = fix_url(config['url'], link_adicionado)
                    url_list.append(full_url)
                    print(full_url)

                    # Extraia e salve o conteúdo do arquivo ZIP
                    download_zip(full_url, config['headers'], config['download_folder'])

                    # Leitura do arquivo Excel e inserção no banco de dados
                    excel_df = pd.read_excel(os.path.join(config['extract_folder'], "Dados_abertos_Nao_Previdenciario.xlsx"))
                    data_to_insert = [tuple(row) for row in excel_df.values]
                    create_table_if_not_exists(db_connection)
                    insert_data_into_table(db_connection, data_to_insert)

            # Aguarde antes da próxima verificação (por exemplo, 1 hora)
            time.sleep(3600)

    except KeyboardInterrupt:
        print("Script interrompido manualmente.")

    # Fecha a conexão com o banco de dados após a conclusão
    db_connection.close()
