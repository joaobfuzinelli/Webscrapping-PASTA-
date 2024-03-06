import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time
import json
from urllib3.exceptions import InsecureRequestWarning
import pandas as pd

# Desativa os avisos relacionados à solicitação não segura
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def download_zip(url_to_check, headers):
    try:
        response = requests.get(url_to_check, headers=headers, verify=False, stream=True)
        response.raise_for_status()  # Verifica se houve algum erro na resposta

        # Extrai o nome do arquivo do URL
        filename = url_to_check.split("/")[-1]

        # Define o caminho local para salvar o arquivo
        local_path = os.path.join("downloads", filename)

        # Cria o diretório de downloads, se não existir
        os.makedirs("downloads", exist_ok=True)

        # Salva o conteúdo do arquivo ZIP localmente
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        print(f"Arquivo baixado com sucesso: {local_path}")

        # Retorna o caminho local do arquivo ZIP baixado
        return local_path

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para {url_to_check}: {e}")
        return None

def extract_links(url_to_check, headers, keyword="Dados_abertos_Nao_Previdenciario"):
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
            if keyword in href:
                links.append(urljoin(url_to_check, href))

        return links
    else:
        return []

def read_excel_to_dict(file_path):
    # Utiliza pandas para ler o arquivo Excel e retorna um dicionário
    df = pd.read_excel(file_path)
    return df.to_dict(orient='records')

if __name__ == "__main__":
    with open('config.json') as f:
        dados_arquivo = json.load(f)

    base_url = dados_arquivo['url']
    url_list = [base_url]
    headers = dados_arquivo['headers']

    # Conjunto para armazenar as URLs já verificadas
    checked_urls = set()

    # Dicionário consolidado para armazenar todos os dados
    consolidated_data = {}

    try:
        while True:
            novas_pastas = set()

            for url_to_check in url_list:
                novas_pastas.update(extract_links(url_to_check, headers))

            links_adicionados = novas_pastas - set(url_list)

            if links_adicionados:
                print("Novas pastas adicionadas:")
                for link_adicionado in links_adicionados:
                    url_list.append(link_adicionado)
                    print(link_adicionado)

            for url_to_check in links_adicionados:
                try:
                    zip_path = download_zip(url_to_check, headers)

                    if zip_path:
                        # Lê todas as planilhas Excel dentro do arquivo ZIP
                        with pd.ExcelFile(zip_path) as xls:
                            for sheet_name in xls.sheet_names:
                                df_data = read_excel_to_dict(xls.parse(sheet_name))

                                # Adiciona os dados ao dicionário consolidado
                                if sheet_name not in consolidated_data:
                                    consolidated_data[sheet_name] = []

                                consolidated_data[sheet_name].extend(df_data)

                except requests.exceptions.RequestException as e:
                    print(f"Erro na requisição: {e}")

            # Aguardar antes da próxima verificação (por exemplo, 1 hora)
            time.sleep(3600)

    except KeyboardInterrupt:
        print("Script interrompido manualmente.")
