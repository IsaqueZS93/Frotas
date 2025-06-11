import sys
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database.models.models_abastecimentos import get_all_abastecimentos
from database.models.models_checklists import get_all_checklists
from database.models.models_veiculos import get_all_veiculos
from utils.advanced_analytics import (
    calcular_evolucao_km,
    detectar_inconsistencias_km,
    calcular_metricas_eficiencia,
    prever_manutencao
)
from services.auth_service import get_user_by_token
from fpdf import FPDF
from datetime import datetime

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ==============================
# 🛑 Verificação de Permissão
# ==============================
if "token" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.stop()

usuario_logado = get_user_by_token(st.session_state["token"])
if not usuario_logado:
    st.warning("⚠️ Sessão inválida. Faça login novamente.")
    st.stop()

# ==============================
# 📌 Layout Principal
# ==============================
st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center;'>📊 Relatórios e Análises</h2>", unsafe_allow_html=True)

# ==============================
# 🔹 Carregando Dados
# ==============================
abastecimentos = get_all_abastecimentos()
checklists = get_all_checklists()
veiculos = get_all_veiculos()

# Converter os dados para DataFrame
df_abastecimentos = pd.DataFrame(abastecimentos) if abastecimentos else pd.DataFrame()
df_checklists = pd.DataFrame(checklists) if checklists else pd.DataFrame()
df_veiculos = pd.DataFrame(veiculos) if veiculos else pd.DataFrame()

# =======================================================
# Definindo datas padrão com base nos dados disponíveis
# =======================================================
default_data_inicial = datetime.today().replace(day=1)
default_data_final = datetime.today()

if not df_abastecimentos.empty:
    try:
        df_abastecimentos["data_abastecimento"] = pd.to_datetime(df_abastecimentos["data_abastecimento"])
        min_date_abastecimento = df_abastecimentos["data_abastecimento"].min()
        max_date_abastecimento = df_abastecimentos["data_abastecimento"].max()
        default_data_inicial = min_date_abastecimento
        default_data_final = max_date_abastecimento
    except Exception as e:
        pass

if not df_checklists.empty:
    try:
        df_checklists["data_vistoria"] = pd.to_datetime(df_checklists["data_vistoria"])
        min_date_vistoria = df_checklists["data_vistoria"].min()
        max_date_vistoria = df_checklists["data_vistoria"].max()
        if min_date_vistoria < default_data_inicial:
            default_data_inicial = min_date_vistoria
        if max_date_vistoria > default_data_final:
            default_data_final = max_date_vistoria
    except Exception as e:
        pass

# =======================================================
# 🎛️ Painel de Filtros (Avançados)
# =======================================================
st.sidebar.header("🎛️ Painel de Filtros")

# Filtro por Placa
placas = df_veiculos["placa"].unique().tolist() if not df_veiculos.empty else []
placa_selecionada = st.sidebar.selectbox("🚗 Selecione um Veículo", ["Todos"] + placas)

# Filtro por Período
data_inicial = st.sidebar.date_input("📅 Data Inicial", default_data_inicial)
data_final = st.sidebar.date_input("📅 Data Final", default_data_final)

# Filtro por Tipo de Checklist
tipos_checklist = df_checklists["tipo"].unique().tolist() if not df_checklists.empty else []
tipo_checklist_selecionado = st.sidebar.selectbox("📋 Tipo de Checklist", ["Todos"] + tipos_checklist, key="painel_tipo_checklist")

# =======================================================
# Aplicando Filtros aos DataFrames
# =======================================================

# Filtrar abastecimentos por data
df_abastecimentos_filtrados = df_abastecimentos.copy()
if not df_abastecimentos_filtrados.empty:
    df_abastecimentos_filtrados["data_abastecimento"] = pd.to_datetime(df_abastecimentos_filtrados["data_abastecimento"])
    df_abastecimentos_filtrados = df_abastecimentos_filtrados[
        (df_abastecimentos_filtrados["data_abastecimento"] >= pd.to_datetime(data_inicial)) &
        (df_abastecimentos_filtrados["data_abastecimento"] <= pd.to_datetime(data_final))
    ]
    if placa_selecionada != "Todos":
        df_abastecimentos_filtrados = df_abastecimentos_filtrados[df_abastecimentos_filtrados["placa"] == placa_selecionada]

# Filtrar checklists por data e tipo
df_checklists_filtrados = df_checklists.copy()
if not df_checklists_filtrados.empty:
    df_checklists_filtrados["data_vistoria"] = pd.to_datetime(df_checklists_filtrados["data_vistoria"])
    df_checklists_filtrados = df_checklists_filtrados[
        (df_checklists_filtrados["data_vistoria"] >= pd.to_datetime(data_inicial)) &
        (df_checklists_filtrados["data_vistoria"] <= pd.to_datetime(data_final))
    ]
    if placa_selecionada != "Todos":
        df_checklists_filtrados = df_checklists_filtrados[df_checklists_filtrados["placa"] == placa_selecionada]
    if tipo_checklist_selecionado != "Todos":
        df_checklists_filtrados = df_checklists_filtrados[df_checklists_filtrados["tipo"] == tipo_checklist_selecionado]

# =======================================================
# 1 - Análise de Quilometragem
# =======================================================
st.markdown("### 📏 Análise de Quilometragem")

if placa_selecionada != "Todos":
    veiculo_id = df_veiculos[df_veiculos["placa"] == placa_selecionada]["id"].iloc[0]
    
    # Calcular evolução de KM
    df_evolucao = calcular_evolucao_km(abastecimentos, checklists, veiculo_id)
    
    if not df_evolucao.empty:
        # Gráfico de evolução de KM
        fig_evolucao = go.Figure()
        
        # Adicionar linha de KM real
        fig_evolucao.add_trace(go.Scatter(
            x=df_evolucao['data'],
            y=df_evolucao['km'],
            mode='lines+markers',
            name='Quilometragem',
            line=dict(color='blue')
        ))
        
        # Adicionar médias móveis
        fig_evolucao.add_trace(go.Scatter(
            x=df_evolucao['data'],
            y=df_evolucao['km_media_7d'],
            mode='lines',
            name='Média 7 dias',
            line=dict(color='green', dash='dash')
        ))
        
        fig_evolucao.add_trace(go.Scatter(
            x=df_evolucao['data'],
            y=df_evolucao['km_media_30d'],
            mode='lines',
            name='Média 30 dias',
            line=dict(color='red', dash='dash')
        ))
        
        fig_evolucao.update_layout(
            title='Evolução da Quilometragem',
            xaxis_title='Data',
            yaxis_title='Quilometragem',
            template='plotly_white'
        )
        
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Métricas de eficiência
        metricas = calcular_metricas_eficiencia(df_evolucao, abastecimentos)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📏 KM Total", f"{metricas['km_total']:,.0f} km")
        with col2:
            st.metric("⛽ Consumo Médio", f"{metricas['km_por_litro']:.2f} km/l")
        with col3:
            st.metric("💰 Custo por KM", f"R$ {metricas['custo_por_km']:.2f}")
        
        # Detectar inconsistências
        inconsistencias = detectar_inconsistencias_km(df_evolucao)
        if inconsistencias:
            st.warning("⚠️ Inconsistências detectadas na quilometragem:")
            for inc in inconsistencias:
                st.text(f"Data: {inc['data'].strftime('%d/%m/%Y')} - Tipo: {inc['tipo']} - Diferença: {inc['diferenca']} km")
        
        # Previsão de manutenção
        previsao = prever_manutencao(df_evolucao)
        if previsao:
            st.info(f"🔧 Próxima manutenção prevista para: {previsao['data_prevista'].strftime('%d/%m/%Y')} (Faltam {previsao['km_restante']:,.0f} km)")

# =======================================================
# 2 - Comparativo entre Veículos
# =======================================================
st.markdown("### 🚗 Comparativo entre Veículos")

if not df_veiculos.empty:
    # Calcular métricas para cada veículo
    metricas_veiculos = []
    for _, veiculo in df_veiculos.iterrows():
        df_evolucao = calcular_evolucao_km(abastecimentos, checklists, veiculo['id'])
        metricas = calcular_metricas_eficiencia(df_evolucao, abastecimentos)
        if metricas:
            metricas['placa'] = veiculo['placa']
            metricas_veiculos.append(metricas)
    
    if metricas_veiculos:
        df_metricas = pd.DataFrame(metricas_veiculos)
        
        # Gráfico de consumo médio
        fig_consumo = px.bar(
            df_metricas,
            x='placa',
            y='km_por_litro',
            title='Consumo Médio por Veículo',
            labels={'placa': 'Veículo', 'km_por_litro': 'KM/L'},
            color='km_por_litro',
            text_auto='.2f'
        )
        st.plotly_chart(fig_consumo, use_container_width=True)
        
        # Gráfico de custo por KM
        fig_custo = px.bar(
            df_metricas,
            x='placa',
            y='custo_por_km',
            title='Custo por KM por Veículo',
            labels={'placa': 'Veículo', 'custo_por_km': 'R$/KM'},
            color='custo_por_km',
            text_auto='.2f'
        )
        st.plotly_chart(fig_custo, use_container_width=True)

# =======================================================
# 3 - Exportação para PDF
# =======================================================
def gerar_pdf_completo():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Relatório de Frota", ln=True, align="C")
    
    # Adicionar período
    pdf.set_font("Arial", "", 12)
    periodo = f"{data_inicial.strftime('%d/%m/%Y')} - {data_final.strftime('%d/%m/%Y')}"
    pdf.cell(200, 10, f"Período: {periodo}", ln=True)
    
    # Adicionar métricas gerais
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Métricas Gerais:", ln=True)
    pdf.set_font("Arial", "", 10)
    
    if not df_abastecimentos.empty:
        total_abastecido = df_abastecimentos["quantidade_litros"].sum()
        custo_total = df_abastecimentos["valor_total"].sum()
        pdf.cell(200, 10, f"Total abastecido: {total_abastecido:.2f} L", ln=True)
        pdf.cell(200, 10, f"Custo total: R$ {custo_total:.2f}", ln=True)
    
    # Adicionar análise por veículo
    if placa_selecionada != "Todos":
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, f"\nAnálise do Veículo {placa_selecionada}:", ln=True)
        pdf.set_font("Arial", "", 10)
        
        veiculo_id = df_veiculos[df_veiculos["placa"] == placa_selecionada]["id"].iloc[0]
        df_evolucao = calcular_evolucao_km(abastecimentos, checklists, veiculo_id)
        metricas = calcular_metricas_eficiencia(df_evolucao, abastecimentos)
        
        if metricas:
            pdf.cell(200, 10, f"KM Total: {metricas['km_total']:,.0f} km", ln=True)
            pdf.cell(200, 10, f"Consumo Médio: {metricas['km_por_litro']:.2f} km/l", ln=True)
            pdf.cell(200, 10, f"Custo por KM: R$ {metricas['custo_por_km']:.2f}", ln=True)
    
    caminho_pdf = "relatorio_frota.pdf"
    pdf.output(caminho_pdf)
    return caminho_pdf

if st.button("📄 Exportar Relatório para PDF"):
    caminho_pdf = gerar_pdf_completo()
    st.success("✅ Relatório gerado com sucesso!")
    st.download_button("📥 Baixar Relatório", open(caminho_pdf, "rb"), file_name="relatorio_frota.pdf")

# =======================================================
# 🔹 Rodapé
# =======================================================
st.markdown("<p class='footer'>© 2024 Fleet Management - Todos os direitos reservados.</p>", unsafe_allow_html=True)
