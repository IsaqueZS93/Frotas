import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import os
import time
from backend.database.db_fleet import create_database, DB_PATH

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
from frontend.screens.Screen_IA import screen_ia  # ✅ Importa a tela do chatbot IA

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

# 🔹 Criar e verificar o banco de dados antes de iniciar
st.write(f"📂 Tentando localizar o banco de dados em: `{DB_PATH}`")
if not os.path.exists(DB_PATH):
    st.warning("⚠️ Banco de dados não encontrado! Criando um novo banco...")
    create_database()

# 🔹 Verifica se o banco foi criado corretamente
if not os.path.exists(DB_PATH):
    st.error("❌ Banco de dados não encontrado! O sistema não pode continuar.")
    st.stop()

st.success("✅ Banco de dados encontrado e pronto para uso!")

# 🔹 Inicializa a sessão do usuário
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "show_welcome" not in st.session_state:
    st.session_state["show_welcome"] = True

# 🔹 Se o usuário NÃO estiver autenticado, exibir tela de login
if not st.session_state["authenticated"]:
    user_name = login_screen()
    
    if user_name:
        st.session_state["user_name"] = user_name
        st.rerun()
else:
    # 🔹 Exibir usuário logado no menu lateral
    st.sidebar.write(f"👤 Usuário logado: {st.session_state.get('user_name', 'Desconhecido')}")
    st.sidebar.write(f"🔑 Permissão: {st.session_state.get('user_type', 'Desconhecido')}")

    # 🔹 Exibir botão de backup para ADMINs
    if st.session_state.get("user_type") == "ADMIN":
        st.sidebar.subheader("⚙️ Configurações Avançadas")

        # 🔹 Botão para download do banco de dados
        with open(DB_PATH, "rb") as file:
            st.sidebar.download_button(
                label="📥 Baixar Backup do Banco",
                data=file,
                file_name="fleet_management.db",
                mime="application/octet-stream"
            )

    # 🔹 Menu lateral para navegação
    menu_option = st.sidebar.radio(
        "Navegação",
        ["Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários", "Cadastrar Veículo", 
         "Gerenciar Veículos", "Novo Checklist", "Gerenciar Checklists", "Novo Abastecimento",
         "Gerenciar Abastecimentos", "Dashboards", "Chatbot IA 🤖", "Logout"]
    )

    if menu_option == "Gerenciar Perfil":
        user_control_screen()
    elif menu_option == "Logout":
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["user_type"] = None
        st.session_state["user_name"] = None
        st.session_state["show_welcome"] = True
        st.success("Você saiu do sistema. Redirecionando para a tela de login... 🔄")
        st.rerun()
