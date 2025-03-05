import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam carregados corretamente
import streamlit as st
import time
import sqlite3
from backend.services.Service_Google_Drive import load_database_into_memory
from frontend.screens.Screen_Login import login_screen
from frontend.screens.Screen_User_Create import user_create_screen
from frontend.screens.Screen_User_List_Edit import user_list_edit_screen
from frontend.screens.Screen_User_Control import user_control_screen
from frontend.screens.Screen_Veiculo_Create import veiculo_create_screen
from frontend.screens.Screen_Veiculo_List_Edit import veiculo_list_edit_screen
from frontend.screens.Screen_Checklists_Create import checklist_create_screen
from frontend.screens.Screen_Checklist_lists import checklist_list_screen
from frontend.screens.Screen_Abastecimento_Create import abastecimento_create_screen
from frontend.screens.Screen_Abastecimento_List_Edit import abastecimento_list_edit_screen
from frontend.screens.Screen_Dash import screen_dash
from frontend.screens.Screen_IA import screen_ia  # ✅ Importar a tela do chatbot IA

# Configuração da página e ocultação do menu padrão do Streamlit
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# 🔄 Carregar banco de dados do Google Drive para a memória
st.write("🔄 Carregando banco de dados do Google Drive...")

conn = load_database_into_memory()  # O banco agora é carregado na memória

if conn is None:
    st.error("❌ ERRO: Não foi possível carregar o banco de dados do Google Drive!")
    st.stop()  # Interrompe a execução do sistema

st.success("✅ Banco de dados carregado da nuvem!")

# Inicializa a sessão do usuário
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "show_welcome" not in st.session_state:
    st.session_state["show_welcome"] = True  # Indica se deve mostrar a tela de boas-vindas

# Se o usuário NÃO estiver autenticado, exibir tela de login
if not st.session_state["authenticated"]:
    login_screen()
else:
    st.title("🚛 Sistema de Gestão de Frotas!")
    st.markdown("### Bem-vindo! Utilize o menu lateral para acessar as funcionalidades.")

    # 🔄 Sempre que houver alteração nos dados, subir para o Google Drive (implementação futura)
    if st.button("💾 Salvar banco de dados no Google Drive"):
        st.error("🚀 No momento, as alterações no banco são feitas apenas na memória! Implementação futura necessária.")
