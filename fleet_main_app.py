import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import os
import sqlite3
from backend.database.db_fleet import create_database, DB_PATH

from frontend.screens.Screen_Login import login_screen

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

# 🔹 Criar e verificar o banco de dados antes de iniciar
if not os.path.exists(DB_PATH):
    st.warning("⚠️ Banco de dados não encontrado! Criando um novo banco...")
    create_database()
if not os.path.exists(DB_PATH):
    st.error("❌ Banco de dados não encontrado! O sistema não pode continuar.")
    st.stop()
st.success("✅ Banco de dados pronto para uso!")

# 🔹 Inicializa as variáveis de estado
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

# 🔹 Tela de Login
if not st.session_state["authenticated"]:
    user_info = login_screen()
    if user_info:
        st.session_state["authenticated"] = True
        st.session_state["user_name"] = user_info["user_name"]
        st.session_state["user_type"] = user_info["user_type"]
        st.rerun()
