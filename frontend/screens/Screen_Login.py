# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\screens\Screen_Login.py

import streamlit as st
import sys
import os
import traceback  # Para capturar detalhes dos erros
import bcrypt  # 🔹 Para comparar a senha com o hash

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos modelos do banco de dados
from backend.db_models.DB_Models_User import get_user_by_usuario


def login_screen():
    """Tela de Login do Sistema de Gestão de Frotas."""

    # 🔹 Estilização com CSS para um visual mais moderno
    st.markdown("""
        <style>
            .title-container {
                text-align: center;
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                margin-bottom: 20px;
            }

            .login-container {
                max-width: 400px;
                margin: auto;
                padding: 2rem;
                border-radius: 10px;
                background-color: #ffffff;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                text-align: center;
            }

            .stTextInput>div>div>input {
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 10px;
            }

            .login-button {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 8px;
                width: 100%;
                cursor: pointer;
                transition: 0.3s;
            }
            .login-button:hover {
                background-color: #2980b9;
            }

            .error-message {
                color: #dc3545;
                font-size: 14px;
                margin-top: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 🔹 Título centralizado
    st.markdown('<div class="title-container">🚛 Gestão de Frotas</div>', unsafe_allow_html=True)

    # 🔹 Centraliza o formulário de login
    with st.container():
        st.subheader("Acesse sua conta")

        usuario = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")

        if st.button("🔓 Entrar", use_container_width=True):
            if not usuario or not senha:
                st.markdown('<p class="error-message">❌ Por favor, preencha todos os campos!</p>', unsafe_allow_html=True)
                print("[ERRO] Campos de usuário ou senha estão vazios.")
                return

            try:
                # 🔹 Buscar usuário no banco
                user = get_user_by_usuario(usuario)

                if user:
                    print(f"[INFO] Usuário encontrado: {user['nome_completo']}")

                    # 🔒 Recuperar senha armazenada no banco
                    senha_hash = user["senha"]

                    if not senha_hash:
                        st.markdown('<p class="error-message">❌ Erro: senha não cadastrada!</p>', unsafe_allow_html=True)
                        print("[ERRO] Senha não encontrada no banco de dados.")
                        return

                    # 🔹 Garantir que o hash seja `bytes` antes da comparação
                    if isinstance(senha_hash, str):
                        senha_hash = senha_hash.encode('utf-8')  # Converte string para bytes

                    # 🔑 Comparação da senha digitada com o hash armazenado
                    if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
                        st.success(f"✅ Bem-vindo, {user['nome_completo']}!")

                        # 🔹 Salvar sessão do usuário
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = user["id"]
                        st.session_state["user_type"] = user["tipo"]

                        print(f"[INFO] Login bem-sucedido para {user['nome_completo']}")
                        st.rerun()
                    else:
                        st.markdown('<p class="error-message">❌ Senha incorreta!</p>', unsafe_allow_html=True)
                        print("[ERRO] Senha incorreta!")
                else:
                    st.markdown('<p class="error-message">❌ Usuário não encontrado!</p>', unsafe_allow_html=True)
                    print("[ERRO] Usuário não encontrado no banco de dados.")

            except Exception as e:
                st.markdown('<p class="error-message">⚠️ Erro inesperado durante a autenticação!</p>', unsafe_allow_html=True)
                print("[FATAL ERRO] Ocorreu um erro inesperado no login.")
                print(traceback.format_exc())  # Mostra a stack trace completa para depuração

    st.markdown('</div>', unsafe_allow_html=True)


# Executar a tela se for o script principal
if __name__ == "__main__":
    login_screen()
