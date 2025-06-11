"""
database/connection.py

Este módulo gerencia a conexão com o banco de dados SQLite para o sistema Fleet Management.

Funcionalidades:
- Criar e gerenciar a conexão com o banco de dados.
- Criar automaticamente as tabelas caso não existam ou estejam desatualizadas.
- Fornecer funções auxiliares para executar consultas.
"""

import sqlite3
import os

# Nome do banco de dados
DATABASE_NAME = "fleet_management.db"

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.

    Retorna:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn

def column_exists(table_name, column_name):
    """
    Verifica se uma coluna existe em uma tabela específica.

    Parâmetros:
        table_name (str): Nome da tabela.
        column_name (str): Nome da coluna a ser verificada.

    Retorna:
        bool: True se a coluna existir, False caso contrário.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row["name"] for row in cursor.fetchall()]
        return column_name in columns

def create_tables():
    """
    Cria ou atualiza as tabelas do banco de dados.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # ✅ Criando tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                data_nascimento TEXT NOT NULL,
                funcao TEXT NOT NULL,
                empresa TEXT NOT NULL,
                tipo TEXT CHECK(tipo IN ('ADMIN', 'OPE')) NOT NULL,
                senha_hash TEXT NOT NULL,
                cnh_foto TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ✅ Criando tabela de veículos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa TEXT UNIQUE NOT NULL,
                renavam TEXT UNIQUE NOT NULL,
                modelo TEXT NOT NULL,
                ano INTEGER NOT NULL,
                km_atual INTEGER NOT NULL DEFAULT 0,
                drive_folder_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ✅ Criando tabela de abastecimentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS abastecimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                veiculo_id INTEGER NOT NULL,
                quantidade_litros REAL NOT NULL,
                km_abastecimento INTEGER NOT NULL,
                tipo_combustivel TEXT CHECK(tipo_combustivel IN ('GASOLINA', 'ÁLCOOL', 'DIESEL', 'GÁS')) NOT NULL,
                valor_total REAL NOT NULL,
                nota_fiscal TEXT,
                data_abastecimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (veiculo_id) REFERENCES veiculos (id) ON DELETE CASCADE
            );
        """)

        # ✅ Criando tabela de checklists (se não existir)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                veiculo_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                tipo TEXT CHECK(tipo IN ('INICIO', 'FIM')) NOT NULL,
                km_atual INTEGER NOT NULL,
                pneus_ok BOOLEAN NOT NULL,
                farois_ok BOOLEAN NOT NULL,
                observacoes TEXT,
                fotos JSON,
                data_vistoria TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (veiculo_id) REFERENCES veiculos (id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            );
        """)

        # ✅ Adicionando colunas novas automaticamente
        novas_colunas = {
            "cinto_seguranca_ok": "BOOLEAN NOT NULL DEFAULT 0",
            "freios_ok": "BOOLEAN NOT NULL DEFAULT 0",
            "nivel_oleo_ok": "BOOLEAN NOT NULL DEFAULT 0",
            "vidros_ok": "BOOLEAN NOT NULL DEFAULT 0",
            "retrovisores_ok": "BOOLEAN NOT NULL DEFAULT 0",
            "buzina_ok": "BOOLEAN NOT NULL DEFAULT 0",
            "itens_emergencia_ok": "BOOLEAN NOT NULL DEFAULT 0"
        }

        for coluna, tipo in novas_colunas.items():
            if not column_exists("checklists", coluna):
                cursor.execute(f"ALTER TABLE checklists ADD COLUMN {coluna} {tipo};")
                print(f"✅ Coluna '{coluna}' adicionada à tabela 'checklists'.")

        # ✅ Confirmando alterações no banco de dados
        conn.commit()
        print("✅ Tabelas verificadas/atualizadas com sucesso!")

def execute_query(query, params=()):
    """
    Executa uma consulta SQL no banco de dados.

    Parâmetros:
        query (str): Consulta SQL a ser executada.
        params (tuple): Parâmetros da consulta.

    Retorna:
        list[sqlite3.Row] | None: Retorna os resultados se for uma consulta SELECT.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if query.strip().upper().startswith("SELECT"):
            return cursor.fetchall()  # Retorna os resultados da consulta
        
        conn.commit()  # Para INSERT, UPDATE, DELETE
        return None

def get_last_inserted_id():
    """
    Retorna o ID do último registro inserido no banco de dados.

    Retorna:
        int: ID do último registro inserido.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_insert_rowid();")
        return cursor.fetchone()[0]

if __name__ == "__main__":
    """
    Se este arquivo for executado diretamente, ele criará/verificará as tabelas do banco de dados.
    """
    create_tables()
    print("\n✅ Estrutura de tabelas criada/verificada com sucesso!")
