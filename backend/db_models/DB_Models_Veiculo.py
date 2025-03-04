# C:\Users\Novaes Engenharia\github - deploy\Frotas\backend\db_models\DB_Models_Veiculo.py

import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import sqlite3
from backend.database.db_fleet import get_db_connection  # Corrige o caminho do import


def create_veiculo(placa, renavam, modelo, ano_fabricacao, capacidade_tanque, hodometro_atual, fotos):
    """Cria um novo veículo no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO veiculos (placa, renavam, modelo, ano_fabricacao, capacidade_tanque, hodometro_atual, fotos) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (placa, renavam, modelo, ano_fabricacao, capacidade_tanque, hodometro_atual, fotos))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_veiculo_by_id(veiculo_id):
    """Retorna um veículo pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM veiculos WHERE id = ?", (veiculo_id,))
    veiculo = cursor.fetchone()
    conn.close()
    return veiculo

def get_veiculo_by_placa(placa):
    """Retorna um veículo pela placa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM veiculos WHERE placa = ?", (placa,))
    veiculo = cursor.fetchone()
    conn.close()
    return veiculo

def get_veiculo_by_renavam(renavam):
    """Retorna um veículo pelo Renavam."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM veiculos WHERE renavam = ?", (renavam,))
    veiculo = cursor.fetchone()
    conn.close()
    return veiculo

def get_all_veiculos():
    """Retorna todos os veículos cadastrados como dicionários para evitar erros com sqlite3.Row."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM veiculos")
    veiculos = cursor.fetchall()
    conn.close()
    
    # Converter cada sqlite3.Row para um dicionário antes de retornar
    return [dict(veiculo) for veiculo in veiculos]

def get_KM_veiculo_placa(placa):
    """Retorna apenas o KM atual de um veículo a partir da placa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT hodometro_atual FROM veiculos WHERE placa = ?", (placa,))
    km = cursor.fetchone()
    conn.close()
    return km["hodometro_atual"] if km else None

def update_veiculo(veiculo_id, placa, renavam, modelo, ano_fabricacao, capacidade_tanque, hodometro_atual, fotos):
    """Atualiza todas as informações de um veículo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE veiculos SET placa=?, renavam=?, modelo=?, ano_fabricacao=?, capacidade_tanque=?, 
        hodometro_atual=?, fotos=? WHERE id=?
    ''', (placa, renavam, modelo, ano_fabricacao, capacidade_tanque, hodometro_atual, fotos, veiculo_id))
    
    conn.commit()
    conn.close()
    return True

def update_veiculos_KM(placa, novo_km):
    """Atualiza apenas o KM de um veículo a partir da placa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE veiculos SET hodometro_atual = ? WHERE placa = ?", (novo_km, placa))
    conn.commit()
    conn.close()
    return True

def delete_veiculo(veiculo_id):
    """Exclui um veículo pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
    conn.commit()
    conn.close()
    return True

def delete_veiculo_por_placa(placa):
    """Exclui um veículo pelo número da placa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM veiculos WHERE placa = ?", (placa,))
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    print("Módulo de gerenciamento de veículos carregado com sucesso!")
