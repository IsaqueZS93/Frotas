# C:\Users\Novaes Engenharia\github - deploy\Frotas\backend\database\db_fleet.py

import sqlite3

# Nome do banco de dados
DB_NAME = "fleet_management.db"

def get_db_connection():
    """Abre uma conexão com o banco de dados e permite acessar colunas pelo nome."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Permite acessar os resultados como dicionários
    return conn

def create_database():
    """Cria o banco de dados e as tabelas se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criar tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            cnh TEXT UNIQUE NOT NULL,
            contato TEXT NOT NULL,
            validade_cnh TEXT NOT NULL,
            funcao TEXT NOT NULL,
            empresa TEXT NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('ADMIN', 'OPE')) NOT NULL
        )
    ''')

    # Criar tabela de veículos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE NOT NULL,
            renavam TEXT UNIQUE NOT NULL,
            modelo TEXT NOT NULL,
            ano_fabricacao INTEGER NOT NULL,
            capacidade_tanque REAL NOT NULL,
            hodometro_atual INTEGER NOT NULL,
            fotos TEXT  -- Links das fotos armazenadas no Google Drive
        )
    ''')

    # Criar tabela de checklists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            tipo TEXT CHECK(tipo IN ('INICIO', 'FIM')) NOT NULL,
            data_hora TEXT NOT NULL,
            placa TEXT NOT NULL,
            km_atual INTEGER NOT NULL,
            km_informado INTEGER NOT NULL,
            pneus_ok BOOLEAN NOT NULL,
            farois_setas_ok BOOLEAN NOT NULL,
            freios_ok BOOLEAN NOT NULL,
            oleo_ok BOOLEAN NOT NULL,
            vidros_retrovisores_ok BOOLEAN NOT NULL,
            itens_seguranca_ok BOOLEAN NOT NULL,
            observacoes TEXT,
            fotos TEXT,  -- Links das fotos no Google Drive
            FOREIGN KEY (placa) REFERENCES veiculos (placa),
            FOREIGN KEY (id_usuario) REFERENCES users (id)
        )
    ''')

    # Criar tabela de abastecimentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS abastecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            placa TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            km_atual INTEGER NOT NULL,
            km_abastecimento INTEGER NOT NULL,
            quantidade_litros REAL NOT NULL,
            tipo_combustivel TEXT CHECK(tipo_combustivel IN ('Gasolina', 'Diesel', 'Etanol', 'GNV')) NOT NULL,
            valor_total REAL NOT NULL,
            valor_por_litro REAL NOT NULL,
            nota_fiscal TEXT,  -- Link da imagem da nota fiscal
            observacoes TEXT,
            FOREIGN KEY (placa) REFERENCES veiculos (placa),
            FOREIGN KEY (id_usuario) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

def column_exists(table_name, column_name):
    """
    Verifica se uma coluna existe dentro de uma determinada tabela no banco de dados.

    Args:
        table_name (str): Nome da tabela.
        column_name (str): Nome da coluna.

    Returns:
        bool: True se a coluna existir, False caso contrário.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row["name"] for row in cursor.fetchall()]
    
    conn.close()
    
    return column_name in columns

if __name__ == "__main__":
    create_database()
    print("✅ Banco de dados atualizado com sucesso!")

    # Teste da função column_exists
    tabela = "abastecimentos"
    coluna = "placa"
    existe = column_exists(tabela, coluna)
    print(f"🔍 A coluna '{coluna}' existe na tabela '{tabela}'? {existe}")
