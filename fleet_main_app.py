import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import os
import sqlite3
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

# Configuração da página
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# Oculta menu e rodapé do Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

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

# 🔹 Verifica se há usuários cadastrados no banco
def is_first_access():
    """Retorna True se não houver usuários cadastrados no banco de dados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela `users` realmente existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            st.warning("⚠️ A tabela `users` não existe! Criando banco novamente...")
            create_database()
            return True  # Permitir acesso inicial
        
        # Contar os usuários cadastrados
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        st.write(f"🔍 Número de usuários no banco: {user_count}")  # Debug no Streamlit
        
        return user_count == 0
    except Exception as e:
        st.error(f"❌ Erro ao verificar usuários: {e}")
        return False

# 🔹 Inicializa a sessão do usuário
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "show_welcome" not in st.session_state:
    st.session_state["show_welcome"] = True

# 🔹 Se for o primeiro acesso, permitir login automático
if not st.session_state["authenticated"]:
    if is_first_access():
        st.warning("⚠️ Nenhum usuário cadastrado. Acesso liberado sem senha na primeira execução!")
        st.session_state["authenticated"] = True
        st.session_state["user_type"] = "ADMIN"
        st.session_state["user_name"] = "Administrador"
        st.rerun()
    else:
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

        # 🔹 Upload do banco de dados
        uploaded_file = st.sidebar.file_uploader("📤 Enviar um novo banco de dados", type=["db"])
        if uploaded_file is not None:
            new_db_path = os.path.join(os.path.dirname(DB_PATH), "fleet_management_uploaded.db")
            with open(new_db_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Substituir o banco de dados principal pelo novo
            os.replace(new_db_path, DB_PATH)
            st.success("✅ Banco de dados atualizado com sucesso! Reinicie o sistema.")
            st.rerun()

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
