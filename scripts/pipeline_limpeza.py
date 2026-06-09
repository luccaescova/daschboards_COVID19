# scripts/pipeline_limpeza.py
import pandas as pd
import numpy as np

def processar_dados():
    print("⚙️ Iniciando tratamento e transformação de dados...")
    
    # 1. Aquisição interna dos dados coletados
    df_covid = pd.read_csv("data/raw/covid_raw.csv")
    df_est = pd.read_csv("data/raw/estados_raw.csv")
    
    # 🔍 INVESTIGAÇÃO DE ERRO: Vamos padronizar o nome das colunas do arquivo do IBGE
    # Remove acentos, espaços e deixa tudo em letras minúsculas para não errar
    df_est.columns = df_est.columns.str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    
    # Se a coluna de população vier com nome diferente (ex: "populacao_2010"), nós adaptamos
    if 'populacao_2010' in df_est.columns:
        df_est = df_est.rename(columns={'populacao_2010': 'populacao'})
    elif 'populacao_2020' in df_est.columns:
        df_est = df_est.rename(columns={'populacao_2020': 'populacao'})
        
    print(f"📋 Colunas detectadas no arquivo de estados: {list(df_est.columns)}")

    # 2. Integração (Merge/Join)
    # Removeemos a linha agregadora nacional para evitar duplicidade na soma dos estados
    df_covid = df_covid[df_covid['state'] != 'TOTAL']
    
    # Unindo as tabelas pelas siglas dos estados ('state' na covid e 'uf' no ibge)
    df_completo = pd.merge(df_covid, df_est, left_on='state', right_on='uf', how='inner')
    
    # 3. Verificação de Segurança
    if 'populacao' not in df_completo.columns:
        # Se mesmo assim não achar, tentamos mapear a primeira coluna numérica que sobrou como população
        colunas_numericas = df_est.select_dtypes(include=[np.number]).columns
        if len(colunas_numericas) > 0:
            df_completo['populacao'] = df_completo[colunas_numericas[0]]
            print(f"⚠️ Atenção: 'populacao' não encontrada. Usando a coluna '{colunas_numericas[0]}' como substituta.")
        else:
            raise KeyError("A coluna de população não foi encontrada no arquivo de estados do IBGE.")

    # 4. Limpeza e Tratamento de Inconsistências
    df_completo['date'] = pd.to_datetime(df_completo['date'])
    df_completo['deaths'] = df_completo['deaths'].fillna(0).astype(int)
    df_completo['newDeaths'] = df_completo['newDeaths'].fillna(0).astype(int)
    df_completo['newCases'] = df_completo['newCases'].fillna(0).astype(int)
    
    # 5. Transformação Avançada (Engenharia de Variáveis)
    # Criando métrica proporcional: Óbitos por 100 mil habitantes
    df_completo['obitos_por_100k'] = (df_completo['deaths'] / df_completo['populacao']) * 100000
    
    # Criando Média Móvel de 7 dias para eliminar o ruído de atraso dos fins de semana
    df_completo = df_completo.sort_values(by=['state', 'date'])
    df_completo['media_movel_obitos'] = df_completo.groupby('state')['newDeaths'].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    
    # Salvando a base final consolidada para alimentação do Dashboard
    df_completo.to_csv("data/processed/covid_dashboard_data.csv", index=False)
    print("✅ Pipeline executado com sucesso! Dados consolidados salvos sem erros.")

if __name__ == "__main__":
    processar_dados()