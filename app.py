import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Inicialização da base tratada
df = pd.read_csv("data/processed/covid_dashboard_data.csv")
df['date'] = pd.to_datetime(df['date'])

# Último ponto temporal disponível na base para os KPIs executivos
ultimo_dia = df[df['date'] == df['date'].max()]
total_obitos = ultimo_dia['deaths'].sum()
total_casos = ultimo_dia['totalCases'].sum()

# Inicialização do App com tema Bootstrap moderno e clean (FLATLY)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([
    html.Div([
        html.H1("Painel de Análise Estratégica: COVID-19 Brasil", className="text-center my-4 fw-bold text-primary"),
        html.P("Análise integrada de dados epidemiológicos para suporte e geração de insights.", className="text-center text-muted mb-4")
    ]),
    
    dcc.Tabs([
        # ==================== DASHBOARD 1 — VISÃO GERAL ====================
        dcc.Tab(label='Dashboard 1 — Visão Geral Executiva', children=[
            html.Br(),
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("Total de Casos Confirmados (Acumulado)", className="card-title text-muted text-center"),
                        html.H2(f"{total_casos:,}".replace(",", "."), className="card-text text-info fw-bold text-center")
                    ])
                ], color="light"), width=6),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("Total de Óbitos Confirmados (Acumulado)", className="card-title text-muted text-center"),
                        html.H2(f"{total_obitos:,}".replace(",", "."), className="card-text text-danger fw-bold text-center")
                    ])
                ], color="light"), width=6),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H5("Curva Epidemiológica Consolidada (Média Móvel de Óbitos em Linha do Tempo)", className="text-secondary mb-3"),
                    dcc.Graph(
                        figure=px.line(
                            df.groupby('date')['newDeaths'].sum().rolling(7).mean().reset_index(),
                            x='date', y='newDeaths',
                            labels={'date': 'Linha Temporal', 'newDeaths': 'Novas Mortes Diárias'},
                            color_discrete_sequence=['#e74c3c']
                        ).update_layout(template="simple_white", height=400)
                    )
                ], width=12)
            ])
        ]),
        
        # ==================== DASHBOARD 2 — EXPLORAÇÃO INTERATIVA ====================
        dcc.Tab(label='Dashboard 2 — Exploração Interativa', children=[
            html.Br(),
            dbc.Row([
                # Painel de Filtros (Esquerda)
                dbc.Col([
                    html.H5("Filtros de Análise", className="text-primary mb-3 fw-bold"),
                    html.Hr(),
                    html.Label("1. Selecione a Unidade Federativa (UF):", className="fw-bold text-secondary"),
                    dcc.Dropdown(
                        id='dropdown-uf',
                        options=[{'label': f"Estado: {state}", 'value': state} for state in sorted(df['state'].unique())],
                        value='SP',
                        clearable=False,
                        className="mb-4"
                    ),
                    html.Label("2. Tipo de Visualização Métrica:", className="fw-bold text-secondary"),
                    dcc.RadioItems(
                        id='radio-metrica',
                        options=[
                            {'label': ' Dados Absolutos (Volume Bruto)', 'value': 'deaths'},
                            {'label': ' Dados Proporcionais (Por 100k Habitantes)', 'value': 'obitos_por_100k'}
                        ],
                        value='deaths',
                        labelStyle={'display': 'block', 'margin-bottom': '12px', 'cursor': 'pointer'}
                    ),
                    html.Div(className="mt-4 p-3 bg-white border rounded text-muted style-sm", children=[
                        html.Small("💡 Dica: Alterne entre dados absolutos e proporcionais para entender o impacto socioeconômico real por estado.")
                    ])
                ], width=3, style={"background-color": "#f8f9fa", "padding": "25px", "border-radius": "10px", "box-shadow": "2px 2px 5px rgba(0,0,0,0.05)"}),
                
                # Matriz de Gráficos (Direita - 5 Visualizações Mínimas)
                dbc.Col([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='vis-1-linha'), width=6),
                        dbc.Col(dcc.Graph(id='vis-2-barra'), width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='vis-3-scatter'), width=6),
                        dbc.Col(dcc.Graph(id='vis-4-box'), width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='vis-5-area'), width=12)
                    ])
                ], width=9)
            ])
        ])
    ])
], fluid=True)

# Callback dinâmico que orquestra a interatividade do Dashboard 2
@app.callback(
    [Output('vis-1-linha', 'figure'),
     Output('vis-2-barra', 'figure'),
     Output('vis-3-scatter', 'figure'),
     Output('vis-4-box', 'figure'),
     Output('vis-5-area', 'figure')],
    [Input('dropdown-uf', 'value'),
     Input('radio-metrica', 'value')]
)
def renderizar_graficos_dinamicos(uf, metrica):
    # Filtrando a base baseado no dropdown do usuário
    df_uf = df[df['state'] == uf].copy()
    
    # Visualização 1: Linha de Evolução Dinâmica
    tit_1 = f"Evolução Temporal da Métrica Selecionada ({uf})"
    fig1 = px.line(df_uf, x='date', y=metrica, title=tit_1, color_discrete_sequence=['#2c3e50'])
    
    # Visualização 2: Ranking comparativo do último dia do histórico
    df_ultimo_top = df[df['date'] == df['date'].max()].sort_values(by=metrica, ascending=False).head(10)
    fig2 = px.bar(df_ultimo_top, x='state', y=metrica, title="Top 10 Estados em Situação Crítica", color='state')
    
    # Visualização 3: Dispersão (Relação de correlação Casos x Óbitos)
    fig3 = px.scatter(df_uf, x='totalCases', y='deaths', title="Dispersão: Correlação Casos vs Óbitos", color_discrete_sequence=['#16a085'])
    
    # Visualização 4: Boxplot para análise de variabilidade por mês de novos casos
    df_uf['mes_ano'] = df_uf['date'].dt.strftime('%Y-%m')
    fig4 = px.box(df_uf, x='mes_ano', y='newCases', title="Dispersão e Outliers de Casos por Mês")
    
    # Visualização 5: Gráfico de Área para volume de novos casos diários
    fig5 = px.area(df_uf, x='date', y='newCases', title="Frequência e Volume de Novas Infecções Diárias", color_discrete_sequence=['#e67e22'])
    
    # Aplicando Storytelling com Dados para deixar todos os gráficos limpos (sem poluição visual)
    for fig in [fig1, fig2, fig3, fig4, fig5]:
        fig.update_layout(
            template="simple_white", 
            margin=dict(l=25, r=25, t=45, b=25),
            font=dict(size=11)
        )
        
    return fig1, fig2, fig3, fig4, fig5

if __name__ == '__main__':
    # Modificado de app.run_server(debug=True) para app.run(debug=True)
    app.run(debug=True)