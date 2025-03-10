import streamlit as st
import sys
import os
from datetime import datetime
from backend.services.Service_Google_Drive import upload_images_to_drive, create_subfolder

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos módulos do projeto
from backend.db_models.DB_Models_Abastecimento import (
    create_abastecimento, 
    get_next_abastecimento_id
)
from backend.db_models.DB_Models_Veiculo import get_all_veiculos, get_KM_veiculo_placa
from backend.services.Service_Email import send_email_alert

# 🔹 ID da pasta principal "Abastecimentos" no Google Drive
PASTA_ABASTECIMENTOS_ID = "1zw9CR0InO4J0ns1MvETMMiZwY7qfAW3A"

def user_is_authenticated():
    """Verifica se o usuário está autenticado e autorizado (ADMIN ou OPE)."""
    return "user_type" in st.session_state and st.session_state.user_type in ["ADMIN", "OPE"]

def user_id():
    """Retorna o ID do usuário logado."""
    return st.session_state.get("user_id", None)

def abastecimento_create_screen():
    """Tela de registro de abastecimento."""

    st.title("⛽ Registro de Abastecimento")

    # 🔹 Verificação de permissão
    if not user_is_authenticated():
        st.error("⚠️ Apenas usuários ADMIN e OPE podem acessar esta tela.")
        return

    # 🔹 Buscar lista de veículos para seleção
    veiculos = get_all_veiculos()
    lista_placas = [veiculo["placa"] for veiculo in veiculos] if veiculos else []

    if not lista_placas:
        st.warning("⚠️ Nenhum veículo cadastrado. Cadastre um veículo primeiro.")
        return

    # 🔹 Formulário de abastecimento
    placa_selecionada = st.selectbox("🚗 Placa do Veículo", lista_placas)

    # 🔹 Buscar o KM atual do veículo selecionado usando get_KM_veiculo_placa
    km_atual = get_KM_veiculo_placa(placa_selecionada)
    if km_atual is None:
        st.error("❌ Não foi possível recuperar o KM atual deste veículo.")
        return
    st.write(f"📌 **KM Atual:** {km_atual} km")

    km_abastecimento = st.number_input("📍 KM no Momento do Abastecimento", min_value=km_atual, step=1)
    quantidade_litros = st.number_input("⛽ Quantidade Abastecida (L)", min_value=0.1, step=0.1)
    tipo_combustivel = st.selectbox("⛽ Tipo de Combustível", ["Gasolina", "Diesel", "Etanol", "GNV"])
    valor_total = st.number_input("💰 Valor Total Pago (R$)", min_value=0.01, step=0.01)

    # 🔹 Cálculo automático do valor por litro
    valor_por_litro = round(valor_total / quantidade_litros, 2) if quantidade_litros > 0 else 0.0
    st.write(f"💲 **Valor por Litro:** R$ {valor_por_litro}")

    # 🔹 Upload da Nota Fiscal (Imagem)
    nota_fiscal = st.file_uploader("📄 Nota Fiscal (Imagem)", type=["png", "jpg", "jpeg"])

    observacoes = st.text_area("📝 Observações Gerais (Opcional)")

    # 🔹 Obter o próximo ID de abastecimento (se necessário)
    abastecimento_id = get_next_abastecimento_id()

    # 🔹 Criar/Obter a subpasta da PLACA dentro da pasta "Abastecimentos"
    pasta_veiculo_id = create_subfolder(PASTA_ABASTECIMENTOS_ID, placa_selecionada)
    if not pasta_veiculo_id:
        st.error("❌ Erro ao criar ou localizar a pasta do veículo no Google Drive.")
        return

    # 🔹 Fazer upload da nota fiscal para o Google Drive
    nota_fiscal_id = None
    if nota_fiscal:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(nota_fiscal.name)[1]
        filename = f"{placa_selecionada}_{timestamp}_{abastecimento_id}{file_extension}"

        # Criar um arquivo temporário para upload
        temp_path = os.path.join(os.getcwd(), filename)
        with open(temp_path, "wb") as f:
            f.write(nota_fiscal.getbuffer())

        # Fazer upload da imagem
        uploaded_file_ids = upload_images_to_drive([temp_path], pasta_veiculo_id)

        # Excluir o arquivo temporário após o upload
        os.remove(temp_path)

        if uploaded_file_ids:
            nota_fiscal_id = uploaded_file_ids[0]

    # 🔹 Criar abastecimento no banco de dados
    sucesso, mensagem = create_abastecimento(
        id_usuario=user_id(),
        placa=placa_selecionada,
        data_hora=datetime.now().strftime("%d/%m/%Y %H:%M"),
        km_atual=km_atual,
        km_abastecimento=km_abastecimento,
        quantidade_litros=quantidade_litros,
        tipo_combustivel=tipo_combustivel,
        valor_total=valor_total,
        nota_fiscal=nota_fiscal_id,  # 🔹 Salva o ID do arquivo no banco
        observacoes=observacoes
    )

    if sucesso:
        st.success("✅ Abastecimento registrado com sucesso!")
    else:
        st.error(f"❌ Erro: {mensagem}")

# 🔹 Executar a tela se for o script principal
if __name__ == "__main__":
    abastecimento_create_screen()
