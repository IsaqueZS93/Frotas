# 🔹 Menu lateral para navegação
menu_option = st.sidebar.radio(
    "Navegação",
    [
        "Gerenciar Perfil", "Cadastrar Usuário", "Gerenciar Usuários", "Cadastrar Veículo",
        "Gerenciar Veículos", "Novo Checklist", "Gerenciar Checklists", "Novo Abastecimento",
        "Gerenciar Abastecimentos", "Dashboards", "Chatbot IA 🤖", "Logout"
    ]
)

# 🔹 Redirecionamento baseado na opção selecionada
if menu_option == "Gerenciar Perfil":
    user_control_screen()
elif menu_option == "Cadastrar Usuário":
    user_create_screen()  # ✅ Agora sempre acessível
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
    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.session_state["user_type"] = None
    st.session_state["user_name"] = None
    st.session_state["first_access"] = True  # ✅ Quando deslogar, volta a pedir login na próxima vez
    st.success("Você saiu do sistema. Redirecionando para a tela de login... 🔄")
    st.rerun()
else:
    st.warning("Você não tem permissão para acessar esta página.")
