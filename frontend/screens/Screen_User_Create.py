# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\screens\Screen_User_Create.py

import streamlit as st
import sys
import os
import bcrypt

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos modelos do banco de dados
from backend.db_models.DB_Models_User import (
    create_user, get_user_by_email, get_user_by_usuario, get_user_by_cnh
)

# -------------------------------
# 🔒 Função para Hash de Senha
# -------------------------------
def gerar_hash(senha):
    """Gera um hash seguro para a senha usando bcrypt."""
    try:
        salt = bcrypt.gensalt()  # 🔹 Gera um salt aleatório
        hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)  # 🔹 Gera o hash da senha
        hash_string = hashed.decode('utf-8')  # 🔹 Retorna o hash como string para salvar no banco

        # 🔹 Verificação de tamanho para garantir que o hash está correto
        if len(hash_string) != 60:
            print(f"[ERRO] Hash gerado com tamanho incorreto: {len(hash_string)} caracteres")
            return None

        return hash_string
    except Exception as e:
        print(f"[ERRO] Falha ao gerar hash da senha: {e}")
        return None

# -------------------------------
# 👤 Tela de Cadastro de Usuário
# -------------------------------
def user_create_screen():
    """Tela para criar um novo usuário no sistema."""
    
    st.title("🚛 Cadastro de Usuário")

    # Apenas ADMIN pode acessar
    if "user_type" not in st.session_state or st.session_state.user_type != "ADMIN":
        st.error("⚠️ Acesso restrito! Apenas usuários ADMIN podem acessar esta tela.")
        return

    # 🔹 Organização dos campos em colunas
    col1, col2 = st.columns(2)

    with col1:
        nome_completo = st.text_input("👤 Nome Completo", placeholder="Digite o nome completo").strip()
        data_nascimento = st.date_input("📅 Data de Nascimento")
        email = st.text_input("📧 Email", placeholder="exemplo@email.com").strip()
        usuario = st.text_input("🔑 Usuário (Login)", placeholder="Escolha um nome de usuário").strip()
        empresa = st.text_input("🏢 Empresa", placeholder="Digite o nome da empresa").strip()

    with col2:
        cnh = st.text_input("🚗 CNH", placeholder="Número da CNH").strip()
        contato = st.text_input("📞 Contato (Telefone)", placeholder="(99) 99999-9999").strip()
        validade_cnh = st.date_input("⏳ Validade da CNH")
        funcao = st.selectbox("🛠 Função", ["Motorista", "Encanador", "Gerente de operações", "Supervisor", "Gestor de Frotas", "Mecânico", "Outro"])

    # 🔹 Senha e confirmação
    st.subheader("🔒 Definição de Senha")
    col3, col4 = st.columns(2)

    with col3:
        senha = st.text_input("🔑 Senha", type="password", placeholder="Digite uma senha segura")
    
    with col4:
        confirmar_senha = st.text_input("🔑 Confirme a Senha", type="password", placeholder="Repita a senha")

    # 🔹 Escolha do tipo de usuário
    tipo = st.radio("👤 Tipo de Usuário", ["ADMIN", "OPE"], horizontal=True)

    # 🔹 Botão de cadastro
    if st.button("✅ Cadastrar Usuário", use_container_width=True):
        # Verifica se todos os campos obrigatórios estão preenchidos
        if not all([nome_completo, email, usuario, cnh, contato, funcao, empresa, senha, confirmar_senha]):
            st.error("❌ Todos os campos são obrigatórios!")
            return

        if senha != confirmar_senha:
            st.error("❌ As senhas não coincidem! Por favor, digite novamente.")
            return

        if len(senha) < 6:
            st.error("❌ A senha deve ter pelo menos 6 caracteres!")
            return

        # Converte as datas para string antes de validar
        data_nascimento_str = data_nascimento.strftime("%d/%m/%Y")
        validade_cnh_str = validade_cnh.strftime("%d/%m/%Y")

        # Verifica se o usuário já existe
        if get_user_by_email(email):
            st.error("❌ Este email já está cadastrado!")
        elif get_user_by_usuario(usuario):
            st.error("❌ Este nome de usuário já está em uso!")
        elif get_user_by_cnh(cnh):
            st.error("❌ Esta CNH já está cadastrada!")
        else:
            try:
                senha_hash = gerar_hash(senha)  # 🔹 Criptografar senha antes de salvar
                
                if not senha_hash:
                    st.error("❌ Erro ao gerar hash da senha!")
                    return

                print(f"[DEBUG] Hash da senha gerado antes de salvar: {senha_hash} (Tamanho: {len(senha_hash)})")

                # Criação do usuário no banco de dados
                sucesso = create_user(
                    nome_completo, data_nascimento_str, email, usuario, cnh, contato, 
                    validade_cnh_str, funcao, empresa, senha_hash, tipo
                )

                if sucesso:
                    st.success("✅ Usuário cadastrado com sucesso!")
                    st.balloons()

                    # 🔹 Confirmação do que foi salvo no banco
                    print(f"[DEBUG] Usuário salvo com hash: {senha_hash}")

                else:
                    st.error("❌ Erro ao cadastrar o usuário. Verifique os dados e tente novamente.")

            except Exception as e:
                st.error(f"⚠️ Erro inesperado: {e}")
                print(f"[ERRO] Falha ao criar usuário: {e}")

# Executar a tela se for o script principal
if __name__ == "__main__":
    user_create_screen()
