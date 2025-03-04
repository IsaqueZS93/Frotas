# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\screens\Screen_Veiculo_Create.py

import streamlit as st
import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import os
import tempfile
from datetime import datetime
from backend.db_models.DB_Models_Veiculo import create_veiculo, get_veiculo_by_placa, get_veiculo_by_renavam
from backend.services.Service_Google_Drive import upload_images_to_drive, create_subfolder

# 🔹 ID da pasta principal dos veículos no Google Drive
PASTA_VEICULOS_ID = "1779UUJikU308xDiz9-8xV0hJs-L8BwsY"

def veiculo_create_screen():
    """Tela para cadastrar novos veículos no sistema."""
    
    st.title("🚗 Cadastro de Veículo")

    # Apenas ADMIN pode acessar
    if "user_type" not in st.session_state or st.session_state.user_type != "ADMIN":
        st.error("⚠️ Acesso restrito! Apenas usuários ADMIN podem acessar esta tela.")
        return

    # Layout organizado em colunas para melhor disposição dos campos
    col1, col2 = st.columns(2)

    with col1:
        placa = st.text_input("🔹 Placa do Veículo", placeholder="Ex: ABC1234").upper().strip()
        modelo = st.text_input("🚘 Modelo do Veículo", placeholder="Ex: Civic LX").strip()
        capacidade_tanque = st.number_input("⛽ Capacidade do Tanque (L)", min_value=1.0, step=0.1)

    with col2:
        renavam = st.text_input("📑 Renavam", placeholder="Ex: 123456789").strip()
        ano_fabricacao = st.number_input("📆 Ano de Fabricação", min_value=1900, max_value=datetime.now().year, step=1)
        hodometro_atual = st.number_input("📍 KM Atual", min_value=0, step=1)

    # Seção de Upload de imagens
    with st.expander("📸 Upload de Imagens do Veículo"):
        imagens = st.file_uploader("Selecione imagens do veículo", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

    # Botão de cadastro do veículo
    if st.button("✅ Cadastrar Veículo", use_container_width=True):
        if not all([placa, renavam, modelo, ano_fabricacao, capacidade_tanque, hodometro_atual]):
            st.error("❌ Todos os campos são obrigatórios!")
            return

        if get_veiculo_by_placa(placa):
            st.warning("⚠️ Este veículo já está cadastrado com essa placa!")
            return

        if get_veiculo_by_renavam(renavam):
            st.warning("⚠️ Já existe um veículo cadastrado com este Renavam!")
            return

        try:
            # Criar a subpasta do veículo dentro da pasta "Veículos" no Google Drive
            pasta_veiculo_id = create_subfolder(PASTA_VEICULOS_ID, placa)  

            if not pasta_veiculo_id:
                st.error("❌ Erro ao criar pasta no Google Drive.")
                return

            # Criar arquivos temporários para as imagens
            imagens_paths = []
            if imagens:
                for idx, imagem in enumerate(imagens, start=1):
                    extensao = os.path.splitext(imagem.name)[1]  # Obtém a extensão do arquivo (.jpg, .png)
                    nome_arquivo = f"{placa}_{modelo.replace(' ', '_')}_{idx}{extensao}"  # Ex: ABC1234_Civic_1.jpg
                    
                    # Criar arquivo temporário com nome correto
                    temp_path = os.path.join(tempfile.gettempdir(), nome_arquivo)
                    with open(temp_path, "wb") as temp_file:
                        temp_file.write(imagem.read())
                    
                    imagens_paths.append(temp_path)

            # Upload das imagens para a pasta correta e obter IDs das imagens
            imagens_ids = upload_images_to_drive(imagens_paths, pasta_veiculo_id) if imagens_paths else []

            # Remover arquivos temporários após upload
            for temp_path in imagens_paths:
                os.remove(temp_path)

            # Concatena os IDs das imagens como string separada por "|"
            imagens_ids_str = "|".join(imagens_ids) if imagens_ids else ""

            # Criar veículo no banco de dados
            sucesso = create_veiculo(placa, renavam, modelo, ano_fabricacao, capacidade_tanque, hodometro_atual, imagens_ids_str)
            
            if sucesso:
                st.success("✅ Veículo cadastrado com sucesso!")
                st.balloons()
            else:
                st.error("❌ Erro ao cadastrar o veículo. Verifique os dados e tente novamente.")

        except Exception as e:
            st.error(f"⚠️ Erro inesperado: {e}")
            print(f"[ERRO] Falha ao cadastrar veículo: {e}")

# Executar a tela se for o script principal
if __name__ == "__main__":
    veiculo_create_screen()
