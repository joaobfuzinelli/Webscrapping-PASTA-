import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import json
from urllib3.exceptions import InsecureRequestWarning

# Desativar os avisos relacionados à solicitação não segura
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def download_zip(url_to_check, headers):
    # O código para download do arquivo ZIP permanece o mesmo
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
    # Código para corrigir URLs, mantido igual ao original
    pass

if __name__ == "__main__":
    with open('config.json') as f: 
        dados_arquivo = json.load(f)

    base_url = dados_arquivo['url']
    url_list = [base_url]
    headers = dados_arquivo['headers']

    # Conjunto para armazenar as URLs já verificadas
    checked_urls = set()

    try:
        while True:
            novas_pastas = set()

            for url_to_check in url_list:
                novas_pastas.update(extract_links(url_to_check, headers))

            links_adicionados = novas_pastas - set(url_list)

            if links_adicionados:
                print("Novas pastas adicionadas:")
                for link_adicionado in links_adicionados:
                    full_url = fix_url(base_url, link_adicionado)
                    url_list.append(full_url)
                    print(full_url)

            for url_to_check in links_adicionados:
                try:
                    full_url = fix_url(base_url, url_to_check)
                    download_zip(full_url, headers)
                except requests.exceptions.RequestException as e:
                    print(f"Erro na requisição: {e}")

            # Aguardar antes da próxima verificação (por exemplo, 1 hora)
            time.sleep(3600)

    except KeyboardInterrupt:
        print("Script interrompido manualmente.")
