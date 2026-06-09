import os
import requests
import pandas as pd

def coletar_dados_covid():
    print("[BÔNUS] Iniciando coleta automática de dados...")
    
    # Criando pastas se não existirem
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # URL 1: Dataset com histórico de casos e óbitos (wcota/covid19br - baseado no Ministério da Saúde)
    url_covid = "https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv"
    df_covid = pd.read_csv(url_covid)
    
    # URL 2: Dataset de cadastro/dimensão com dados populacionais dos estados (IBGE)
    url_populacao = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/estados.csv"
    df_estados = pd.read_csv(url_populacao)
    
    # Salvando os arquivos brutos distintos (Atende ao critério de 2 arquivos distintos)
    df_covid.to_csv("data/raw/covid_raw.csv", index=False)
    df_estados.to_csv("data/raw/estados_raw.csv", index=False)
    print("✅ Dados salvos com sucesso na pasta data/raw/!")

if __name__ == "__main__":
    coletar_dados_covid()