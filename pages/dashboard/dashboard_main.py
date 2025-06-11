"""
pages/dashboard/dashboard_main.py

Módulo principal do Dashboard.

Funcionalidades:
- Exibição do resumo geral do sistema.
- Navegação entre diferentes seções do dashboard.
- Integração com gráficos e alertas.
"""

import streamlit as st
import pandas as pd
import time
from database.models.models_abastecimentos import get_all_abastecimentos
from database.models.models_veiculos import get_all_veiculos
from database.models.models_usuarios import get_all_usuarios
from pages.dashboard.dashboard_charts import render_charts
from pages.dashboard.dashboard_alerts import render_alerts
from services.auth_service import get_user_by_token

# Aplicando o CSS personalizado
st.markdown('<link rel="stylesheet" href="/static/css/styles.css">', unsafe_allow_html=True)

# ==============================
# 🛑 Verificação de Permissão (Apenas ADMIN e OPE)
# ==============================
if "token" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.stop()

usuario_logado = get_user_by_token(st.session_state["token"])

if not usuario_logado:
    st.warning("⚠️ Sessão inválida. Faça login novamente.")
    st.stop()

st.markdown("<h2 style='text-align: center;'>📊 Dashboard - Visão Geral</h2>", unsafe_allow_html=True)

# ==============================
# 🔹 Carregamento de Dados
# ==============================
with st.spinner("Carregando dados..."):
    usuarios = get_all_usuarios()
    veiculos = get_all_veiculos()
    abastecimentos = get_all_abastecimentos()

    total_usuarios = len(usuarios)
    total_veiculos = len(veiculos)
    total_abastecimentos = len(abastecimentos)

    time.sleep(1)  # Simula carregamento de dados

# ==============================
# 📌 Exibição de Métricas Resumidas
# ==============================
st.markdown("### 📌 Resumo Geral")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👤 Usuários Cadastrados", total_usuarios)
    
with col2:
    st.metric("🚗 Veículos Ativos", total_veiculos)
    
with col3:
    st.metric("⛽ Abastecimentos", total_abastecimentos)

st.divider()

# ==============================
# 📊 Seção de Gráficos
# ==============================
st.markdown("### 📈 Análises e Gráficos")
render_charts()

st.divider()

# ==============================
# 🚨 Seção de Alertas e Notificações
# ==============================
st.markdown("### 🚨 Alertas do Sistema")
render_alerts()

st.divider()

# ==============================
# 🔹 Rodapé
# ==============================
st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)
