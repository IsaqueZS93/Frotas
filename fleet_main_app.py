# C:\Users\Novaes Engenharia\github - deploy\Frotas\fleet_main_app.py

import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import streamlit as st
import time  # 🔹 Para controle do redirecionamento automático
@@ -18,7 +16,7 @@
from frontend.screens.Screen_Dash import screen_dash
from frontend.screens.Screen_IA import screen_ia  # ✅ Importa a tela do chatbot IA

#  Configuração da página e ocultação do menu padrão do Streamlit
# Configuração da página e ocultação do menu padrão do Streamlit
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

hide_menu_style = """
@@ -30,63 +28,26 @@
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

#  Inicializa o banco de dados
# Inicializa o banco de dados
create_database()

#  Depuração das credenciais do Google Drive
st.subheader("🔍 Verificando credenciais do Google Drive...")

try:
    if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
        st.success("✅ Conta de serviço detectada.")
        st.json(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    else:
        st.error("❌ Conta de serviço NÃO encontrada em `st.secrets`.")

    if "web" in st.secrets:
        st.success("✅ Credenciais OAuth detectadas.")
        st.json(st.secrets["web"])
    else:
        st.error("❌ Credenciais OAuth NÃO encontradas em `st.secrets`.")
except Exception as e:
    st.error(f"❌ Erro ao carregar segredos do Streamlit: {e}")

#  Testando a conexão com o Google Drive
st.subheader("🔗 Testando conexão com o Google Drive...")
try:
    service = get_google_drive_service()
    st.success("✅ Conexão com o Google Drive estabelecida com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Google Drive: {e}")

#  Testando a criação de pasta no Google Drive
st.subheader("📂 Testando criação de pasta no Google Drive")
try:
    folder_id = create_folder("Teste_Pasta")
    if folder_id:
        st.success(f"📁 Pasta criada com sucesso! ID: {folder_id}")
    else:
        st.error("❌ Falha ao criar a pasta.")
except Exception as e:
    st.error(f"❌ Erro ao criar a pasta no Google Drive: {e}")

#  Inicializa a sessão do usuário
# Inicializa a sessão do usuário
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "show_welcome" not in st.session_state:
    st.session_state["show_welcome"] = True  # Indica se deve mostrar a tela de boas-vindas

#  Se o usuário NÃO estiver autenticado, exibir tela de login
# Se o usuário NÃO estiver autenticado, exibir tela de login
if not st.session_state["authenticated"]:
    login_screen()
else:
    #  Exibir a tela de boas-vindas antes do menu lateral
    # Exibir a tela de boas-vindas antes do menu lateral
    if st.session_state["show_welcome"]:
        st.title("🚛 Sistema de Gestão de Frotas!")
        st.markdown("""
        ###  Como navegar no sistema?
        ### Como navegar no sistema?
        - **Menu lateral**: Utilize o menu lateral para acessar todas as funcionalidades do sistema.
        - **Cadastrar e Gerenciar**: Adicione e edite usuários, veículos e abastecimentos.
        - **Checklists**: Registre e acompanhe os checklists de veículos.
@@ -143,7 +104,7 @@
        elif menu_option == "Dashboards" and st.session_state["user_type"] == "ADMIN":
            screen_dash()
        elif menu_option == "Chatbot IA 🤖":
            screen_ia()  #  Chama a tela do chatbot IA
            screen_ia()  # Chama a tela do chatbot IA
        elif menu_option == "Logout":
            # Botão de logout: Reseta sessão e recarrega a página
            st.session_state["authenticated"] = False
