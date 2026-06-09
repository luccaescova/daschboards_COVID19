# 📊 Painel de Análise Estratégica: COVID-19 no Brasil

Este projeto final foi desenvolvido como requisito para a disciplina de Banco de Dados / Ciência de Dados. O objetivo principal é aplicar de forma integrada o pipeline de Data Science — desde a coleta automática e tratamento até a construção de um dashboard interativo utilizando **Python**, **Pandas** e **Dash**.

---

## 📂 1. Estrutura do Repositório

O projeto segue uma arquitetura modular para garantir a organização e separação de conceitos:

```text
├── data/
│   ├── raw/                 # Dados brutos coletados via script automático
│   └── processed/           # Dados consolidados e limpos pelo pipeline de ETL
├── scripts/
│   ├── crawler_bonus.py     # Script de coleta automatizada (+1.0 Ponto Bônus)
│   └── pipeline_limpeza.py  # Script de Engenharia, Merge e Tratamento
├── app.py                   # Código principal da interface interativa Dash
└── requirements.txt         # Dependências obrigatórias do sistema

