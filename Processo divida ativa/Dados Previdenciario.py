import os
import shutil
import pandas as pd
from zipfile import ZipFile
from rarfile import RarFile
from pathlib import Path

def obter_caminho_pasta():
    caminho_pasta = input("Digite o caminho da pasta contendo os arquivos ZIP e RAR: ").strip()
    return Path(caminho_pasta)

def extrair_zip_ou_rar(arquivo, pasta_destino):
    try:
        if arquivo.suffix == ".zip":
            with ZipFile(arquivo, 'r') as zip_ref:
                zip_ref.extractall(pasta_destino)
        elif arquivo.suffix == ".rar":
            with RarFile(arquivo, 'r') as rar_ref:
                rar_ref.extractall(pasta_destino)
        print(f"Arquivo {arquivo.name} extraído para {pasta_destino}")
    except Exception as e:
        print(f"Erro ao extrair {arquivo.name}: {e}")

def processar_arquivos_zip_ou_rar(pasta_origem, pasta_destino):
    for arquivo in pasta_origem.iterdir():
        if arquivo.is_file() and arquivo.suffix in (".zip", ".rar"):
            extrair_zip_ou_rar(arquivo, pasta_destino)

def processar_arquivos_excel(pasta):
    dataframes = []
    for arquivo_excel in pasta.rglob("*.xls*"):
        try:
            df = pd.read_excel(arquivo_excel)
            dataframes.append(df)
            print(f"Arquivo Excel lido: {arquivo_excel}")
            print(f"Número de linhas: {len(df)}")
            print(f"Colunas: {df.columns.tolist()}")
        except Exception as e:
            print(f"Erro ao ler {arquivo_excel}: {e}")

    if dataframes:
        df_consolidado = pd.concat(dataframes, ignore_index=True)
        return df_consolidado
    else:
        return None

def main():
    caminho_pasta = obter_caminho_pasta()
    pasta_temporaria = caminho_pasta / "Extrair/Conteudo/temp"

    # Cria a pasta temporária se não existir
    pasta_temporaria.mkdir(parents=True, exist_ok=True)

    try:
        processar_arquivos_zip_ou_rar(caminho_pasta, pasta_temporaria)

        df_consolidado = processar_arquivos_excel(pasta_temporaria)

        if df_consolidado is not None:
            # Agora você pode trabalhar com o DataFrame consolidado
            # (df_consolidado) como desejar.
            # Aqui, por exemplo, estou mostrando as primeiras linhas:
            print("Dicionário Consolidado:")
            print(df_consolidado.head())
    finally:
        # Adicione uma mensagem informando que a pasta temporária não será removida
        print("A pasta temporária não será removida após o processamento.")

if __name__ == "__main__":
    main()
