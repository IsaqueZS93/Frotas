"""
pages/checklist_final.py

Tela de registro do Checklist de Fim de Dia.

Funcionalidades:
- Permite o registro do estado do veículo no fim do dia.
- Upload de imagens do estado do veículo ao final do expediente.
- Compara com o checklist de início do dia.
- Atualiza a quilometragem do veículo no banco de dados.
- Salva os dados no banco de dados e no Google Drive.
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

# Criando a pasta principal no Google Drive para Checklists Finais, caso não exista
if "CHECKLISTS_FOLDER_ID" not in st.session_state:
    st.session_state["CHECKLISTS_FOLDER_ID"] = create_drive_folder("Checklists/Fim")

CHECKLISTS_FOLDER_ID = st.session_state["CHECKLISTS_FOLDER_ID"]

# Aplicando o CSS personalizado
st.markdown('<link rel="stylesheet" href="/static/css/styles.css">', unsafe_allow_html=True)

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

st.markdown("<h2 style='text-align: center;'>📋 Checklist de Fim de Dia</h2>", unsafe_allow_html=True)

# ==============================
# 🔹 Formulário para Criar Checklist
# ==============================
veiculos = get_all_veiculos()
opcoes_placas = [v["placa"] for v in veiculos]

if not opcoes_placas:
    st.warning("⚠️ Nenhum veículo cadastrado. Cadastre um veículo antes de registrar checklists.")
    st.stop()

placa = st.selectbox("Placa do Veículo", opcoes_placas)
veiculo_id = get_veiculo_id(placa)  # Obtém o ID do veículo
data_vistoria = st.date_input("Data do Checklist", value=datetime.today())

# Recupera o último checklist do veículo (de início do dia)
ultimo_checklist = get_last_checklist(veiculo_id)
km_inicial = ultimo_checklist["km_atual"] if ultimo_checklist else 0

km_final = st.number_input(
    "📏 Quilometragem Final", min_value=km_inicial, step=1, value=km_inicial
)

# Verifica inconsistência de quilometragem
if km_inicial and not validar_km_abastecimento(veiculo_id, km_final):
    st.warning("⚠️ A quilometragem informada parece inconsistente com o registro do início do dia.")

# Perguntas do checklist de fim de dia
st.subheader("🚗 Condições do Veículo no Final do Dia")
pneus_ok = st.radio("📌 Pneus estão em bom estado?", ["Sim", "Não"]) == "Sim"
farois_ok = st.radio("💡 Todas as luzes e faróis estão funcionando?", ["Sim", "Não"]) == "Sim"
cinto_seguranca_ok = st.radio("🎯 O cinto de segurança está funcionando?", ["Sim", "Não"]) == "Sim"
freios_ok = st.radio("🛑 Os freios estão funcionando corretamente?", ["Sim", "Não"]) == "Sim"
nivel_oleo_ok = st.radio("🛢️ O nível do óleo está adequado?", ["Sim", "Não"]) == "Sim"
vidros_ok = st.radio("🪟 Todos os vidros estão intactos?", ["Sim", "Não"]) == "Sim"
retrovisores_ok = st.radio("🔍 Os retrovisores estão ajustados corretamente?", ["Sim", "Não"]) == "Sim"
buzina_ok = st.radio("📢 A buzina está funcionando?", ["Sim", "Não"]) == "Sim"
itens_emergencia_ok = st.radio("🚨 O veículo tem triângulo, chave de roda e estepe?", ["Sim", "Não"]) == "Sim"
limpeza = st.radio("🧼 O veículo está limpo?", ["Sim", "Não"]) == "Sim"
nivel_combustivel_final = st.radio("⛽ Nível de Combustível ao Final do Dia:", ["Cheio", "3/4", "1/2", "1/4", "Reserva"])
danos_novos = st.text_area("❗ Relatar danos novos (se houver)")
avarias_anteriores = ultimo_checklist["observacoes"] if ultimo_checklist else "Nenhuma"
st.text(f"Avarias registradas no início do dia: {avarias_anteriores}")

# Upload de imagens do veículo (estado final)
imagens = st.file_uploader(
    "📸 Tire fotos do veículo (Danos, Estado Geral, Interior)", 
    type=["jpg", "png", "jpeg"], accept_multiple_files=True
)

# ✅ BOTÃO DE ENVIO
if st.button("✅ Salvar Checklist"):
    if not (veiculo_id and km_final):
        st.error("⚠️ Todos os campos obrigatórios devem ser preenchidos.")
    else:
        # Criando uma pasta específica para o veículo dentro do Google Drive
        veiculo_folder_id = create_drive_folder(f"Checklists/Fim/{placa}", CHECKLISTS_FOLDER_ID)

        # Valida e faz upload das imagens para o Google Drive
        image_links = []
        if imagens:
            for imagem in imagens:
                if validar_imagem(imagem):
                    upload_result = upload_file_to_drive(imagem, "image/jpeg", veiculo_folder_id, imagem.name)

                    # Verifica se o upload foi bem-sucedido antes de gerar o link
                    if upload_result and "id" in upload_result:
                        image_link = f"https://drive.google.com/file/d/{upload_result['id']}/view"
                        image_links.append(image_link)
                    else:
                        st.error(f"❌ Falha no upload da imagem {imagem.name}. Tente novamente.")

                else:
                    st.error(f"❌ Imagem {imagem.name} inválida ou corrompida. Não foi enviada.")

        # Salva o checklist no banco de dados
        create_checklist(
            veiculo_id, usuario_logado["id"], "FIM", km_final, 
            pneus_ok, farois_ok, cinto_seguranca_ok, freios_ok, nivel_oleo_ok, 
            vidros_ok, retrovisores_ok, buzina_ok, itens_emergencia_ok, 
            danos_novos, ",".join(image_links) if image_links else None
        )

        # Atualiza a quilometragem do veículo no banco de dados
        update_veiculo(veiculo_id, km_atual=km_final)

        st.success("✅ Checklist de Fim registrado com sucesso!")
        st.rerun()

# ==============================
# 🔹 Rodapé
# ==============================
st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)
