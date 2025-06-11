"""
pages/checklist_inicio.py

Tela de registro do Checklist de Início de Dia.

Funcionalidades:
- Permite o registro de informações iniciais do veículo.
- Upload de imagens do estado do veículo no início do dia.
- Compara com o último checklist do veículo, se disponível.
- Valida as imagens antes do upload.
- Salva os dados no banco de dados e no Google Drive.
- Atualiza a quilometragem do veículo no banco de dados.
"""

import sys
import os

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import datetime
from database.models.models_checklists import create_checklist, get_last_checklist
from database.models.models_veiculos import get_all_veiculos, get_veiculo_id, update_veiculo
from utils.image_utils import validar_imagem
from utils.km_calculations import validar_km_abastecimento
from services.auth_service import get_user_by_token
from services.google_drive_service import upload_file_to_drive, create_drive_folder

# 🗂️ ID da pasta principal do Google Drive para Checklists de Início
CHECKLISTS_INICIO_FOLDER_ID = "13oBpfpmJWrRpp4gTb4FN04WXWZbQoSzq"

st.set_page_config(page_title="Checklist de Início", layout="wide")

# ==============================
# 🛑 Verificação de Permissão
# ==============================
if "token" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.stop()

usuario_logado = get_user_by_token(st.session_state["token"])
if not usuario_logado:
    st.warning("⚠️ Sessão inválida. Faça login novamente.")
    st.stop()

st.markdown("<h2 style='text-align: center;'>📋 Checklist de Início de Dia</h2>", unsafe_allow_html=True)

# ==============================
# 🔹 Formulário para Criar Checklist
# ==============================
veiculos = get_all_veiculos()
opcoes_placas = [v["placa"] for v in veiculos]

if not opcoes_placas:
    st.warning("⚠️ Nenhum veículo cadastrado. Cadastre um veículo antes de registrar checklists.")
    st.stop()

placa = st.selectbox("Placa do Veículo", opcoes_placas)
veiculo_id = get_veiculo_id(placa)
data_vistoria = st.date_input("Data do Checklist", value=datetime.today())

# 🛠️ Recupera o último checklist do veículo (se houver)
ultimo_checklist = get_last_checklist(veiculo_id)
km_ultimo = ultimo_checklist["km_atual"] if ultimo_checklist else 0
km_atual = st.number_input("📏 Quilometragem Atual", min_value=0, step=1, value=km_ultimo)

# 🚨 Verifica inconsistência de quilometragem
if km_ultimo and not validar_km_abastecimento(veiculo_id, km_atual):
    st.warning("⚠️ A quilometragem informada parece inconsistente.")

# ✅ Perguntas do checklist
st.subheader("🚗 Condições do Veículo")
pneus_ok = st.radio("📌 Pneus estão em bom estado?", ["Sim", "Não"]) == "Sim"
farois_ok = st.radio("💡 Todas as luzes e faróis estão funcionando?", ["Sim", "Não"]) == "Sim"
cinto_seguranca_ok = st.radio("🎯 O cinto de segurança está funcionando?", ["Sim", "Não"]) == "Sim"
freios_ok = st.radio("🛑 Os freios estão funcionando corretamente?", ["Sim", "Não"]) == "Sim"
nivel_oleo_ok = st.radio("🛢️ O nível do óleo está adequado?", ["Sim", "Não"]) == "Sim"
vidros_ok = st.radio("🪟 Todos os vidros estão intactos?", ["Sim", "Não"]) == "Sim"
retrovisores_ok = st.radio("🔍 Os retrovisores estão ajustados corretamente?", ["Sim", "Não"]) == "Sim"
buzina_ok = st.radio("📢 A buzina está funcionando?", ["Sim", "Não"]) == "Sim"
itens_emergencia_ok = st.radio("🚨 O veículo tem triângulo, chave de roda e estepe?", ["Sim", "Não"]) == "Sim"

observacoes = st.text_area("❗ Relatar observações (se houver)")

# 📸 Upload de imagens do veículo
imagens = st.file_uploader("📸 Tire fotos do veículo", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

# ✅ BOTÃO DE ENVIO
if st.button("✅ Salvar Checklist"):
    if not veiculo_id or not km_atual:
        st.error("⚠️ Todos os campos obrigatórios devem ser preenchidos.")
    else:
        # 🔹 Criando a pasta do veículo dentro da pasta principal de Checklists de Início
        veiculo_folder_id = create_drive_folder(placa, CHECKLISTS_INICIO_FOLDER_ID)

        # 🔹 Upload das imagens para o Google Drive
        image_links = []
        if imagens:
            for imagem in imagens:
                if validar_imagem(imagem):
                    upload_result = upload_file_to_drive(imagem, "image/jpeg", veiculo_folder_id, imagem.name)

                    if upload_result and "id" in upload_result:
                        image_link = f"https://drive.google.com/file/d/{upload_result['id']}/view"
                        image_links.append(image_link)
                    else:
                        st.error(f"❌ Falha no upload da imagem {imagem.name}. Tente novamente.")
                else:
                    st.error(f"❌ Imagem {imagem.name} inválida ou corrompida. Não foi enviada.")

        # 🔹 Se não houver imagens, envia None para o banco de dados
        image_links = ",".join(image_links) if image_links else None

        # 🔹 Salva o checklist no banco de dados
        create_checklist(
            veiculo_id, usuario_logado["id"], "INICIO", km_atual, 
            pneus_ok, farois_ok, cinto_seguranca_ok, freios_ok, nivel_oleo_ok, 
            vidros_ok, retrovisores_ok, buzina_ok, itens_emergencia_ok, 
            observacoes, image_links
        )

        # 🔹 Atualiza a quilometragem do veículo no banco de dados
        update_veiculo(veiculo_id, km_atual=km_atual)

        st.success("✅ Checklist de Início registrado com sucesso!")
        st.rerun()

# ==============================
# 🔹 Rodapé
# ==============================
st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)
