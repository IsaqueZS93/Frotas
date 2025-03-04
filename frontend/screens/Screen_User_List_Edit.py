# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\screens\Screen_User_List_Edit.py

import streamlit as st
import sys
import os
import bcrypt  # 🔒 Para hash de senha

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos modelos do banco de dados
from backend.db_models.DB_Models_User import get_all_users, update_user, delete_user, get_user_by_id

# 🔒 Função para gerar o hash da nova senha
def gerar_hash(senha):
    """Gera um hash seguro para a senha usando bcrypt."""
    try:
        salt = bcrypt.gensalt()  # Gera um salt aleatório
        hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)  # Gera o hash da senha
        return hashed.decode('utf-8')  # Retorna o hash como string para salvar no banco
    except Exception as e:
        print(f"[ERRO] Falha ao gerar hash da senha: {e}")
        return None

def user_list_edit_screen():
    """Tela para listar, editar e excluir usuários."""

    st.title("Gerenciamento de Usuários 🛠️")

    # Apenas ADMIN pode acessar
    if "user_type" not in st.session_state or st.session_state.user_type != "ADMIN":
        st.error("Apenas usuários ADMIN podem acessar esta tela.")
        return

    # Obter todos os usuários cadastrados
    users = get_all_users()

    if not users:
        st.warning("Nenhum usuário cadastrado no momento.")
        return

    # Criar opções de filtro
    filtro_nome = st.text_input("🔎 Buscar por Nome:")
    filtro_funcao = st.selectbox("📌 Filtrar por Função:", ["Todos"] + list(set(user["funcao"] for user in users)))
    filtro_tipo = st.radio("🔹 Tipo de Usuário:", ["Todos", "ADMIN", "OPE"], index=0)

    # Filtrar lista de usuários conforme os critérios
    usuarios_filtrados = [
        user for user in users
        if (filtro_nome.lower() in user["nome_completo"].lower()) and
           (filtro_funcao == "Todos" or user["funcao"] == filtro_funcao) and
           (filtro_tipo == "Todos" or user["tipo"] == filtro_tipo)
    ]

    if not usuarios_filtrados:
        st.warning("Nenhum usuário encontrado com os filtros selecionados.")
        return

    # Exibir lista de usuários
    for user in usuarios_filtrados:
        user_id = user['id']  # ID do usuário para diferenciar os campos únicos

        with st.expander(f"👤 {user['nome_completo']} - {user['funcao']} ({user['tipo']})"):
            novo_nome = st.text_input("Nome Completo", user["nome_completo"], key=f"nome_{user_id}")
            nova_data_nasc = st.text_input("Data de Nascimento", user["data_nascimento"], key=f"nasc_{user_id}")
            novo_email = st.text_input("Email", user["email"], key=f"email_{user_id}")
            novo_usuario = st.text_input("Usuário", user["usuario"], key=f"usuario_{user_id}")
            nova_cnh = st.text_input("CNH", user["cnh"], key=f"cnh_{user_id}")
            novo_contato = st.text_input("Contato", user["contato"], key=f"contato_{user_id}")
            nova_validade_cnh = st.text_input("Validade CNH", user["validade_cnh"], key=f"validade_{user_id}")

            # Correção da seleção da função para evitar erro ao filtrar
            funcoes_disponiveis = ["Motorista", "Encanador", "Gerente de operações", "Supervisor", "Gestor de Frotas", "Mecânico", "Outro"]
            if user["funcao"] not in funcoes_disponiveis:
                funcoes_disponiveis.append(user["funcao"])  # Garante que a função do usuário esteja na lista
            nova_funcao = st.selectbox("Função", funcoes_disponiveis, index=funcoes_disponiveis.index(user["funcao"]), key=f"funcao_{user_id}")

            nova_empresa = st.text_input("Empresa", user["empresa"], key=f"empresa_{user_id}")
            novo_tipo = st.radio("Tipo de Usuário", ["ADMIN", "OPE"], index=["ADMIN", "OPE"].index(user["tipo"]), key=f"tipo_{user_id}")

            # Campo opcional para nova senha
            nova_senha = st.text_input("Nova Senha (opcional)", type="password", key=f"senha_{user_id}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Atualizar", key=f"update_{user_id}"):
                    # Se uma nova senha for fornecida, gera um novo hash
                    senha_hash = None
                    if nova_senha:
                        senha_hash = gerar_hash(nova_senha)
                        if not senha_hash:
                            st.error("❌ Erro ao gerar hash da nova senha!")
                            return

                    sucesso = update_user(
                        user_id, novo_nome, nova_data_nasc, novo_email, novo_usuario, nova_cnh,
                        novo_contato, nova_validade_cnh, nova_funcao, nova_empresa, novo_tipo, senha_hash
                    )
                    if sucesso:
                        st.success(f"✅ Usuário {novo_nome} atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao atualizar usuário. Verifique os dados e tente novamente.")

            with col2:
                if st.button("🗑️ Excluir", key=f"delete_{user_id}"):
                    st.session_state[f"confirm_delete_{user_id}"] = True

            # Confirmação antes de excluir
            if st.session_state.get(f"confirm_delete_{user_id}", False):
                st.warning(f"⚠️ Tem certeza que deseja excluir {user['nome_completo']}?")
                col3, col4 = st.columns(2)
                
                with col3:
                    if st.button("✅ Sim, excluir", key=f"confirm_delete_btn_{user_id}"):
                        delete_user(user_id)
                        st.success(f"✅ Usuário {user['nome_completo']} removido com sucesso!")
                        del st.session_state[f"confirm_delete_{user_id}"]
                        st.rerun()
                
                with col4:
                    if st.button("❌ Cancelar", key=f"cancel_delete_btn_{user_id}"):
                        del st.session_state[f"confirm_delete_{user_id}"]

# Executar a tela se for o script principal
if __name__ == "__main__":
    user_list_edit_screen()
