import streamlit as st
import Imports_fleet  # 🔹 Garante que todos os caminhos do projeto sejam adicionados corretamente
import os
import tempfile
from PIL import Image, UnidentifiedImageError
from backend.db_models.DB_Models_Veiculo import (
    get_all_veiculos, get_veiculo_by_placa, update_veiculo, delete_veiculo, delete_veiculo_por_placa
)
from backend.services.Service_Google_Drive import download_file, delete_file

def veiculo_list_edit_screen():
    """Tela para listar, editar e excluir veículos."""

    st.title("🚗 Gerenciamento de Veículos")

    # Apenas ADMIN pode acessar
    if "user_type" not in st.session_state or st.session_state.user_type != "ADMIN":
        st.error("⚠️ Acesso restrito! Apenas usuários ADMIN podem acessar esta tela.")
        return

    # 🔹 Obter todos os veículos
    veiculos = get_all_veiculos()

    if not veiculos:
        st.warning("⚠️ Nenhum veículo cadastrado.")
        return

    # 🔹 Seleção do veículo
    veiculo_selecionado = st.selectbox(
        "Selecione um veículo para editar",
        veiculos,
        format_func=lambda v: f"{v['placa']} - {v['modelo']}"
    )

    if veiculo_selecionado:
        st.subheader("✏️ Editar Veículo")

        # 🔹 Organização dos campos em duas colunas
        col1, col2 = st.columns(2)

        with col1:
            novo_modelo = st.text_input("🚘 Modelo do Veículo", veiculo_selecionado["modelo"])
            nova_capacidade_tanque = st.number_input("⛽ Capacidade do Tanque (L)", min_value=1.0, step=0.1, value=veiculo_selecionado["capacidade_tanque"])
        
        with col2:
            novo_ano_fabricacao = st.number_input("📆 Ano de Fabricação", min_value=1900, max_value=2100, value=veiculo_selecionado["ano_fabricacao"])
            novo_hodometro = st.number_input("📍 KM Atual", min_value=0, step=1, value=veiculo_selecionado["hodometro_atual"])

        # 🔹 Exibição de imagens com tratamento de erro
        with st.expander("📸 Imagens do Veículo"):
            imagens_validas = []
            
            if veiculo_selecionado["fotos"]:
                fotos_ids = veiculo_selecionado["fotos"].split("|")
                for idx, foto_id in enumerate(fotos_ids, start=1):
                    temp_path = os.path.join(tempfile.gettempdir(), f"{veiculo_selecionado['placa']}_imagem_{idx}.jpg")
                    try:
                        download_file(foto_id, temp_path)
                        with Image.open(temp_path) as img:
                            imagens_validas.append(temp_path)
                    except UnidentifiedImageError:
                        st.error(f"❌ Erro: A imagem {idx} não pôde ser aberta. Pode estar corrompida.")
                    except Exception as e:
                        st.error(f"❌ Erro ao baixar/exibir a imagem {idx}: {e}")
                
                if imagens_validas:
                    st.image(imagens_validas, caption=[f"Imagem {i+1}" for i in range(len(imagens_validas))], use_container_width=True)

        # 🔹 Botões de ação organizados em colunas
        col3, col4 = st.columns([2, 1])

        with col3:
            if st.button("💾 Salvar Alterações", use_container_width=True):
                try:
                    sucesso = update_veiculo(
                        veiculo_selecionado["id"], veiculo_selecionado["placa"], veiculo_selecionado["renavam"],
                        novo_modelo, novo_ano_fabricacao, nova_capacidade_tanque, novo_hodometro, veiculo_selecionado["fotos"]
                    )
                    if sucesso:
                        st.success("✅ Veículo atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar veículo. Verifique os dados e tente novamente.")
                except Exception as e:
                    st.error(f"⚠️ Erro inesperado ao salvar alterações: {e}")

        with col4:
            if st.button("🗑 Excluir Veículo", use_container_width=True):
                try:
                    if veiculo_selecionado["fotos"]:
                        fotos_ids = veiculo_selecionado["fotos"].split("|")
                        for foto_id in fotos_ids:
                            try:
                                delete_file(foto_id)
                            except Exception as e:
                                st.error(f"Erro ao excluir imagem {foto_id}: {e}")

                    sucesso = delete_veiculo_por_placa(veiculo_selecionado["placa"])
                    if sucesso:
                        st.success("✅ Veículo excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir veículo do banco de dados.")
                except Exception as e:
                    st.error(f"❌ Erro inesperado ao excluir veículo: {e}")

# Executar a tela se for o script principal
if __name__ == "__main__":
    veiculo_list_edit_screen()
