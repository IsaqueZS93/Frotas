# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\screens\Screen_Checklist_lists.py

import streamlit as st
import sys
import os
from datetime import datetime

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos módulos do projeto
from backend.db_models.DB_Models_checklists import (
    get_all_checklists, 
    get_checklists_by_placa, 
    get_checklists_by_id, 
    delete_checklist
)
from backend.db_models.DB_Models_Veiculo import get_all_veiculos
from backend.db_models.DB_Models_User import get_user_by_id
from backend.services.Service_Google_Drive import search_files, list_files_in_folder, get_folder_id_by_name

# 🔹 ID da pasta principal "Checklists" no Google Drive
PASTA_CHECKLISTS_ID = "10T2UHhc-wQXWRDj-Kc5F_dAHUM5F1TrK"

def checklist_list_screen():
    """Tela para listar, editar e excluir checklists."""

    st.title("📋 Listagem e Gerenciamento de Checklists")

    # 🔹 Verifica se o usuário está logado
    if "user_id" not in st.session_state:
        st.error("Você precisa estar logado para acessar esta tela.")
        return

    user_type = st.session_state["user_type"]

    # 🔹 Apenas usuários ADMIN podem acessar
    if user_type != "ADMIN":
        st.error("Você não tem permissão para acessar esta tela.")
        return

    # 🔹 Filtros de busca
    st.subheader("🔍 Filtros de Busca")
    col1, col2, col3 = st.columns(3)

    with col1:
        placa_filter = st.selectbox("📌 Filtrar por Placa", ["Todas"] + [veiculo["placa"] for veiculo in get_all_veiculos()])
    with col2:
        data_filter = st.date_input("📅 Filtrar por Data", value=None)
    with col3:
        usuario_filter = st.text_input("👤 Filtrar por ID Usuário ou Nome")

    # 🔹 Buscar checklists com base nos filtros aplicados
    if placa_filter != "Todas":
        checklists = get_checklists_by_placa(placa_filter)
    else:
        checklists = get_all_checklists()

    if data_filter:
        checklists = [c for c in checklists if c["data_hora"].startswith(data_filter.strftime("%d/%m/%Y"))]

    if usuario_filter:
        checklists = [c for c in checklists if usuario_filter.lower() in str(c["id_usuario"]).lower()]

    # 🔹 Exibir lista de checklists
    st.subheader("📑 Checklists Registrados")
    if not checklists:
        st.info("Nenhum checklist encontrado com os filtros selecionados.")
        return

    for checklist in checklists:
        with st.expander(f"📌 Checklist ID: {checklist['id']} | Placa: {checklist['placa']} | Data: {checklist['data_hora']}"):
            user_info = get_user_by_id(checklist["id_usuario"])
            usuario_nome = user_info["nome_completo"] if user_info else "Usuário desconhecido"

            # 🔹 Exibir informações do checklist
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"👤 **Usuário:** {usuario_nome} (ID: {checklist['id_usuario']})")
                st.write(f"🕒 **Data/Hora:** {checklist['data_hora']}")
                st.write(f"📌 **Placa do Veículo:** {checklist['placa']}")
                st.write(f"📊 **KM Atual:** {checklist['km_atual']} km")
                st.write(f"📊 **KM Informado:** {checklist['km_informado']} km")
                st.write(f"🛞 **Condição dos Pneus:** {'✅ OK' if checklist['pneus_ok'] else '❌ Problema'}")
                st.write(f"💡 **Faróis e Setas:** {'✅ OK' if checklist['farois_setas_ok'] else '❌ Problema'}")
                st.write(f"🛑 **Freios:** {'✅ OK' if checklist['freios_ok'] else '❌ Problema'}")
                st.write(f"🛢️ **Nível do Óleo:** {'✅ OK' if checklist['oleo_ok'] else '❌ Problema'}")
                st.write(f"🚗 **Vidros e Retrovisores:** {'✅ OK' if checklist['vidros_retrovisores_ok'] else '❌ Problema'}")
                st.write(f"🦺 **Itens de Segurança:** {'✅ OK' if checklist['itens_seguranca_ok'] else '❌ Problema'}")
                st.write(f"📝 **Observações:** {checklist['observacoes'] if checklist['observacoes'] else 'Nenhuma observação registrada.'}")

            # 🔹 Buscar imagens no Google Drive
            with col2:
                st.subheader("📸 Fotos do Veículo")

                # Verifica se há imagens cadastradas no banco
                if checklist["fotos"]:
                    fotos_ids = checklist["fotos"].split("|")

                    # Buscar a pasta da placa dentro da pasta Checklists
                    pasta_veiculo_id = get_folder_id_by_name(checklist["placa"])

                    if pasta_veiculo_id:
                        imagens = list_files_in_folder(pasta_veiculo_id)
                        imagens_encontradas = [img for img in imagens if img["id"] in fotos_ids]

                        if imagens_encontradas:
                            for imagem in imagens_encontradas:
                                st.markdown(f"[🖼 Visualizar Imagem]({imagem['webViewLink']})", unsafe_allow_html=True)
                        else:
                            st.info("📌 Nenhuma imagem encontrada na pasta correspondente do Google Drive.")
                    else:
                        st.info("📌 Nenhuma pasta correspondente encontrada para esta placa no Google Drive.")
                else:
                    st.info("📌 Nenhuma imagem foi anexada a este checklist.")

            # 🔹 Botão de exclusão do checklist
            if st.button(f"🗑️ Excluir Checklist {checklist['id']}", key=f"delete_{checklist['id']}"):
                delete_checklist(checklist["id"])
                st.success(f"✅ Checklist {checklist['id']} excluído com sucesso!")
                st.rerun()

# Executar a tela se for o script principal
if __name__ == "__main__":
    checklist_list_screen()
