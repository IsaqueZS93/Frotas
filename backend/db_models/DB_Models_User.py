# C:\Users\Novaes Engenharia\github - deploy\Frotas\backend\db_models\DB_Models_User.py

import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import sqlite3
import bcrypt
from backend.database.db_fleet import get_db_connection  # Corrige o caminho do import


# 🔹 Função para gerar hash de senha
def gerar_hash(senha):
    """Gera um hash seguro para a senha usando bcrypt."""
    try:
        salt = bcrypt.gensalt()  # 🔹 Gera um salt aleatório
        hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)  # 🔹 Gera o hash da senha
        return hashed.decode('utf-8')  # 🔹 Retorna o hash como string (para salvar no banco)
    except Exception as e:
        print(f"[ERRO] Falha ao gerar hash da senha: {e}")
        return None


# 🔹 Função para verificar senha

def verificar_senha(senha_digitada, senha_armazenada):
    """Compara a senha digitada com o hash armazenado no banco de dados, garantindo compatibilidade."""

    try:
        # 🔹 Certifica-se de que os valores não estão vazios
        if not senha_digitada or not senha_armazenada:
            print("[ERRO] Senha digitada ou senha armazenada está vazia!")
            return False

        print(f"[DEBUG] Senha Digitada: {senha_digitada}")
        print(f"[DEBUG] Hash Armazenado no BD: {senha_armazenada}")

        # 🔹 Converte a senha digitada para bytes
        senha_digitada_bytes = senha_digitada.encode('utf-8')

        # 🔹 O hash armazenado no banco de dados já está como string, então convertemos para bytes antes da comparação
        senha_armazenada_bytes = senha_armazenada.encode('utf-8')

        print(f"[DEBUG] Senha Digitada (Bytes): {senha_digitada_bytes}")
        print(f"[DEBUG] Hash Armazenado (Bytes): {senha_armazenada_bytes}")

        # 🔹 Verificação usando bcrypt
        resultado = bcrypt.checkpw(senha_digitada_bytes, senha_armazenada_bytes)

        if resultado:
            print("[SUCESSO] Senha correta!")
        else:
            print("[ERRO] Senha incorreta!")

        return resultado

    except Exception as e:
        print(f"[FATAL ERRO] Erro na verificação da senha: {e}")
        return False

    
def create_user(nome_completo, data_nascimento, email, usuario, cnh, contato, validade_cnh, funcao, empresa, senha_hash, tipo):
    """Cria um novo usuário no banco de dados, armazenando a senha de forma segura."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print(f"[DEBUG] Hash recebido em create_user: {senha_hash} (Tamanho: {len(senha_hash)})")

        cursor.execute('''
            INSERT INTO users (nome_completo, data_nascimento, email, usuario, cnh, contato, validade_cnh, funcao, empresa, senha, tipo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome_completo, data_nascimento, email, usuario, cnh, contato, validade_cnh, funcao, empresa, senha_hash, tipo))
        
        conn.commit()

        # 🔹 Verifica o que foi salvo no banco
        cursor.execute("SELECT senha FROM users WHERE usuario = ?", (usuario,))
        hash_realmente_salvo = cursor.fetchone()[0]
        print(f"[DEBUG] Hash salvo no banco: {hash_realmente_salvo} (Tamanho: {len(hash_realmente_salvo)})")

        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Retorna um usuário pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_cnh(cnh):
    """Retorna um usuário pela CNH."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE cnh = ?", (cnh,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_funcao(funcao):
    """Retorna usuários por função."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE funcao = ?", (funcao,))
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_name_by_id(user_id):
    """Retorna o nome do usuário com base no ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome_completo FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else "Desconhecido"

def get_user_by_nome(nome):
    """Retorna usuários pelo nome."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE nome_completo LIKE ?", ('%' + nome + '%',))
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_email(email):
    """Retorna um usuário pelo email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_usuario(usuario):
    """Retorna um usuário pelo login."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE usuario = ?", (usuario,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_tipo(tipo):
    """Retorna usuários por tipo (ADMIN ou OPE)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE tipo = ?", (tipo,))
    users = cursor.fetchall()
    conn.close()
    return users

def get_all_users():
    """Retorna todos os usuários."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def update_user(user_id, nome_completo, data_nascimento, email, usuario, cnh, contato, validade_cnh, funcao, empresa, tipo, nova_senha=None):
    """Atualiza um usuário. Se nova_senha for fornecida, atualiza a senha também."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if nova_senha:
            cursor.execute('''
                UPDATE users 
                SET nome_completo=?, data_nascimento=?, email=?, usuario=?, cnh=?, contato=?, validade_cnh=?, 
                    funcao=?, empresa=?, tipo=?, senha=? 
                WHERE id=?
            ''', (nome_completo, data_nascimento, email, usuario, cnh, contato, validade_cnh, 
                  funcao, empresa, tipo, nova_senha, user_id))
        else:
            cursor.execute('''
                UPDATE users 
                SET nome_completo=?, data_nascimento=?, email=?, usuario=?, cnh=?, contato=?, validade_cnh=?, 
                    funcao=?, empresa=?, tipo=? 
                WHERE id=?
            ''', (nome_completo, data_nascimento, email, usuario, cnh, contato, validade_cnh, 
                  funcao, empresa, tipo, user_id))

        conn.commit()
        print(f"[INFO] Usuário {user_id} atualizado com sucesso.")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao atualizar usuário {user_id}: {e}")
        return False

    finally:
        conn.close()


def delete_user(user_id):
    """Exclui um usuário pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def comparar_id_users(id_1, id_2):
    """Compara dois IDs de usuário e retorna True se forem iguais."""
    return id_1 == id_2

if __name__ == "__main__":
    print("Módulo de gerenciamento de usuários carregado com sucesso!")
    
def update_user_password(user_id, nova_senha):
    """Atualiza a senha do usuário no banco de dados."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Gerar um novo hash para a nova senha
        senha_hash = gerar_hash(nova_senha)

        # Atualizar no banco de dados
        cursor.execute("UPDATE users SET senha = ? WHERE id = ?", (senha_hash, user_id))
        conn.commit()
        conn.close()

        print(f"[SUCESSO] Senha do usuário ID {user_id} foi atualizada com sucesso.")
        return True

    except Exception as e:
        print(f"[ERRO] Erro ao atualizar a senha do usuário ID {user_id}: {e}")
        return False
    
    
