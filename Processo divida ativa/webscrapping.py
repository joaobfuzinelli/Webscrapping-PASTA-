import os
import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

# Desativa os avisos relacionados à solicitação não segura
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def download_zip(url_to_check, headers, extract_folder):
    try:
        response = requests.get(url_to_check, headers=headers, verify=False, stream=True)
        response.raise_for_status()  # Verifica se houve algum erro na resposta

        # Extrai o nome do arquivo do URL
        filename = url_to_check.split("/")[-1]

        # Gera um nome de arquivo único para evitar substituições
        base_name, extension = os.path.splitext(filename)
        count = 1
        while os.path.exists(os.path.join(extract_folder, filename)):
            filename = f"{base_name}_{count}{extension}"
            count += 1

        # Define o caminho local para salvar o arquivo ZIP
        local_path = os.path.join(extract_folder, filename)

        # Cria o diretório de downloads, se não existir
        os.makedirs(extract_folder, exist_ok=True)

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

def get_zip_urls(base_url, headers, folder):
    url_to_check = urljoin(base_url, folder)
    response = requests.get(url_to_check, headers=headers, verify=False)
    response.raise_for_status()  # Verifica se houve algum erro na resposta

    soup = BeautifulSoup(response.text, 'html.parser')
    zip_urls = []

    # Padrões desejados na nomenclatura dos arquivos ZIP
    desired_patterns = [
        r"Dados_abertos_Nao_Previdenciario\.zip",
        r"Dados_abertos_Nao_Previdenciario[^/]+\.zip",  # Trata erros de digitação
    ]

    for a in soup.find_all('a', href=True):
        href = a['href']
        for pattern in desired_patterns:
            if re.search(pattern, href) and "Portal_da_Cidadania_Tributaria" not in href:
                zip_urls.append(urljoin(url_to_check, href))

    return zip_urls

def get_trimestre_folders(base_url, headers):
    response = requests.get(base_url, headers=headers, verify=False)
    response.raise_for_status()  # Verifica se houve algum erro na resposta

    soup = BeautifulSoup(response.text, 'html.parser')
    trimestre_folders = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('/')]

    return trimestre_folders

if __name__ == "__main__":
    with open('config.json') as f:
        dados_arquivo = json.load(f)

    base_url = dados_arquivo['url']
    headers = dados_arquivo['headers']

    # Caminho para a área de trabalho do usuário
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

    # Pasta onde os arquivos serão salvos na área de trabalho
    extract_folder = os.path.join(desktop_path, 'Automação Web Scrapping', 'Downloads')

    trimestre_folders = get_trimestre_folders(base_url, headers)

    for trimestre_folder in trimestre_folders:
        zip_urls = get_zip_urls(base_url, headers, trimestre_folder)

        for zip_url in zip_urls:
            download_zip(zip_url, headers, extract_folder)

    print("Downloads concluídos. Arquivos salvos em 'Automação Web Scrapping/Downloads' na área de trabalho.")
