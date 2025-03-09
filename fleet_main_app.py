import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import os
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

# 🔹 Configuração inicial do Streamlit com tema azul claro
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# 🔹 Estilização personalizada para um tema azul claro
custom_style = """
    <style>
    body {
        background-color: #E3F2FD;
        color: #0D47A1;
        font-family: Arial, sans-serif;
    }
    .stButton>button {
        background-color: #42A5F5;
        color: white;
        border-radius: 10px;
        padding: 10px;
        width: 100%;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        background-color: #1976D2;
    }
    input, textarea, select {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #90CAF9;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    label, h1, h2, h3, h4, h5, h6 {
        font-weight: bold;
    }
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# 🔹 Inicializa as variáveis de estado
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

# 🔹 Exibe o menu lateral sempre
st.sidebar.title("⚙️ Configuração do Banco de Dados")

# 🔹 Upload do banco de dados SEMPRE disponível no menu lateral
st.sidebar.subheader("📤 Enviar um novo banco de dados")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo (.db)", type=["db"])

if uploaded_file is not None:
    new_db_path = os.path.join(os.path.dirname(DB_PATH), "fleet_management_uploaded.db")
    with open(new_db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Substituir o banco de dados principal pelo novo
    os.replace(new_db_path, DB_PATH)
    st.sidebar.success("✅ Banco de dados atualizado com sucesso! Reinicie o sistema.")
    st.stop()

# 🔹 Se o banco de dados não existir, exibe um aviso
if not os.path.exists(DB_PATH):
    st.sidebar.error("❌ Banco de dados não encontrado! O sistema não pode continuar sem um banco válido.")
    st.stop()

# 🔹 Se o banco existir, exibe a tela de login
if not st.session_state["authenticated"]:
    user_info = login_screen()
    if user_info:
        st.session_state["authenticated"] = True
        st.session_state["user_name"] = user_info["user_name"]
        st.session_state["user_type"] = user_info["user_type"]
        st.rerun()

# 🔹 Exibir menu lateral após login
else:
    st.sidebar.write(f"👤 **Usuário:** {st.session_state.get('user_name', 'Desconhecido')}")
    st.sidebar.write(f"🔑 **Permissão:** {st.session_state.get('user_type', 'Desconhecido')}")

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

    menu_option = st.sidebar.radio(
        "🚗 **Menu Principal**",
        ["Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários", "Cadastrar Veículo",
         "Gerenciar Veículos", "Novo Checklist", "Gerenciar Checklists", "Novo Abastecimento",
         "Gerenciar Abastecimentos", "Dashboards", "Chatbot IA 🤖", "Logout"]
    )

    # 🔹 Controle das telas de navegação
    if menu_option == "Gerenciar Perfil":
        user_control_screen()
    elif menu_option == "Cadastrar Usuário":
        user_create_screen()
    elif menu_option == "Gerenciar Usuários" and st.session_state["user_type"] == "ADMIN":
        user_list_edit_screen()
    elif menu_option == "Cadastrar Veículo" and st.session_state["user_type"] == "ADMIN":
        veiculo_create_screen()
    elif menu_option == "Gerenciar Veículos" and st.session_state["user_type"] == "ADMIN":
        veiculo_list_edit_screen()
    elif menu_option == "Novo Checklist":
        checklist_create_screen()
    elif menu_option == "Gerenciar Checklists" and st.session_state["user_type"] == "ADMIN":
        checklist_list_screen()
    elif menu_option == "Novo Abastecimento":
        abastecimento_create_screen()
    elif menu_option == "Gerenciar Abastecimentos" and st.session_state["user_type"] == "ADMIN":
        abastecimento_list_edit_screen()
    elif menu_option == "Dashboards" and st.session_state["user_type"] == "ADMIN":
        screen_dash()
    elif menu_option == "Chatbot IA 🤖":
        screen_ia()
    elif menu_option == "Logout":
        st.session_state.clear()
        st.success("✅ Você saiu do sistema! Redirecionando... 🔄")
        st.rerun()
