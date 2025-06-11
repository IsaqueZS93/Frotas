"""
database/models/models_usuarios.py

Este módulo contém o modelo de Usuários e suas operações no banco de dados.

Funcionalidades:
- Criar usuários com hash seguro de senha.
- Listar, buscar, atualizar e excluir usuários.
- Garantir integridade dos dados no banco de dados.

"""

import sqlite3
import bcrypt
from database.connection import get_db_connection, execute_query, get_last_inserted_id

def hash_password(password):
    """
    Gera um hash seguro para a senha do usuário.

    Parâmetros:
        password (str): Senha em texto puro.

    Retorna:
        str: Hash da senha gerado.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.

    Parâmetros:
        password (str): Senha em texto puro fornecida pelo usuário.
        hashed_password (str): Hash da senha armazenado no banco.

    Retorna:
        bool: True se a senha estiver correta, False caso contrário.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_usuario(nome, email, cpf, data_nascimento, funcao, empresa, tipo, senha, cnh_foto=None):
    """
    Cria um novo usuário no banco de dados.

    Parâmetros:
        nome (str): Nome completo do usuário.
        email (str): E-mail do usuário (único).
        cpf (str): CPF do usuário (único).
        data_nascimento (str): Data de nascimento (YYYY-MM-DD).
        funcao (str): Cargo do usuário.
        empresa (str): Empresa onde o usuário trabalha.
        tipo (str): Tipo do usuário ('ADMIN' ou 'OPE').
        senha (str): Senha do usuário (será armazenada como hash).
        cnh_foto (str, opcional): URL da CNH salva no Google Drive.

    Retorna:
        int: ID do usuário inserido.
    """
    senha_hash = hash_password(senha)

    query = """
    INSERT INTO usuarios (nome, email, cpf, data_nascimento, funcao, empresa, tipo, senha_hash, cnh_foto)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    execute_query(query, (nome, email, cpf, data_nascimento, funcao, empresa, tipo, senha_hash, cnh_foto))
    return get_last_inserted_id()


def get_usuario_by_id(user_id):
    """
    Retorna os detalhes de um usuário específico.

    Parâmetros:
        user_id (int): ID do usuário.

    Retorna:
        dict | None: Dicionário com os dados do usuário ou None se não encontrado.
    """
    query = "SELECT * FROM usuarios WHERE id = ?"
    result = execute_query(query, (user_id,))
    return dict(result[0]) if result else None

def get_usuario_by_email(email):
    """
    Retorna os detalhes de um usuário pelo e-mail.

    Parâmetros:
        email (str): E-mail do usuário.

    Retorna:
        dict | None: Dicionário com os dados do usuário ou None se não encontrado.
    """
    query = "SELECT * FROM usuarios WHERE email = ?"
    result = execute_query(query, (email,))
    return dict(result[0]) if result else None

from database.connection import execute_query

def get_usuario_by_id(user_id):
    """
    Retorna os detalhes de um usuário pelo ID.

    Parâmetros:
        user_id (int): ID do usuário.

    Retorna:
        dict | None: Dicionário com os dados do usuário ou None se não encontrado.
    """
    query = "SELECT * FROM usuarios WHERE id = ?"
    result = execute_query(query, (user_id,))
    return dict(result[0]) if result else None


def get_all_usuarios():
    """
    Retorna a lista de todos os usuários cadastrados.

    Retorna:
        list: Lista de dicionários com os dados dos usuários.
    """
    query = "SELECT * FROM usuarios"
    result = execute_query(query)
    return [dict(row) for row in result] if result else []

def update_usuario(user_id, nome=None, email=None, funcao=None, empresa=None, tipo=None, senha=None):
    """
    Atualiza os dados de um usuário no banco de dados.

    Parâmetros:
        user_id (int): ID do usuário a ser atualizado.
        nome (str, opcional): Novo nome.
        email (str, opcional): Novo e-mail.
        funcao (str, opcional): Nova função.
        empresa (str, opcional): Nova empresa.
        tipo (str, opcional): Novo tipo de usuário ('ADMIN' ou 'OPE').
        senha (str, opcional): Nova senha (será armazenada como hash se fornecida).

    Retorna:
        bool: True se a atualização foi bem-sucedida, False caso contrário.
    """
    fields = []
    values = []

    if nome:
        fields.append("nome = ?")
        values.append(nome)
    if email:
        fields.append("email = ?")
        values.append(email)
    if funcao:
        fields.append("funcao = ?")
        values.append(funcao)
    if empresa:
        fields.append("empresa = ?")
        values.append(empresa)
    if tipo:
        fields.append("tipo = ?")
        values.append(tipo)
    if senha:
        fields.append("senha_hash = ?")
        values.append(hash_password(senha))

    if not fields:
        return False  # Nenhuma atualização a ser feita

    values.append(user_id)
    query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = ?"

    execute_query(query, tuple(values))
    return True

def delete_usuario(user_id):
    """
    Exclui um usuário do banco de dados.

    Parâmetros:
        user_id (int): ID do usuário a ser excluído.

    Retorna:
        bool: True se a exclusão foi bem-sucedida, False caso contrário.
    """
    query = "DELETE FROM usuarios WHERE id = ?"
    execute_query(query, (user_id,))
    return True
