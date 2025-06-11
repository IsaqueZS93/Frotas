"""
pages/login.py

Tela de login do sistema Fleet Management.

Funcionalidades:
- Autenticação de usuários via e-mail e senha.
- Validação de credenciais usando auth_service.py.
- Redirecionamento após login bem-sucedido.
"""
import sys
import os
import bcrypt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from services.auth_service import login

# Aplicando o CSS personalizado
st.markdown('<link rel="stylesheet" href="/static/css/styles.css">', unsafe_allow_html=True)

# ==============================
# 🎨 Interface da Tela de Login
# ==============================
st.markdown("<h2 style='text-align: center;'>🚗 Fleet Management </h2>", unsafe_allow_html=True)

# Centralizando a área de login
st.markdown("""
    <div style='display: flex; justify-content: center;'>
        <div style='width: 350px; padding: 20px; background: white; border-radius: 8px; 
        box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.1);'>
""", unsafe_allow_html=True)

# Campos de entrada
email = st.text_input("E-mail", placeholder="Digite seu e-mail")
senha = st.text_input("Senha", placeholder="Digite sua senha", type="password")

# Botão de Login
if st.button("Entrar", type="primary"):
    if email and senha:
        user_data = login(email, senha)

        if user_data:
            # Armazenando o token e dados do usuário na sessão
            st.session_state["token"] = user_data["token"]
            st.session_state["user"] = user_data

            st.success(f"✅ Bem-vindo, {user_data['nome']}! Redirecionando...")

            # Redirecionamento para o sistema principal
            st.switch_page("app.py")

        else:
            st.error("❌ E-mail ou senha incorretos. Tente novamente.")
    else:
        st.warning("⚠️ Preencha todos os campos.")

# ==============================
# 🔹 Rodapé
# ==============================
st.markdown("</div></div>", unsafe_allow_html=True)
st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)
