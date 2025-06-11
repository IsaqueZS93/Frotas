"""
services/auth_service.py

Este módulo gerencia a autenticação de usuários no sistema Fleet Management.

Funcionalidades:
- Login de usuários usando e-mail e senha.
- Geração de hash seguro para senhas.
- Controle de permissões (ADMIN e OPE).
- Geração de token de autenticação para sessão.
"""

import bcrypt
import secrets
from database.models.models_usuarios import get_usuario_by_id

from database.models.models_usuarios import get_usuario_by_email, verify_password

# Dicionário para armazenar sessões ativas
SESSIONS = {}

def login(email, senha):
    """
    Autentica um usuário usando e-mail e senha.

    Parâmetros:
        email (str): E-mail do usuário.
        senha (str): Senha fornecida no login.

    Retorna:
        dict | None: Dicionário com informações do usuário autenticado e token de sessão, ou None se falhar.
    """
    usuario = get_usuario_by_email(email)

    if not usuario:
        print("Erro: Usuário não encontrado!")
        return None

    if not verify_password(senha, usuario["senha_hash"]):
        print("Erro: Senha incorreta!")
        return None

    # Gerando um token de sessão seguro
    token = secrets.token_hex(32)
    SESSIONS[token] = usuario["id"]

    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "tipo": usuario["tipo"],  # ADMIN ou OPE
        "token": token
    }

def logout(token):
    """
    Finaliza a sessão do usuário.

    Parâmetros:
        token (str): Token de sessão do usuário.

    Retorna:
        bool: True se o logout foi bem-sucedido, False caso contrário.
    """
    if token in SESSIONS:
        del SESSIONS[token]
        return True
    return False

def get_user_by_token(token):
    """
    Obtém os dados do usuário autenticado com base no token da sessão.

    Parâmetros:
        token (str): Token de sessão do usuário.

    Retorna:
        dict | None: Dicionário com informações do usuário, ou None se o token for inválido.
    """
    user_id = SESSIONS.get(token)
    if user_id:
        return get_usuario_by_id(user_id)
    return None

if __name__ == "__main__":
    """
    Testes básicos das funções de autenticação.
    """
    print("\nTentando login...")
    user_data = login("joao@email.com", "senha123")

    if user_data:
        print(f"Usuário autenticado: {user_data}")
        token = user_data["token"]

        print("\nVerificando usuário com token...")
        user = get_user_by_token(token)
        print(user)

        print("\nFazendo logout...")
        if logout(token):
            print("Logout realizado com sucesso!")
        else:
            print("Falha no logout!")
    else:
        print("Falha na autenticação.")
