# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\screens\Screen_User_Control.py

import streamlit as st
import sys
import os

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos modelos do banco de dados
from backend.db_models.DB_Models_User import get_user_by_id, update_user, verificar_senha, gerar_hash


def user_control_screen():
    """Tela para o usuário visualizar e editar suas próprias informações."""

    st.title("Perfil do Usuário 👤")

    # Verifica se o usuário está logado
    if "user_id" not in st.session_state:
        st.error("Você precisa estar logado para acessar esta tela.")
        return

    # Obtém os dados do usuário logado
    user_id = st.session_state.user_id
    user = get_user_by_id(user_id)

    if not user:
        st.error("Usuário não encontrado!")
        return

    # Exibe os dados atuais
    st.subheader("Seus Dados")

    novo_nome = st.text_input("Nome Completo", user["nome_completo"])
    nova_data_nasc = st.text_input("Data de Nascimento", user["data_nascimento"])
    novo_email = st.text_input("Email", user["email"])
    novo_usuario = st.text_input("Usuário (Login)", user["usuario"])
    nova_cnh = st.text_input("CNH", user["cnh"])
    novo_contato = st.text_input("Contato", user["contato"])
    nova_validade_cnh = st.text_input("Validade CNH", user["validade_cnh"])
    nova_funcao = st.text_input("Função", user["funcao"], disabled=True)
    nova_empresa = st.text_input("Empresa", user["empresa"])
    novo_tipo = st.text_input("Tipo de Usuário", user["tipo"], disabled=True)

    if st.button("💾 Atualizar Dados"):
        sucesso = update_user(user_id, novo_nome, nova_data_nasc, novo_email, novo_usuario, nova_cnh, novo_contato, nova_validade_cnh, nova_funcao, nova_empresa, novo_tipo)
        if sucesso:
            st.success("Dados atualizados com sucesso! ✅")
        else:
            st.error("Erro ao atualizar seus dados. Verifique e tente novamente.")

    # Seção para alterar senha
    st.subheader("Alterar Senha 🔑")

    senha_atual = st.text_input("Senha Atual", type="password")
    nova_senha = st.text_input("Nova Senha", type="password")
    confirmar_senha = st.text_input("Confirmar Nova Senha", type="password")

    if st.button("🔄 Alterar Senha"):
        if not senha_atual or not nova_senha or not confirmar_senha:
            st.error("Todos os campos de senha são obrigatórios!")
        elif nova_senha != confirmar_senha:
            st.error("As senhas não coincidem!")
        else:
            # Verifica se a senha atual está correta
            if not verificar_senha(senha_atual, user["senha"]):
                st.error("Senha atual incorreta! ❌")
            else:
                # Criptografa a nova senha e atualiza
                nova_senha_hash = gerar_hash(nova_senha)
                sucesso = update_user(user_id, novo_nome, nova_data_nasc, novo_email, novo_usuario, nova_cnh, novo_contato, nova_validade_cnh, nova_funcao, nova_empresa, novo_tipo, nova_senha_hash)
                
                if sucesso:
                    st.success("Senha alterada com sucesso! ✅")
                else:
                    st.error("Erro ao alterar a senha. Tente novamente.")

# Executar a tela se for o script principal
if __name__ == "__main__":
    user_control_screen()
