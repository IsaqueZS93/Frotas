"""
pages/crud_usuarios.py

Tela CRUD para gerenciamento de usuários (somente ADMIN).

Funcionalidades:
- Listar usuários existentes.
- Criar novos usuários com senha segura.
- Editar usuários cadastrados.
- Excluir usuários com confirmação.
"""

import sys
import os
import io

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import bcrypt
from database.models.models_usuarios import (
    get_all_usuarios, create_usuario, update_usuario, delete_usuario
)
from services.auth_service import get_user_by_token
from services.google_drive_service import upload_file_to_drive

# 📌 ID da pasta CNHs no Google Drive
CNH_FOLDER_ID = "1cTg0fV0VgzHKM23evhTf93SXHRu3ojjG"

# Aplicando o CSS personalizado
st.markdown('<link rel="stylesheet" href="/static/css/styles.css">', unsafe_allow_html=True)

# ==============================
# 🛑 Verificação de Permissão (Apenas ADMIN)
# ==============================
if "token" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.stop()

usuario_logado = get_user_by_token(st.session_state["token"])

if not usuario_logado or usuario_logado["tipo"] != "ADMIN":
    st.warning("🚫 Acesso negado! Apenas administradores podem gerenciar usuários.")
    st.stop()

st.markdown("<h2 style='text-align: center;'>👤 Gerenciamento de Usuários</h2>", unsafe_allow_html=True)

# ==============================
# 🔹 Formulário para Criar Novo Usuário
# ==============================
with st.expander("➕ Adicionar Novo Usuário"):
    with st.form("form_novo_usuario"):
        nome = st.text_input("Nome Completo", placeholder="Digite o nome")
        email = st.text_input("E-mail", placeholder="exemplo@email.com")
        cpf = st.text_input("CPF", placeholder="Somente números")
        data_nascimento = st.date_input("Data de Nascimento")
        funcao = st.text_input("Função", placeholder="Ex.: Supervisor de Frotas")
        empresa = st.text_input("Empresa", placeholder="Nome da empresa")
        tipo = st.selectbox("Tipo de Usuário", ["ADMIN", "OPE"])
        senha = st.text_input("Senha", type="password", placeholder="Defina uma senha segura")
        foto_cnh = st.file_uploader("Foto da CNH (opcional)", type=["jpg", "png", "jpeg", "pdf"])

        if st.form_submit_button("Salvar Usuário"):
            if nome and email and cpf and senha:
                # Gerando hash da senha
                senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

                # Upload da CNH para o Google Drive (se fornecida)
                cnh_drive_link = None
                if foto_cnh:
                    try:
                        file_bytes = io.BytesIO(foto_cnh.read())  # Criar objeto BytesIO
                        upload_result = upload_file_to_drive(
                            file_bytes=file_bytes,  # Passando o objeto BytesIO diretamente
                            filename=foto_cnh.name,
                            mime_type="image/jpeg",
                            folder_id=CNH_FOLDER_ID
                        )
                        if upload_result and "id" in upload_result:
                            cnh_drive_link = f"https://drive.google.com/file/d/{upload_result['id']}/view"
                    except Exception as e:
                        st.error(f"❌ Erro ao enviar CNH para o Google Drive: {e}")


                # Criar usuário sem o campo extra caso ele não exista na função create_usuario
                if cnh_drive_link:
                    create_usuario(nome, email, cpf, data_nascimento, funcao, empresa, tipo, senha_hash, cnh_drive_link)
                else:
                    create_usuario(nome, email, cpf, data_nascimento, funcao, empresa, tipo, senha_hash)

                st.success("✅ Usuário cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("⚠️ Todos os campos obrigatórios devem ser preenchidos.")

# ==============================
# 📌 Listagem de Usuários
# ==============================
st.subheader("📋 Usuários Cadastrados")

usuarios = get_all_usuarios()

if not usuarios:
    st.info("🔹 Nenhum usuário cadastrado.")
else:
    for usuario in usuarios:
        with st.expander(f"{usuario['nome']} ({usuario['tipo']})"):
            col1, col2 = st.columns(2)

            with col1:
                st.text(f"📧 E-mail: {usuario['email']}")
                st.text(f"📌 Função: {usuario['funcao']}")
                st.text(f"🏢 Empresa: {usuario['empresa']}")
                st.text(f"🆔 CPF: {usuario['cpf']}")

            with col2:
                cnh_foto = usuario.get("cnh_foto", None)  # Certifique-se de que a chave está correta
                if cnh_foto:
                    st.markdown(f"[📄 Visualizar CNH]({cnh_foto})", unsafe_allow_html=True)

            # Botões de Ação
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Editar", key=f"edit_{usuario['id']}"):
                    with st.form(f"form_edit_{usuario['id']}"):
                        novo_nome = st.text_input("Nome", value=usuario["nome"])
                        nova_funcao = st.text_input("Função", value=usuario["funcao"])
                        nova_empresa = st.text_input("Empresa", value=usuario["empresa"])
                        novo_tipo = st.selectbox("Tipo de Usuário", ["ADMIN", "OPE"], index=["ADMIN", "OPE"].index(usuario["tipo"]))

                        if st.form_submit_button("Salvar Alterações"):
                            update_usuario(usuario["id"], novo_nome, nova_funcao, nova_empresa, novo_tipo)
                            st.success("✅ Usuário atualizado com sucesso!")
                            st.rerun()

            with col2:
                if st.button("🗑️ Excluir", key=f"delete_{usuario['id']}"):
                    delete_usuario(usuario["id"])
                    st.success("✅ Usuário excluído com sucesso!")
                    st.rerun()

# ==============================
# 🔹 Rodapé
# ==============================
st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)
