"""
database/models/models_abastecimentos.py

Este módulo contém o modelo de Abastecimentos e suas operações no banco de dados.

Funcionalidades:
- Registrar abastecimentos e associá-los a um veículo.
- Fazer upload da nota fiscal para o Google Drive.
- Listar, buscar, atualizar e excluir abastecimentos.
- Calcular o custo médio por KM rodado.
"""

import sqlite3
from database.connection import get_db_connection, execute_query, get_last_inserted_id
from services.google_drive_service import upload_file_to_drive
from database.models.models_veiculos import get_veiculo_by_id, update_veiculo, get_veiculo_id

# ID da pasta no Google Drive onde as notas fiscais serão armazenadas
INVOICES_FOLDER_ID = "1yv2nWX5wiJiHc2-sHiykgYclUy8yw1Hb"  # Substitua pelo ID correto

from database.models.models_veiculos import get_veiculo_id

def create_abastecimento(placa, quantidade_litros, km_abastecimento, tipo_combustivel, valor_total, nota_fiscal=None):
    """
    Registra um novo abastecimento no banco de dados e faz upload da nota fiscal para o Google Drive.

    Parâmetros:
        placa (str): Placa do veículo abastecido.
        quantidade_litros (float): Quantidade de litros abastecidos.
        km_abastecimento (int): Quilometragem registrada no momento do abastecimento.
        tipo_combustivel (str): Tipo de combustível ('GASOLINA', 'ÁLCOOL', 'DIESEL', 'GÁS').
        valor_total (float): Valor total pago no abastecimento.
        nota_fiscal (str, opcional): Link da nota fiscal no Google Drive.

    Retorna:
        int: ID do abastecimento inserido.
    """

    # Obtém o ID do veículo com base na placa
    veiculo_id = get_veiculo_id(placa)
    if not veiculo_id:
        raise ValueError("Veículo não encontrado!")

    # Insere os dados no banco
    query = """
    INSERT INTO abastecimentos (veiculo_id, quantidade_litros, km_abastecimento, tipo_combustivel, valor_total, nota_fiscal)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (veiculo_id, quantidade_litros, km_abastecimento, tipo_combustivel, valor_total, nota_fiscal))
    abastecimento_id = get_last_inserted_id()

    # Atualiza a quilometragem do veículo
    update_veiculo(veiculo_id, km_atual=km_abastecimento)

    return abastecimento_id


def get_abastecimento_by_id(abastecimento_id):
    """
    Retorna os detalhes de um abastecimento específico.

    Parâmetros:
        abastecimento_id (int): ID do abastecimento.

    Retorna:
        dict | None: Dicionário com os dados do abastecimento ou None se não encontrado.
    """
    query = "SELECT * FROM abastecimentos WHERE id = ?"
    result = execute_query(query, (abastecimento_id,))
    return dict(result[0]) if result else None

def get_all_abastecimentos():
    """
    Retorna a lista de todos os abastecimentos cadastrados.

    Retorna:
        list: Lista de dicionários com os dados dos abastecimentos.
    """
    query = """
    SELECT a.*, v.placa FROM abastecimentos a
    JOIN veiculos v ON a.veiculo_id = v.id
    ORDER BY a.data_abastecimento DESC
    """
    result = execute_query(query)
    return [dict(row) for row in result] if result else []

def update_abastecimento(abastecimento_id, quantidade_litros, km_abastecimento, tipo_combustivel, valor_total):
    """
    Atualiza um registro de abastecimento existente no banco de dados.

    Parâmetros:
        abastecimento_id (int): ID do abastecimento a ser atualizado.
        quantidade_litros (float): Nova quantidade de litros abastecidos.
        km_abastecimento (int): Novo valor de quilometragem no momento do abastecimento.
        tipo_combustivel (str): Novo tipo de combustível.
        valor_total (float): Novo valor total pago pelo abastecimento.

    Retorna:
        bool: True se a atualização foi bem-sucedida, False caso contrário.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE abastecimentos
            SET quantidade_litros = ?, km_abastecimento = ?, tipo_combustivel = ?, valor_total = ?
            WHERE id = ?
        """, (quantidade_litros, km_abastecimento, tipo_combustivel, valor_total, abastecimento_id))

        conn.commit()
        return cursor.rowcount > 0  # Retorna True se alguma linha foi alterada

    except sqlite3.Error as e:
        print("❌ Erro ao atualizar abastecimento:", e)
        return False

    finally:
        conn.close()

def delete_abastecimento(abastecimento_id):
    """
    Exclui um abastecimento do banco de dados.

    Parâmetros:
        abastecimento_id (int): ID do abastecimento a ser excluído.

    Retorna:
        bool: True se a exclusão foi bem-sucedida, False caso contrário.
    """
    query = "DELETE FROM abastecimentos WHERE id = ?"
    execute_query(query, (abastecimento_id,))
    return True

def get_all_abastecimentos():
    """
    Retorna a lista de todos os abastecimentos cadastrados.

    Retorna:
        list: Lista de dicionários com os dados dos abastecimentos.
    """
    query = """
    SELECT a.*, v.placa FROM abastecimentos a
    JOIN veiculos v ON a.veiculo_id = v.id
    ORDER BY a.data_abastecimento DESC
    """
    result = execute_query(query)
    return [dict(row) for row in result] if result else []

def calcular_custo_por_km(veiculo_id):
    """
    Calcula o custo médio por KM rodado baseado no histórico de abastecimentos.

    Parâmetros:
        veiculo_id (int): ID do veículo.

    Retorna:
        float | None: Custo médio por KM ou None se não houver dados suficientes.
    """
    query = """
    SELECT km_abastecimento, valor_total
    FROM abastecimentos
    WHERE veiculo_id = ?
    ORDER BY data_abastecimento ASC
    """

    abastecimentos = execute_query(query, (veiculo_id,))
    
    if not abastecimentos or len(abastecimentos) < 2:
        return None  # Não há dados suficientes para calcular

    km_inicial = abastecimentos[0]["km_abastecimento"]
    km_final = abastecimentos[-1]["km_abastecimento"]
    total_gasto = sum(a["valor_total"] for a in abastecimentos)

    if km_final > km_inicial:
        custo_por_km = total_gasto / (km_final - km_inicial)
        return round(custo_por_km, 2)

    return None

# ===========================
# ✅ EXPORTANDO FUNÇÕES
# ===========================
__all__ = [
    "get_all_abastecimentos",
    "create_abastecimento",
    "update_abastecimento",
    "delete_abastecimento",
    "get_abastecimento_by_id",
    "calcular_custo_por_km"
]
