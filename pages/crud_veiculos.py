"""
pages/crud_veiculos.py

Tela CRUD para gerenciamento de veículos (somente ADMIN).
"""

import sys
import os
import io
import streamlit as st
from datetime import datetime
from database.models.models_veiculos import (
    get_all_veiculos, create_veiculo, update_veiculo, delete_veiculo
)
from services.auth_service import get_user_by_token
from services.google_drive_service import upload_file_to_drive, create_drive_folder, delete_new_folders_from_drive, get_folder_id_by_name, list_files_in_folder, set_public_permission, upload_file_to_drive2

# ==============================
# 📌 ID da pasta principal "Imagens Veículos" no Google Drive
# ==============================
VEICULOS_FOLDER_ID = "1QbzMjD8Rtg541ZrkerAUTQTIH-FAeiUL"

# ==============================
# 🛑 Verificação de Permissão (Apenas ADMIN)
# ==============================
if "token" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.stop()

usuario_logado = get_user_by_token(st.session_state["token"])

if not usuario_logado or usuario_logado["tipo"] != "ADMIN":
    st.warning("🚫 Acesso negado! Apenas administradores podem gerenciar veículos.")
    st.stop()

st.markdown("<h2 style='text-align: center;'>🚗 Gerenciamento de Veículos</h2>", unsafe_allow_html=True)

# ==============================
# 🔹 Formulário para Criar Novo Veículo
# ==============================
with st.expander("➕ Adicionar Novo Veículo"):
    with st.form("form_novo_veiculo"):
        placa = st.text_input("Placa", placeholder="Ex: ABC1234").upper()
        renavam = st.text_input("Renavam", placeholder="Número do Renavam")
        modelo = st.text_input("Modelo", placeholder="Ex: Fiat Uno")
        ano = st.number_input("Ano", min_value=1990, max_value=2030, step=1)
        km_atual = st.number_input("Quilometragem Atual", min_value=0, step=1)

        # Criar pasta específica para a placa no Google Drive
        veiculo_folder_id = create_drive_folder(placa, VEICULOS_FOLDER_ID)

        # Upload de imagens do veículo direto para o Google Drive
        imagens = st.file_uploader(
            "📸 Fotos do Veículo (Frente, Traseira, Laterais, Interior)", 
            type=["jpg", "png", "jpeg"], accept_multiple_files=True
        )

        observacoes = st.text_area("Observações")

        if st.form_submit_button("Salvar Veículo"):
            if placa and modelo and ano:
                image_links = []
                if imagens:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Obtém a data e hora atuais
                    for idx, imagem in enumerate(imagens, start=1):
                        try:
                            file_bytes = io.BytesIO(imagem.read())

                            # Define o nome do arquivo no formato: PLACA_DATA_IDX.jpg
                            filename = f"{placa}_{timestamp}_{idx}.jpg"

                            upload_result = upload_file_to_drive(
                                file_bytes=file_bytes,  
                                filename=filename,  
                                mime_type="image/jpeg", 
                                folder_id=veiculo_folder_id
                            )

                            if upload_result and "id" in upload_result:
                                image_link = f"https://drive.google.com/file/d/{upload_result['id']}/view"
                                image_links.append(image_link)
                            else:
                                st.error(f"❌ Erro ao enviar {filename} para o Google Drive.")

                        except Exception as e:
                            st.error(f"❌ Erro ao processar {filename}: {e}")

                # Cadastra o veículo no banco de dados
                create_veiculo(placa, renavam, modelo, ano, km_atual, observacoes, ",".join(image_links))
                st.success("✅ Veículo cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("⚠️ Todos os campos obrigatórios devem ser preenchidos.")

# ==============================
# 📌 Listagem de Veículos
# ==============================
st.subheader("📋 Veículos Cadastrados")

veiculos = get_all_veiculos()

if not veiculos:
    st.info("🔹 Nenhum veículo cadastrado.")
else:
    for veiculo in veiculos:
        with st.expander(f"🚗 {veiculo['modelo']} - {veiculo['placa']} ({veiculo['ano']})"):
            col1, col2 = st.columns(2)

            with col1:
                st.text(f"📌 Placa: {veiculo['placa']}")
                st.text(f"🆔 Renavam: {veiculo['renavam']}")
                st.text(f"🚗 Modelo: {veiculo['modelo']}")
                st.text(f"📅 Ano: {veiculo['ano']}")
                st.text(f"📏 KM Atual: {veiculo['km_atual']}")

                # Verifica se há observações
                observacoes = (veiculo.get("observacoes") or "").strip()
                if observacoes:
                    st.text(f"📝 Observações: {observacoes}")

            with col2:
                # Buscar o ID da pasta do veículo no Google Drive com base na placa
                veiculo_folder_id = get_folder_id_by_name(veiculo["placa"], VEICULOS_FOLDER_ID)

                if veiculo_folder_id:
                    imagens = list_files_in_folder(veiculo_folder_id)

                    if imagens:
                        st.markdown("📸 **Imagens do Veículo:**")
                        for imagem in imagens:
                            image_id = imagem["id"]
                            image_name = imagem["name"]

                            # 🔹 Força a permissão pública no arquivo antes de gerar o link
                            set_public_permission(image_id)

                            # 🔹 Link correto para exibir imagens publicamente
                            image_link = f"https://drive.google.com/uc?export=view&id={image_id}"

                            # 🔹 Link correto para baixar a imagem sem restrição
                            download_link = f"https://drive.google.com/uc?export=download&id={image_id}"
                            
                            # Exibir a imagem e botão de download
                            st.image(image_link, width=250, caption=image_name)
                            st.markdown(f"[📥 Baixar {image_name}]({download_link})", unsafe_allow_html=True)
                    else:
                        st.info("🚫 Nenhuma imagem cadastrada para este veículo.")
                else:
                    st.warning("🚨 Pasta do veículo não encontrada no Google Drive.")


            # Botões de Ação
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Editar", key=f"edit_{veiculo['id']}"):
                    with st.form(f"form_edit_{veiculo['id']}"):
                        novo_modelo = st.text_input("Modelo", value=veiculo["modelo"])
                        novo_ano = st.number_input("Ano", min_value=1990, max_value=2030, step=1, value=veiculo["ano"])
                        nova_km = st.number_input("Quilometragem Atual", min_value=0, step=1, value=veiculo["km_atual"])
                        novas_observacoes = st.text_area("Observações", value=veiculo.get("observacoes", ""))

                        if st.form_submit_button("Salvar Alterações"):
                            update_veiculo(veiculo["id"], modelo=novo_modelo, ano=novo_ano, km_atual=nova_km, observacoes=novas_observacoes)
                            st.success("✅ Veículo atualizado com sucesso!")
                            st.experimental_rerun()

            with col2:
                if st.button("🗑️ Excluir", key=f"delete_{veiculo['id']}"):
                    delete_veiculo(veiculo["id"])
                    st.success("✅ Veículo excluído com sucesso!")
                    st.rerun()

# ==============================
# 📌 Botão para limpar pastas "New Folder"
# ==============================
st.markdown("### 🗑️ Limpar Pastas Vazias")
if st.button("🗑 - Apagar NEW FOLDER"):
    deleted_folders = delete_new_folders_from_drive(VEICULOS_FOLDER_ID)

    if deleted_folders:
        st.success(f"✅ {len(deleted_folders)} pasta(s) 'New Folder' foram excluídas!")
    else:
        st.info("🔍 Nenhuma pasta 'New Folder' encontrada.")
# ==============================
# 🔹 Rodapé
# ==============================
st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)
