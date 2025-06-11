import sys
import os
import streamlit as st
from database.models.models_abastecimentos import (
    get_all_abastecimentos, create_abastecimento, update_abastecimento, delete_abastecimento
)
from database.models.models_veiculos import get_all_veiculos
from services.auth_service import get_user_by_token
from services.google_drive_service import upload_file_to_drive
from utils.km_calculations import calcular_custo_por_km  # Integração com cálculo de custo por KM
from PIL import Image
import io

# Definição direta da pasta de Notas Fiscais no Google Drive
NOTAS_FISCAIS_FOLDER_ID = "1yv2nWX5wiJiHc2-sHiykgYclUy8yw1Hb"

# Aplicando o CSS personalizado
st.markdown('<link rel="stylesheet" href="/static/css/styles.css">', unsafe_allow_html=True)

# ==============================
# 🛑 Verificação de Permissão (ADMIN e OPE)
# ==============================
if "token" not in st.session_state:
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.stop()

usuario_logado = get_user_by_token(st.session_state["token"])

if not usuario_logado:
    st.warning("⚠️ Sessão inválida. Faça login novamente.")
    st.stop()

st.markdown("<h2 style='text-align: center;'>⛽ Gerenciamento de Abastecimentos</h2>", unsafe_allow_html=True)

# ==============================
# 🔹 Formulário para Criar Novo Abastecimento
# ==============================
with st.expander("➕ Registrar Novo Abastecimento"):
    with st.form("form_novo_abastecimento"):
        veiculos = get_all_veiculos()
        opcoes_placas = [v["placa"] for v in veiculos]

        if not opcoes_placas:
            st.warning("⚠️ Nenhum veículo cadastrado. Cadastre um veículo antes de registrar abastecimentos.")
            st.stop()

        placa = st.selectbox("Placa do Veículo", opcoes_placas)
        litros_abastecidos = st.number_input("Quantidade de Litros", min_value=1.0, step=0.1)
        km_abastecimento = st.number_input("KM no Momento do Abastecimento", min_value=0, step=1)
        tipo_combustivel = st.selectbox("Tipo de Combustível", ["GASOLINA", "ÁLCOOL", "DIESEL", "GÁS"])
        valor_total = st.number_input("Valor Total do Abastecimento (R$)", min_value=0.0, step=0.01)
        horario = st.time_input("Horário do Abastecimento")

        # Upload da nota fiscal
        nota_fiscal = st.file_uploader("Nota Fiscal (opcional)", type=["jpg", "png", "jpeg", "pdf"])

        if st.form_submit_button("Registrar Abastecimento"):
            nota_fiscal_link = None
            if nota_fiscal:
                if nota_fiscal.type in ["image/png", "image/jpeg", "image/jpg"]:
                    image = Image.open(nota_fiscal)
                    img_byte_arr = io.BytesIO()
                    image.convert("RGB").save(img_byte_arr, format="JPEG")
                    img_byte_arr.seek(0)
                    upload_result = upload_file_to_drive(img_byte_arr, "image/jpeg", NOTAS_FISCAIS_FOLDER_ID, nota_fiscal.name)
                    if upload_result and "id" in upload_result:
                        nota_fiscal_link = f"https://drive.google.com/file/d/{upload_result['id']}/view"
                else:
                    st.error("❌ Formato de imagem inválido. Apenas JPG, PNG ou PDF são aceitos.")
                    st.stop()

            create_abastecimento(placa, litros_abastecidos, km_abastecimento, tipo_combustivel, valor_total, nota_fiscal_link)
            st.success("✅ Abastecimento registrado com sucesso!")

            # Atualiza o custo médio por KM do veículo
            custo_por_km = calcular_custo_por_km(placa)
            if custo_por_km:
                st.info(f"📊 Custo médio por KM atualizado: **R$ {custo_por_km}**")

            st.experimental_rerun()

# ==============================
# 📌 Lista de Abastecimentos
# ==============================
st.subheader("📋 Abastecimentos Registrados")

abastecimentos = get_all_abastecimentos()

if not abastecimentos:
    st.info("🔹 Nenhum abastecimento registrado.")
else:
    for abastecimento in abastecimentos:
        with st.expander(f"⛽ {abastecimento['placa']} - {abastecimento['tipo_combustivel']} ({abastecimento['quantidade_litros']}L)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text(f"🚗 Placa: {abastecimento['placa']}")
                st.text(f"⛽ Combustível: {abastecimento['tipo_combustivel']}")
                st.text(f"⏰ Horário: {abastecimento['horario']}")
                st.text(f"📏 KM Abastecimento: {abastecimento['km_abastecimento']} km")
                st.text(f"💧 Litros: {abastecimento['quantidade_litros']}L")
                st.text(f"💲 Valor Total: R$ {abastecimento['valor_total']}")

                # Exibir o custo médio por KM rodado
                custo_por_km = calcular_custo_por_km(abastecimento["placa"])
                if custo_por_km:
                    st.text(f"📊 Custo por KM: R$ {custo_por_km}")

            with col2:
                if abastecimento["nota_fiscal"]:
                    st.markdown(f"[📄 Visualizar Nota Fiscal]({abastecimento['nota_fiscal']})", unsafe_allow_html=True)

# ==============================
# 🔹 Rodapé
# ==============================
st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)
