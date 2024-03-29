import os
import pandas as pd
from pathlib import Path

def obter_caminho_pasta():
    caminho_pasta = input("Digite o caminho da pasta contendo os arquivos CSV: ").strip()
    return Path(caminho_pasta)

def processar_arquivos_csv(pasta):
    dataframes = []
    for arquivo_csv in pasta.rglob("*.csv"):
        try:
            # Tenta ler o arquivo CSV com a codificação 'utf-8'
            df = pd.read_csv(arquivo_csv, encoding='utf-8')
            dataframes.append(df)
            print(f"Arquivo CSV lido: {arquivo_csv}")
            print(f"Número de linhas: {len(df)}")
            print(f"Colunas: {df.columns.tolist()}")
        except UnicodeDecodeError:
            # Se falhar, tenta ler usando a codificação 'latin-1'
            df = pd.read_csv(arquivo_csv, encoding='latin-1')
            dataframes.append(df)
            print(f"Arquivo CSV lido com codificação 'latin-1': {arquivo_csv}")
            print(f"Número de linhas: {len(df)}")
            print(f"Colunas: {df.columns.tolist()}")
        except Exception as e:
            print(f"Erro ao ler {arquivo_csv}: {e}")

    if dataframes:
        df_consolidado = pd.concat(dataframes, ignore_index=True)
        return df_consolidado
    else:
        return None

def main():
    caminho_pasta = obter_caminho_pasta()

    df_consolidado = processar_arquivos_csv(caminho_pasta)

    if df_consolidado is not None:
        # Aqui você pode trabalhar com o DataFrame consolidado (df_consolidado) como desejar.
        # Por exemplo, mostrando as primeiras linhas:
        print("Dicionário Consolidado:")
        print(df_consolidado.head())

if __name__ == "__main__":
    main()
