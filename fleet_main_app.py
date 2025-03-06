import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam carregados corretamente
import streamlit as st
import time  # 🔹 Para controle do redirecionamento automático
from backend.services.Service_Google_Drive import download_database  # 🔹 Importa a função de download
from backend.database.db_fleet import create_database
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

# Inicializa o banco de dados
create_database()

# Inicializa a sessão do usuário
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None  # ✅ Salvar nome do usuário
if "show_welcome" not in st.session_state:
    st.session_state["show_welcome"] = True  # Indica se deve mostrar a tela de boas-vindas

# Se o usuário NÃO estiver autenticado, exibir tela de login
if not st.session_state["authenticated"]:
    user_name = login_screen()  # ✅ Supondo que login_screen retorna o nome do usuário ao fazer login
    
    if user_name:
        st.session_state["user_name"] = user_name  # ✅ Salvar nome do usuário na sessão
        st.rerun()
else:
    # Debug: Mostrar usuário e função no menu lateral
    st.sidebar.write(f"👤 Usuário logado: {st.session_state.get('user_name', 'Desconhecido')}")
    st.sidebar.write(f"🔑 Permissão: {st.session_state.get('user_type', 'Desconhecido')}")

    # Exibir a tela de boas-vindas antes do menu lateral
    if st.session_state["show_welcome"]:
        st.title("🚛 Sistema de Gestão de Frotas!")
        st.markdown("""
        ### Como navegar no sistema?
        - **Menu lateral**: Utilize o menu lateral para acessar todas as funcionalidades do sistema.
        - **Cadastrar e Gerenciar**: Adicione e edite usuários, veículos e abastecimentos.
        - **Checklists**: Registre e acompanhe os checklists de veículos.
        - **Dashboards**: Visualize estatísticas sobre a frota.
        - **IA Inteligente**: Utilize a IA para obter insights sobre os dados da frota.
        - **Logout**: Para sair, basta clicar na opção *Logout* no menu lateral.
        """)

        st.success("✅ Você está autenticado. Selecione uma opção no menu lateral para começar!")

        # Botão para acessar o menu ou redirecionamento automático após 20 segundos
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Acessar o Menu"):
                st.session_state["show_welcome"] = False
                st.rerun()

        with col2:
            with st.spinner("Redirecionando para o menu em 20 segundos... ⏳"):
                time.sleep(20)
                st.session_state["show_welcome"] = False
                st.rerun()

    else:
        # Menu lateral para navegação
        st.sidebar.title("Gestão de Frotas 🚛")
        menu_option = st.sidebar.radio(
            "Navegação",
            [
                "Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários", "Cadastrar Veículo", "Gerenciar Veículos",
                "Novo Checklist", "Gerenciar Checklists", "Novo Abastecimento", "Gerenciar Abastecimentos", "Dashboards", 
                "Chatbot IA 🤖", "Logout"
            ]
        )

        # ✅ Exibir botão de backup para ADMINs
        if st.session_state.get("user_type") == "ADMIN":
            st.sidebar.subheader("⚙️ Configurações Avançadas")
            if st.sidebar.button("📥 Baixar Backup do Banco"):
                st.write("🔄 Baixando backup do banco de dados...")
                download_database()
                st.success("✅ Backup do banco de dados baixado com sucesso!")

        if menu_option == "Gerenciar Perfil":
            user_control_screen()
        elif menu_option == "Cadastrar Usuário" and st.session_state["user_type"] == "ADMIN":
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
            screen_ia()  # Chama a tela do chatbot IA
        elif menu_option == "Logout":
            # Botão de logout: Reseta sessão e recarrega a página
            st.session_state["authenticated"] = False
            st.session_state["user_id"] = None
            st.session_state["user_type"] = None
            st.session_state["user_name"] = None
            st.session_state["show_welcome"] = True  # Resetar para exibir boas-vindas na próxima vez
            st.success("Você saiu do sistema. Redirecionando para a tela de login... 🔄")
            st.rerun()
        else:
            st.warning("Você não tem permissão para acessar esta página.")
