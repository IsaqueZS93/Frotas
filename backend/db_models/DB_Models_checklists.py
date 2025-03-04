# C:\Users\Novaes Engenharia\github - deploy\Frotas\backend\db_models\DB_Models_checklists.py

import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import sqlite3
from datetime import datetime
from backend.database.db_fleet import get_db_connection  # Corrige o caminho do import

def create_checklist(id_usuario, tipo, placa, km_atual, km_informado, pneus_ok, farois_setas_ok, 
                     freios_ok, oleo_ok, vidros_retrovisores_ok, itens_seguranca_ok, observacoes, fotos):
    """
    Insere um novo checklist no banco de dados.

    Args:
        id_usuario (int): ID do usuário que preencheu o checklist.
        tipo (str): Tipo do checklist ("INICIO" ou "FIM").
        placa (str): Placa do veículo.
        km_atual (int): KM atual do veículo.
        km_informado (int): KM informado pelo usuário.
        pneus_ok (bool): Condição dos pneus.
        farois_setas_ok (bool): Condição dos faróis e setas.
        freios_ok (bool): Condição dos freios.
        oleo_ok (bool): Condição do nível do óleo.
        vidros_retrovisores_ok (bool): Condição dos vidros e retrovisores.
        itens_seguranca_ok (bool): Condição dos itens de segurança e emergência.
        observacoes (str): Observações gerais.
        fotos (str): Caminho das fotos associadas ao checklist.

    Returns:
        bool: True se o checklist for criado com sucesso.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    cursor.execute('''
        INSERT INTO checklists (id_usuario, tipo, data_hora, placa, km_atual, km_informado, 
                                pneus_ok, farois_setas_ok, freios_ok, oleo_ok, vidros_retrovisores_ok, 
                                itens_seguranca_ok, observacoes, fotos) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_usuario, tipo, data_hora, placa, km_atual, km_informado, pneus_ok, farois_setas_ok, 
          freios_ok, oleo_ok, vidros_retrovisores_ok, itens_seguranca_ok, observacoes, fotos))
    
    conn.commit()
    conn.close()
    return True

def get_checklists_by_id(checklist_id):
    """Retorna um checklist pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checklists WHERE id = ?", (checklist_id,))
    checklist = cursor.fetchone()
    conn.close()
    return checklist

def get_checklists_by_placa(placa):
    """Retorna todos os checklists de um veículo pela placa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checklists WHERE placa = ?", (placa,))
    checklists = cursor.fetchall()
    conn.close()
    return checklists

def get_checklists_by_id_usuario(id_usuario):
    """Retorna todos os checklists feitos por um usuário específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checklists WHERE id_usuario = ?", (id_usuario,))
    checklists = cursor.fetchall()
    conn.close()
    return checklists

def get_all_checklists():
    """Retorna todos os checklists cadastrados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checklists")
    checklists = cursor.fetchall()
    conn.close()
    return checklists

def get_all_checklists3():
    """Retorna todos os checklists cadastrados com colunas explicitamente definidas."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Agora a consulta seleciona as colunas na mesma ordem esperada no código
    cursor.execute("""
        SELECT id, id_usuario, tipo, data_hora, placa, km_atual, km_informado,
               pneus_ok, farois_setas_ok, freios_ok, oleo_ok, vidros_retrovisores_ok,
               itens_seguranca_ok, observacoes, fotos
        FROM checklists
        ORDER BY data_hora DESC
    """)

    checklists = cursor.fetchall()
    conn.close()
    return checklists


def get_all_checklists2():
    """Retorna todos os checklists cadastrados com colunas explicitamente definidas."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Agora a consulta seleciona as colunas na mesma ordem da função `load_checklists()`
    cursor.execute("""
        SELECT id, id_usuario, tipo, data_hora, placa, km_atual, km_informado,
               pneus_ok, farois_setas_ok, freios_ok, oleo_ok, vidros_retrovisores_ok,
               itens_seguranca_ok, observacoes, fotos
        FROM checklists
        ORDER BY data_hora DESC
    """)

    checklists = cursor.fetchall()
    conn.close()
    return checklists


def get_alertas_checklists():
    """
    Retorna uma lista de alertas contendo a placa do veículo e a descrição dos problemas identificados.
    
    Apenas veículos que apresentaram falhas serão listados.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT placa, data_hora, 
               CASE 
                   WHEN pneus_ok = 0 THEN 'Pneus em más condições'
                   WHEN farois_setas_ok = 0 THEN 'Faróis/setas com defeito'
                   WHEN freios_ok = 0 THEN 'Freios com problema'
                   WHEN oleo_ok = 0 THEN 'Óleo em nível inadequado'
                   WHEN vidros_retrovisores_ok = 0 THEN 'Vidros/retrovisores desalinhados'
                   WHEN itens_seguranca_ok = 0 THEN 'Itens de segurança ausentes'
               END as problema
        FROM checklists
        WHERE pneus_ok = 0 OR farois_setas_ok = 0 OR freios_ok = 0 
              OR oleo_ok = 0 OR vidros_retrovisores_ok = 0 OR itens_seguranca_ok = 0
    ''')
    alertas = cursor.fetchall()
    conn.close()
    return alertas

def get_checklists_KMs():
    """Retorna uma lista com Placa, Data, KM atual e KM informado."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT placa, data_hora, km_atual, km_informado FROM checklists")
    checklists_km = cursor.fetchall()
    conn.close()
    return checklists_km

def delete_checklist(checklist_id):
    """Exclui um checklist pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM checklists WHERE id = ?", (checklist_id,))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    print("✅ Módulo de checklists carregado com sucesso!")
