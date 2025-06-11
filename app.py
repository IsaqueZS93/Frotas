import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.connection import create_tables
from services.auth_service import get_user_by_token

# ✅ Atualiza o banco de dados no início
try:
    create_tables()
except Exception as e:
    st.error(f"Erro ao inicializar o banco de dados: {e}")
    st.stop()

# ✅ Configuração da Página
st.set_page_config(
    page_title="Gestão de Frotas",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None  # Remove a barra lateral extra do Streamlit
)

# ✅ Verificação de Login
if "token" not in st.session_state:
    st.switch_page("pages/login.py")

usuario_logado = get_user_by_token(st.session_state["token"])

if not usuario_logado:
    st.warning("⚠️ Sessão inválida. Faça login novamente.")
    st.switch_page("pages/login.py")

# ✅ Menu lateral único
with st.sidebar:
    st.title("📌 Menu Principal")

    if usuario_logado["tipo"] == "ADMIN":
        st.markdown("### 🔧 Administração")
        st.page_link("pages/crud_usuarios.py", label="👥 Gerenciar Usuários")
        st.page_link("pages/crud_veiculos.py", label="🚗 Gerenciar Veículos")

    st.markdown("### ⛽ Operações")
    st.page_link("pages/crud_abastecimentos.py", label="⛽ Abastecimentos")
    st.page_link("pages/checklist_inicio.py", label="📋 Checklists")

    st.markdown("### 📊 Relatórios")
    st.page_link("pages/reports.py", label="📊 Relatórios")

    st.markdown("---")
    if st.button("🚪 Sair"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

st.markdown(f"<h2 style='text-align: center;'>Bem-vindo, {usuario_logado['nome']}!</h2>", unsafe_allow_html=True)
