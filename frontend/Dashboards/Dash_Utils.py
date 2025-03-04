# 📂 C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\Dashboards\Dash_Utils.py

import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# 🔹 Garante que o diretório raiz do projeto esteja no sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações corrigidas
from backend.db_models.DB_Models_Abastecimento import get_all_abastecimentos_2
from backend.db_models.DB_Models_checklists import get_all_checklists, get_all_checklists3, get_all_checklists2
from backend.db_models.DB_Models_Veiculo import get_all_veiculos

# -------------------------------
# 🛠️ Funções de Carregamento de Dados
# -------------------------------
def load_abastecimentos():
    """Carrega todos os abastecimentos formatados como DataFrame, garantindo a coluna 'data_hora'."""
    data = get_all_abastecimentos_2()

    if not data:  # Se não houver dados, retorna um DataFrame vazio com as colunas corretas
        return pd.DataFrame(columns=[
            'id', 'id_usuario', 'placa', 'data_hora', 'km_atual', 'km_abastecimento',
            'quantidade_litros', 'tipo_combustivel', 'valor_total'
        ])

    df = pd.DataFrame(data, columns=[
        'id', 'id_usuario', 'placa', 'data_hora', 'km_atual', 'km_abastecimento',
        'quantidade_litros', 'tipo_combustivel', 'valor_total'
    ])

    # ✅ Garante que 'data_hora' seja um datetime válido
    df['data_hora'] = pd.to_datetime(df['data_hora'], format='%d/%m/%Y %H:%M', errors='coerce')

    return df

def load_checklists():
    """Carrega todos os checklists formatados como DataFrame."""
    data = get_all_checklists3()

    if not data:
        return pd.DataFrame(columns=[
            'id', 'id_usuario', 'tipo', 'data_hora', 'placa', 'km_atual', 'km_informado',
            'pneus_ok', 'farois_setas_ok', 'freios_ok', 'oleo_ok', 'vidros_retrovisores_ok',
            'itens_seguranca_ok', 'observacoes', 'fotos'
        ])

    df = pd.DataFrame(data, columns=[
        'id', 'id_usuario', 'tipo', 'data_hora', 'placa', 'km_atual', 'km_informado',
        'pneus_ok', 'farois_setas_ok', 'freios_ok', 'oleo_ok', 'vidros_retrovisores_ok',
        'itens_seguranca_ok', 'observacoes', 'fotos'
    ])

    # ✅ Converter colunas booleanas corretamente
    bool_columns = ['pneus_ok', 'farois_setas_ok', 'freios_ok', 'oleo_ok', 'vidros_retrovisores_ok', 'itens_seguranca_ok']
    for col in bool_columns:
        df[col] = df[col].astype(bool)

    # ✅ Converter 'data_hora' para datetime, tratando erros
    df['data_hora'] = pd.to_datetime(df['data_hora'], format='%d/%m/%Y %H:%M', errors='coerce')

    return df


def load_veiculos():
    """Carrega todos os veículos como DataFrame."""
    data = get_all_veiculos()
    return pd.DataFrame(data, columns=['id', 'placa', 'renavam', 'modelo', 'ano_fabricacao', 'capacidade_tanque', 'hodometro_atual'])

# -------------------------------
# 📊 Funções de Cálculo e Análises
# -------------------------------
def calcular_consumo_medio(placa, period):
    """Calcula o consumo médio de combustível (KM/L) de um veículo no período especificado."""
    df = load_abastecimentos()

    if df.empty:
        return 0

    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')
    period = pd.to_datetime(period)

    df = df[(df['placa'] == placa) & (df['data_hora'] >= period)]
    
    if len(df) < 2:
        return 0  # Não há dados suficientes para cálculo
    
    km_total = df['km_abastecimento'].max() - df['km_abastecimento'].min()
    litros_total = df['quantidade_litros'].sum()
    
    return round(km_total / litros_total, 2) if litros_total > 0 else 0

def calcular_custo_por_km(placa, period):
    """Calcula o custo médio por KM rodado de um veículo."""
    df = load_abastecimentos()

    if df.empty:
        return 0

    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')
    period = pd.to_datetime(period)

    df = df[(df['placa'] == placa) & (df['data_hora'] >= period)]
    
    if df.empty:
        return 0
    
    km_total = df['km_abastecimento'].max() - df['km_abastecimento'].min()
    custo_total = df['valor_total'].sum()
    
    return round(custo_total / km_total, 2) if km_total > 0 else 0

# -------------------------------
# 📈 Funções de Gráficos Interativos (Plotly)
# -------------------------------
def plot_grafico_linhas(df, titulo, xlabel, ylabel):
    """Cria um gráfico de linhas interativo com Plotly."""

    if df.empty:
        st.warning("📌 Dados insuficientes para gerar o gráfico.")
        return

    fig = px.line(df, x='Data', y='Valor', color='Tipo', markers=True, title=titulo)
    fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel, hovermode="x")
    
    st.plotly_chart(fig, use_container_width=True)

def plot_grafico_barras(df, titulo, xlabel, ylabel):
    """Cria um gráfico de barras interativo com Plotly."""

    if df.empty:
        st.warning("📌 Dados insuficientes para gerar o gráfico.")
        return

    fig = px.bar(df, x='Placa', y='Litros Abastecidos', title=titulo, text_auto=True)
    fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
    
    st.plotly_chart(fig, use_container_width=True)
    
def calcular_total_gastos(period):
    """Calcula o custo total de abastecimento em um determinado período."""
    df = load_abastecimentos()
    
    # 🔹 Certifique-se de que 'data_hora' está em formato datetime antes da comparação
    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')

    df = df[df['data_hora'] >= period]

    return df['valor_total'].sum() if not df.empty else 0

def plot_pizza_problemas(df):
    """Cria um gráfico de pizza interativo com Plotly."""

    if df.empty:
        st.warning("📌 Dados insuficientes para gerar o gráfico.")
        return

    fig = px.pie(df, names='Categoria', values='Valor', title='Problemas mais comuns nos checklists')
    st.plotly_chart(fig, use_container_width=True)
