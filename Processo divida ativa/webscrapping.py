import zipfile
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib3.exceptions import InsecureRequestWarning
import time
import sqlite3

# Desativar os avisos relacionados à solicitação não segura
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def download_zip(url_to_check, headers):
    # Adicione aqui o código para baixar o arquivo ZIP
    pass

def extract_links(url_to_check, headers):
    try:
        response = requests.get(url_to_check, headers=headers, verify=False)
        response.raise_for_status()  # Verifica se houve algum erro na resposta
    except requests.exceptions.RequestException as e:
        print(f"Falha na requisição para {url_to_check}: {e}")
        return []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'Dados_abertos_Nao_Previdenciario.zip' in href:
                links.append(href)

        return links
    else:
        return []

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

def read_config_from_json():
    # Leitura das configurações do JSON
    return {
        "zip_filename": "Caminho/Para/Dados_abertos_Nao_Previdenciario.zip",
        "extract_folder": "Caminho/Para/Extrair/Conteudo",
        "url": "https://dadosabertos.pgfn.gov.br/",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        },
        "database": {
            "type": "sqlite",
            "name": "banco_ficticio.db"
        }
    }

if __name__ == "__main__":
    # Leitura das configurações do JSON
    config = read_config_from_json()

    # Conexão com o banco de dados
    if config['database']['type'] == 'sqlite':
        db_connection = sqlite3.connect(config['database']['name'])
    else:
        # Adapte aqui para outros tipos de banco de dados
        pass

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
                    download_zip(full_url, config['headers'])

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
