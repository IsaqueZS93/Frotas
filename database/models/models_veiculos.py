"""
database/models/models_veiculos.py

Este módulo contém o modelo de Veículos e suas operações no banco de dados.

Funcionalidades:
- Criar veículos e associá-los ao Google Drive.
- Listar, buscar, atualizar e excluir veículos.
- Armazenar o ID da pasta no Drive para cada veículo.
"""

import sqlite3
from database.connection import get_db_connection, execute_query, get_last_inserted_id
from services.google_drive_service import create_drive_folder
from services.google_drive_service import delete_drive_folder

# ID da pasta principal no Google Drive onde os veículos serão armazenados
IMAGES_VEHICLES_FOLDER_ID = "1QbzMjD8Rtg541ZrkerAUTQTIH-FAeiUL"  # Definido diretamente

def create_veiculo(placa, renavam, modelo, ano, km_atual, observacoes="", fotos=""):
    """
    Cria um novo veículo no banco de dados e gera uma pasta no Google Drive.

    Parâmetros:
        placa (str): Placa do veículo (única).
        renavam (str): Código RENAVAM do veículo (único).
        modelo (str): Modelo do veículo.
        ano (int): Ano de fabricação.
        km_atual (int): Quilometragem atual.
        observacoes (str, opcional): Observações sobre o veículo.
        fotos (str, opcional): Links das fotos do veículo.

    Retorna:
        int: ID do veículo inserido.
    """
    if not IMAGES_VEHICLES_FOLDER_ID:
        raise ValueError("❌ ERRO: ID da pasta 'Imagens Veículos' no Google Drive não foi configurado corretamente!")

    # Criar pasta no Google Drive para o veículo
    try:
        drive_folder_id = create_drive_folder(placa, IMAGES_VEHICLES_FOLDER_ID)
    except Exception as e:
        raise RuntimeError(f"❌ Erro ao criar pasta no Google Drive para {placa}: {str(e)}")

    query = """
    INSERT INTO veiculos (placa, renavam, modelo, ano, km_atual, drive_folder_id, observacoes, fotos)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (placa, renavam, modelo, ano, km_atual, drive_folder_id, observacoes, fotos))
    return get_last_inserted_id()

def get_veiculo_by_id(veiculo_id):
    """
    Retorna os detalhes de um veículo específico.

    Parâmetros:
        veiculo_id (int): ID do veículo.

    Retorna:
        dict | None: Dicionário com os dados do veículo ou None se não encontrado.
    """
    query = """
    SELECT id, placa, renavam, modelo, ano, km_atual, drive_folder_id, observacoes, fotos
    FROM veiculos WHERE id = ?
    """
    result = execute_query(query, (veiculo_id,))
    return dict(result[0]) if result else None

def get_veiculo_id(placa):
    """
    Retorna o ID de um veículo com base na placa.

    Parâmetros:
        placa (str): Placa do veículo.

    Retorna:
        int | None: ID do veículo se encontrado, ou None se não existir.
    """
    query = "SELECT id FROM veiculos WHERE placa = ? LIMIT 1"
    result = execute_query(query, (placa,))
    return result[0]["id"] if result else None

def get_veiculo_by_placa(placa):
    """
    Retorna os detalhes de um veículo pela placa.

    Parâmetros:
        placa (str): Placa do veículo.

    Retorna:
        dict | None: Dicionário com os dados do veículo ou None se não encontrado.
    """
    query = """
    SELECT id, placa, renavam, modelo, ano, km_atual, drive_folder_id, observacoes, fotos
    FROM veiculos WHERE placa = ?
    """
    result = execute_query(query, (placa,))
    return dict(result[0]) if result else None

def get_all_veiculos():
    """
    Retorna a lista de todos os veículos cadastrados.

    Retorna:
        list: Lista de dicionários com os dados dos veículos.
    """
    query = """
    SELECT id, placa, renavam, modelo, ano, km_atual, drive_folder_id, observacoes, fotos
    FROM veiculos
    """
    result = execute_query(query)
    return [dict(row) for row in result] if result else []

def update_veiculo(veiculo_id, placa=None, modelo=None, ano=None, km_atual=None, observacoes=None, fotos=None):
    """
    Atualiza os dados de um veículo no banco de dados.

    Parâmetros:
        veiculo_id (int): ID do veículo a ser atualizado.
        placa (str, opcional): Nova placa.
        modelo (str, opcional): Novo modelo.
        ano (int, opcional): Novo ano.
        km_atual (int, opcional): Nova quilometragem.
        observacoes (str, opcional): Novas observações.
        fotos (str, opcional): Novos links de fotos.

    Retorna:
        bool: True se a atualização foi bem-sucedida, False caso contrário.
    """
    fields = []
    values = []

    if placa:
        fields.append("placa = ?")
        values.append(placa)
    if modelo:
        fields.append("modelo = ?")
        values.append(modelo)
    if ano:
        fields.append("ano = ?")
        values.append(ano)
    if km_atual:
        fields.append("km_atual = ?")
        values.append(km_atual)
    if observacoes is not None:
        fields.append("observacoes = ?")
        values.append(observacoes)
    if fotos is not None:
        fields.append("fotos = ?")
        values.append(fotos)

    if not fields:
        return False  # Nenhuma atualização a ser feita

    values.append(veiculo_id)
    query = f"UPDATE veiculos SET {', '.join(fields)} WHERE id = ?"

    execute_query(query, tuple(values))
    return True

def delete_veiculo(veiculo_id):
    """
    Exclui um veículo do banco de dados e sua pasta associada no Google Drive.

    Parâmetros:
        veiculo_id (int): ID do veículo a ser excluído.

    Retorna:
        bool: True se a exclusão foi bem-sucedida, False caso contrário.
    """
    # Obtém o veículo pelo ID
    veiculo = get_veiculo_by_id(veiculo_id)
    if not veiculo:
        return False  # Se não encontrar, retorna falso

    # Se houver uma pasta associada, exclui do Google Drive
    drive_folder_id = veiculo.get("drive_folder_id")
    if drive_folder_id:
        try:
            delete_drive_folder(drive_folder_id)
        except Exception as e:
            print(f"⚠️ Erro ao excluir a pasta do Google Drive: {e}")

    # Exclui o veículo do banco de dados
    query = "DELETE FROM veiculos WHERE id = ?"
    execute_query(query, (veiculo_id,))
    return True