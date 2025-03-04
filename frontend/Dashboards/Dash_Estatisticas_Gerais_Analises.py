# 📂 C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\Dashboards\Dash_Estatisticas_Gerais_Analises.py

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from Dash_Utils import (
    load_abastecimentos, calcular_total_gastos, calcular_consumo_medio, calcular_custo_por_km, 
    plot_grafico_linhas, plot_grafico_barras
)

# -------------------------------
# 📊 Estatísticas Gerais (Sem Filtros)
# -------------------------------
def estatisticas_gerais():
    """Exibe os cards com estatísticas gerais."""
    df = load_abastecimentos()

    if df.empty:
        st.warning("🚨 Nenhum dado de abastecimento disponível.")
        return df

    # ✅ Garantir que 'data_hora' existe e está formatada corretamente
    if 'data_hora' not in df.columns:
        st.error("Erro: Coluna 'data_hora' não encontrada nos dados de abastecimento.")
        return df

    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')

    total_litros = df['quantidade_litros'].sum()
    custo_total = df['valor_total'].sum()
    km_total_percorrido = (df['km_abastecimento'].max() - df['km_abastecimento'].min()) if len(df) > 1 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("⛽ Total de Litros Abastecidos", f"{total_litros:.2f} L")
    col2.metric("💰 Custo Total", f"R$ {custo_total:,.2f}")
    col3.metric("🚗 KM Total Percorrido", f"{km_total_percorrido} km")

    return df

# -------------------------------
# 📈 Gráfico de Estatísticas Gerais
# -------------------------------
def grafico_estatisticas(df):
    """Cria um gráfico de linhas mostrando Total de Litros, Custo e KM percorrido ao longo do tempo."""
    
    if df.empty or 'data_hora' not in df.columns:
        st.warning("📌 Não há dados suficientes para gerar o gráfico.")
        return
    
    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')

    # ✅ Agrupamento correto por data
    df_grouped = df.groupby(df['data_hora'].dt.date).agg({
        'quantidade_litros': 'sum',
        'valor_total': 'sum',
        'km_abastecimento': 'sum'
    }).reset_index()

    df_grouped.rename(columns={'data_hora': 'Data'}, inplace=True)

    if df_grouped.empty:
        st.warning("📌 Nenhum dado válido disponível para o gráfico.")
        return

    # ✅ Reformata os dados para visualização correta
    df_melted = df_grouped.melt(id_vars=['Data'], var_name='Tipo', value_name='Valor')

    # 🔹 Criando gráfico interativo com Plotly
    fig = px.line(df_melted, x='Data', y='Valor', color='Tipo', markers=True, title="📊 Evolução de Consumo, Custos e Distância")
    fig.update_layout(xaxis_title="Data", yaxis_title="Valor", hovermode="x")
    
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📊 Análises com Filtros
# -------------------------------
def analise_filtros():
    """Seção de análises baseadas em filtros como Placa, Data, KM e Custos."""
    df = load_abastecimentos()

    if df.empty:
        return

    st.subheader("🔍 Análises Personalizadas")
    placas = df['placa'].unique()
    placa_selecionada = st.selectbox("🚗 Selecione a Placa do Veículo", placas)

    # ✅ Garantir que 'periodo' esteja em formato datetime para evitar erro de comparação
    periodo = st.date_input("📅 Selecione um período", value=pd.to_datetime('today'))
    periodo = pd.to_datetime(periodo)

    consumo_medio = calcular_consumo_medio(placa_selecionada, periodo)
    custo_por_km = calcular_custo_por_km(placa_selecionada, periodo)

    col1, col2 = st.columns(2)
    col1.metric("⛽ Consumo Médio (KM/L)", f"{consumo_medio:.2f} KM/L")
    col2.metric("💲 Custo por KM", f"R$ {custo_por_km:.2f}")

    # 🔹 Gráfico de consumo por veículo
    df_grouped = df.groupby('placa').agg({'quantidade_litros': 'sum'}).reset_index()
    df_grouped.columns = ['Placa', 'Litros Abastecidos']

    fig = px.bar(df_grouped, x='Placa', y='Litros Abastecidos', text_auto=True, title="📊 Consumo de Combustível por Veículo")
    fig.update_layout(xaxis_title="Placa", yaxis_title="Litros Abastecidos")
    
    st.plotly_chart(fig, use_container_width=True)

    # 🔹 Tabela de consumo e custos
    df_table = df[['placa', 'km_abastecimento', 'quantidade_litros', 'valor_total']].copy()

    # Evitar divisão por zero
    df_table['KM/L'] = df_table.apply(lambda row: row['km_abastecimento'] / row['quantidade_litros'] if row['quantidade_litros'] > 0 else 0, axis=1)
    df_table['KM/Custo'] = df_table.apply(lambda row: row['km_abastecimento'] / row['valor_total'] if row['valor_total'] > 0 else 0, axis=1)

    st.write("📋 **Tabela de Consumo e Custos**")
    st.dataframe(df_table)

# -------------------------------
# 🚀 Execução do Dashboard
# -------------------------------
def dashboard_estatisticas():
    """Função principal para exibir estatísticas gerais e análises."""
    st.title("📊 Estatísticas Gerais de Abastecimento")
    df = estatisticas_gerais()
    

    if not df.empty:
        grafico_estatisticas(df)
        analise_filtros()
    else:
        st.warning("🚨 Nenhum dado de abastecimento disponível.")

if __name__ == "__main__":
    dashboard_estatisticas()
