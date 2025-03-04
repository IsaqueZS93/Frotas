# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\screens\Screen_Dash.py

import streamlit as st
import sys
import os

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos dashboards
from frontend.Dashboards.Dash_Estatisticas_Gerais_Analises import dashboard_estatisticas
from frontend.Dashboards.Dash_Checklists import dashboard_checklists
from frontend.Dashboards.Export_Geral import export_dashboard


# -------------------------------
# 🔒 Verificação de Acesso
# -------------------------------
def verificar_permissao():
    if "user_type" not in st.session_state or st.session_state.user_type != "ADMIN":
        st.error("⚠️ Apenas usuários ADMIN podem acessar esta tela.")
        st.stop()

# -------------------------------
# 📊 Tela Principal do Dashboard
# -------------------------------
def screen_dash():
    """
    Tela principal do dashboard, permitindo alternar entre estatísticas gerais, checklists e exportação de relatórios.
    """
    verificar_permissao()
    st.title("📊 Painel de Controle - Gestão de Frotas")

    # Menu de seleção
    menu = ["📈 Estatísticas Gerais", "📋 Checklists", "📄 Exportar Relatório"]
    escolha = st.sidebar.radio("🔍 Selecione uma visão:", menu)

    # Renderiza o dashboard conforme a escolha
    if escolha == "📈 Estatísticas Gerais":
        dashboard_estatisticas()
        
    elif escolha == "📋 Checklists":
        dashboard_checklists()
        
    elif escolha == "📄 Exportar Relatório":
        export_dashboard()
        

if __name__ == "__main__":
    screen_dash()
