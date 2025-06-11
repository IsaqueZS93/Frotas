"""
pages/dashboard/dashboard_charts.py

Módulo responsável por gerar gráficos e visualizações interativas para o Dashboard.

Funcionalidades:
- Gráfico de abastecimentos por veículo.
- Gráfico de consumo médio de combustível.
- Gráfico de usuários ativos no sistema.
- Gráfico de evolução de quilometragem.
- Gráfico de custos por veículo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.models.models_abastecimentos import get_all_abastecimentos
from database.models.models_veiculos import get_all_veiculos
from database.models.models_usuarios import get_all_usuarios
from utils.advanced_analytics import (
    calcular_evolucao_km,
    calcular_metricas_eficiencia
)

# ==============================
# 📊 Função Principal - Renderiza os Gráficos
# ==============================
def render_charts():
    """
    Gera os gráficos do dashboard utilizando dados do banco de dados.
    """
    st.markdown("### 📊 Visualizações e Análises")

    # Carregar dados
    abastecimentos = get_all_abastecimentos()
    veiculos = get_all_veiculos()
    usuarios = get_all_usuarios()

    # Converter para DataFrames
    df_abastecimentos = pd.DataFrame(abastecimentos)
    df_veiculos = pd.DataFrame(veiculos)
    df_usuarios = pd.DataFrame(usuarios)

    # ==============================
    # 🔹 Gráfico: Evolução de Quilometragem
    # ==============================
    if not df_veiculos.empty:
        st.markdown("#### 📏 Evolução de Quilometragem")
        
        # Selecionar veículo para análise detalhada
        placa_selecionada = st.selectbox(
            "Selecione um veículo para análise detalhada",
            ["Todos"] + df_veiculos["placa"].tolist()
        )
        
        if placa_selecionada != "Todos":
            veiculo_id = df_veiculos[df_veiculos["placa"] == placa_selecionada]["id"].iloc[0]
            df_evolucao = calcular_evolucao_km(abastecimentos, [], veiculo_id)
            
            if not df_evolucao.empty:
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
                
                # Exibir métricas de eficiência
                metricas = calcular_metricas_eficiencia(df_evolucao, abastecimentos)
                if metricas:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📏 KM Total", f"{metricas['km_total']:,.0f} km")
                    with col2:
                        st.metric("⛽ Consumo Médio", f"{metricas['km_por_litro']:.2f} km/l")
                    with col3:
                        st.metric("💰 Custo por KM", f"R$ {metricas['custo_por_km']:.2f}")

    # ==============================
    # 🔹 Gráfico: Consumo por Veículo
    # ==============================
    if not df_abastecimentos.empty:
        st.markdown("#### ⛽ Consumo por Veículo")
        
        # Calcular métricas para cada veículo
        metricas_veiculos = []
        for _, veiculo in df_veiculos.iterrows():
            df_evolucao = calcular_evolucao_km(abastecimentos, [], veiculo['id'])
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

    # ==============================
    # 🔹 Gráfico: Distribuição de Usuários
    # ==============================
    if not df_usuarios.empty:
        st.markdown("#### 👥 Distribuição de Usuários")
        
        usuarios_tipo = df_usuarios["tipo"].value_counts().reset_index()
        usuarios_tipo.columns = ["Tipo de Usuário", "Quantidade"]

        fig_usuarios = px.pie(
            usuarios_tipo,
            names="Tipo de Usuário",
            values="Quantidade",
            title="Distribuição de Usuários por Tipo",
            hole=0.4
        )
        st.plotly_chart(fig_usuarios, use_container_width=True)

    # ==============================
    # 📌 Rodapé
    # ==============================
    st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)
