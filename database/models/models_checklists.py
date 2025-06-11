"""
database/models/models_checklists.py

Este módulo contém o modelo de Checklists e suas operações no banco de dados.

Funcionalidades:
- Registrar checklists diários (INÍCIO e FIM do dia).
- Fazer upload de fotos para o Google Drive.
- Criar alertas para veículos com problemas.
- Atualizar a quilometragem do veículo automaticamente.
"""

import sqlite3
import json
from database.connection import get_db_connection, execute_query, get_last_inserted_id
from services.google_drive_service import upload_file_to_drive
from database.models.models_veiculos import update_veiculo

# ID da pasta no Google Drive onde as imagens dos checklists serão armazenadas
CHECKLISTS_FOLDER_ID = "ID_DA_PASTA_CHECKLISTS"  # Altere para o ID correto

def create_checklist(
    veiculo_id, usuario_id, tipo, km_atual, 
    pneus_ok, farois_ok, cinto_seguranca_ok, freios_ok, nivel_oleo_ok, 
    vidros_ok, retrovisores_ok, buzina_ok, itens_emergencia_ok, 
    observacoes=None, fotos_paths=None  # 🔹 Agora fotos_paths pode ser None
):
    """
    Registra um novo checklist no banco de dados e faz upload das imagens para o Google Drive.

    Parâmetros:
        veiculo_id (int): ID do veículo.
        usuario_id (int): ID do usuário que realizou a vistoria.
        tipo (str): Tipo do checklist ('INICIO' ou 'FIM').
        km_atual (int): Quilometragem registrada no momento da vistoria.
        pneus_ok (bool): Pneus estão em boas condições.
        farois_ok (bool): Faróis estão funcionando corretamente.
        cinto_seguranca_ok (bool): O cinto de segurança está funcionando?
        freios_ok (bool): Os freios estão em boas condições?
        nivel_oleo_ok (bool): O nível de óleo do motor está adequado?
        vidros_ok (bool): Todos os vidros estão intactos e sem trincas?
        retrovisores_ok (bool): Os retrovisores estão ajustados corretamente?
        buzina_ok (bool): A buzina está funcionando?
        itens_emergencia_ok (bool): O veículo possui triângulo, chave de roda e estepe?
        observacoes (str, opcional): Observações adicionais.
        fotos_paths (list, opcional): Lista de caminhos locais das fotos tiradas.

    Retorna:
        int: ID do checklist inserido.
    """
    # 🔹 Garante que fotos_paths sempre seja uma lista válida
    if not fotos_paths:
        fotos_paths = []

    # Upload das fotos para o Google Drive e armazenamento dos links
    fotos_drive_links = []
    for foto_path in fotos_paths:
        upload_result = upload_file_to_drive(foto_path, "image/jpeg", CHECKLISTS_FOLDER_ID)
        if upload_result and "id" in upload_result:
            foto_link = f"https://drive.google.com/file/d/{upload_result['id']}/view"
            fotos_drive_links.append(foto_link)

    fotos_json = json.dumps(fotos_drive_links) if fotos_drive_links else None

    # Insere os dados no banco
    query = """
    INSERT INTO checklists (
        veiculo_id, usuario_id, tipo, km_atual, pneus_ok, farois_ok, 
        cinto_seguranca_ok, freios_ok, nivel_oleo_ok, vidros_ok, 
        retrovisores_ok, buzina_ok, itens_emergencia_ok, observacoes, fotos
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    execute_query(query, (
        veiculo_id, usuario_id, tipo, km_atual, pneus_ok, farois_ok, 
        cinto_seguranca_ok, freios_ok, nivel_oleo_ok, vidros_ok, 
        retrovisores_ok, buzina_ok, itens_emergencia_ok, observacoes, fotos_json
    ))
    checklist_id = get_last_inserted_id()

    # Atualiza a quilometragem do veículo ao final do dia
    if tipo == "FIM":
        update_veiculo(veiculo_id, km_atual=km_atual)

    return checklist_id

def get_checklist_by_id(checklist_id):
    """
    Retorna os detalhes de um checklist específico.

    Parâmetros:
        checklist_id (int): ID do checklist.

    Retorna:
        dict | None: Dicionário com os dados do checklist ou None se não encontrado.
    """
    query = "SELECT * FROM checklists WHERE id = ?"
    result = execute_query(query, (checklist_id,))
    return dict(result[0]) if result else None

def get_checklists_by_veiculo(veiculo_id):
    """
    Retorna todos os checklists associados a um veículo.

    Parâmetros:
        veiculo_id (int): ID do veículo.

    Retorna:
        list: Lista de dicionários com os checklists do veículo.
    """
    query = "SELECT * FROM checklists WHERE veiculo_id = ? ORDER BY data_vistoria DESC"
    result = execute_query(query, (veiculo_id,))
    return [dict(row) for row in result] if result else []

def get_last_checklist(veiculo_id):
    """
    Retorna o último checklist cadastrado para um veículo específico.

    Parâmetros:
        veiculo_id (int): ID do veículo.

    Retorna:
        dict | None: Último checklist do veículo ou None se não houver registros.
    """
    query = "SELECT * FROM checklists WHERE veiculo_id = ? ORDER BY data_vistoria DESC LIMIT 1"
    result = execute_query(query, (veiculo_id,))
    return dict(result[0]) if result else None

def get_alertas_checklists():
    """
    Retorna uma lista de veículos que apresentaram problemas nos checklists.

    Retorna:
        list: Lista de alertas contendo ID do veículo e descrição do problema.
    """
    query = """
    SELECT v.placa, c.*
    FROM checklists c
    JOIN veiculos v ON c.veiculo_id = v.id
    WHERE 
        c.pneus_ok = 0 OR c.farois_ok = 0 OR c.cinto_seguranca_ok = 0 OR 
        c.freios_ok = 0 OR c.nivel_oleo_ok = 0 OR c.vidros_ok = 0 OR 
        c.retrovisores_ok = 0 OR c.buzina_ok = 0 OR c.itens_emergencia_ok = 0
    ORDER BY c.data_vistoria DESC
    """
    result = execute_query(query)
    
    alertas = []
    for row in result:
        problemas = []
        if not row["pneus_ok"]: problemas.append("Pneus danificados")
        if not row["farois_ok"]: problemas.append("Faróis com defeito")
        if not row["cinto_seguranca_ok"]: problemas.append("Cinto de segurança inoperante")
        if not row["freios_ok"]: problemas.append("Freios comprometidos")
        if not row["nivel_oleo_ok"]: problemas.append("Óleo do motor abaixo do nível")
        if not row["vidros_ok"]: problemas.append("Vidros trincados")
        if not row["retrovisores_ok"]: problemas.append("Retrovisores desalinhados")
        if not row["buzina_ok"]: problemas.append("Buzina não funciona")
        if not row["itens_emergencia_ok"]: problemas.append("Kit de emergência incompleto")

        alertas.append({
            "placa": row["placa"],
            "problemas": problemas,
            "observacoes": row["observacoes"],
            "data_vistoria": row["data_vistoria"]
        })

    return alertas

def delete_checklist(checklist_id):
    """
    Exclui um checklist do banco de dados.

    Retorna:
        bool: True se a exclusão foi bem-sucedida.
    """
    query = "DELETE FROM checklists WHERE id = ?"
    execute_query(query, (checklist_id,))
    return True

def get_all_checklists():
    """
    Retorna todos os checklists cadastrados no banco de dados, incluindo a placa do veículo.

    Retorna:
        list[dict]: Lista de dicionários com os checklists registrados.
    """
    query = """
    SELECT c.*, v.placa
    FROM checklists c
    JOIN veiculos v ON c.veiculo_id = v.id
    ORDER BY c.data_vistoria DESC
    """
    result = execute_query(query)
    return [dict(row) for row in result] if result else []

