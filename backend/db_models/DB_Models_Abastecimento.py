# C:\Users\Novaes Engenharia\github - deploy\Frotas\backend\db_models\DB_Models_Abastecimento.py

import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import sqlite3
from datetime import datetime
from backend.database.db_fleet import get_db_connection  # Corrige o caminho do import


def create_abastecimento(id_usuario, placa, data_hora, km_atual, km_abastecimento, quantidade_litros, tipo_combustivel, valor_total, nota_fiscal, observacoes):
    """
    Registra um novo abastecimento no banco de dados.
    O valor por litro é calculado automaticamente.
    """

    if km_abastecimento < km_atual:
        return False, "O KM do abastecimento não pode ser inferior ao KM atual do veículo."

    valor_por_litro = round(valor_total / quantidade_litros, 2) if quantidade_litros > 0 else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO abastecimentos (id_usuario, placa, data_hora, km_atual, km_abastecimento, quantidade_litros, tipo_combustivel, valor_total, valor_por_litro, nota_fiscal, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_usuario, placa, data_hora, km_atual, km_abastecimento, quantidade_litros, tipo_combustivel, valor_total, valor_por_litro, nota_fiscal, observacoes))
        conn.commit()
        return True, "✅ Abastecimento registrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "❌ Erro ao registrar abastecimento."
    finally:
        conn.close()

def get_abastecimento_by_id(id_abastecimento):
    """Retorna um abastecimento pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM abastecimentos WHERE id = ?", (id_abastecimento,))
    abastecimento = cursor.fetchone()
    conn.close()
    return abastecimento

def get_abastecimento_by_placa(placa):
    """Retorna todos os abastecimentos de um determinado veículo (pela placa)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM abastecimentos WHERE placa = ? ORDER BY data_hora DESC", (placa,))
    abastecimentos = cursor.fetchall()
    conn.close()
    return abastecimentos

def get_abastecimento_by_usuario(id_usuario):
    """Retorna todos os abastecimentos registrados por um usuário específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM abastecimentos WHERE id_usuario = ? ORDER BY data_hora DESC", (id_usuario,))
    abastecimentos = cursor.fetchall()
    conn.close()
    return abastecimentos

def get_all_abastecimentos():
    """Retorna todos os abastecimentos registrados no sistema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM abastecimentos ORDER BY data_hora DESC")
    abastecimentos = cursor.fetchall()
    conn.close()
    return abastecimentos

def get_all_abastecimentos_2():
    """
    Retorna todos os abastecimentos registrados no sistema,
    EXCLUINDO os campos 'nota_fiscal' e 'observacoes'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🔹 Apenas os campos necessários, sem 'nota_fiscal' e 'observacoes'
    cursor.execute("""
        SELECT id, id_usuario, placa, data_hora, km_atual, km_abastecimento, 
               quantidade_litros, tipo_combustivel, valor_total
        FROM abastecimentos
        ORDER BY data_hora DESC
    """)
    
    abastecimentos = cursor.fetchall()
    conn.close()
    return abastecimentos

def delete_abastecimento(id_abastecimento):
    """Exclui um abastecimento pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM abastecimentos WHERE id = ?", (id_abastecimento,))
    conn.commit()
    conn.close()
    return True

def get_consumo_veiculo(placa):
    """Calcula o consumo médio do veículo com base nos abastecimentos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT km_abastecimento, quantidade_litros FROM abastecimentos WHERE placa = ? ORDER BY data_hora", (placa,))
    registros = cursor.fetchall()

    if len(registros) < 2:
        return None  # Consumo médio não pode ser calculado com menos de 2 registros.

    total_km = registros[-1]["km_abastecimento"] - registros[0]["km_abastecimento"]
    total_combustivel = sum(r["quantidade_litros"] for r in registros if r["quantidade_litros"] > 0)

    consumo_medio = total_km / total_combustivel if total_combustivel > 0 else 0

    conn.close()
    return round(consumo_medio, 2)

def get_custos_por_veiculo():
    """Retorna um relatório de gastos com combustível por veículo."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT placa, SUM(valor_total) as custo_total, SUM(quantidade_litros) as litros_total 
        FROM abastecimentos GROUP BY placa
    ''')
    custos = cursor.fetchall()
    
    conn.close()
    return custos

def get_ultimo_km_veiculo(placa):
    """
    Retorna o último KM registrado do veículo com base no último abastecimento ou checklist.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    # Primeiro tenta buscar o último abastecimento
    cursor.execute("SELECT km_abastecimento FROM abastecimentos WHERE placa = ? ORDER BY data_hora DESC LIMIT 1", (placa,))
    km_abastecimento = cursor.fetchone()

    if km_abastecimento:
        conn.close()
        return km_abastecimento["km_abastecimento"]

    # Caso não haja abastecimento registrado, busca o KM mais recente do checklist
    cursor.execute("SELECT km_informado FROM checklists WHERE placa = ? ORDER BY data_hora DESC LIMIT 1", (placa,))
    km_checklist = cursor.fetchone()

    conn.close()
    return km_checklist["km_informado"] if km_checklist else 0

def get_next_abastecimento_id():
    """
    Retorna o próximo ID disponível para um novo abastecimento.
    
    Returns:
        int: Próximo ID disponível.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) FROM abastecimentos")
    max_id = cursor.fetchone()[0]
    
    conn.close()
    
    return (max_id + 1) if max_id else 1  # Se não houver registros, retorna 1

if __name__ == "__main__":
    print("✅ Módulo de abastecimentos carregado com sucesso!")

    # Teste de algumas funções
    placa_teste = "ABC1234"
    print(f"🔍 Último KM do veículo {placa_teste}: {get_ultimo_km_veiculo(placa_teste)} km")
    print(f"⛽ Consumo médio do veículo {placa_teste}: {get_consumo_veiculo(placa_teste)} km/L")
