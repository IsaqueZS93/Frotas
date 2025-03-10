import streamlit as st
import sys
import os
from datetime import datetime

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos módulos do projeto
from backend.db_models.DB_Models_checklists import create_checklist
from backend.db_models.DB_Models_Veiculo import get_veiculo_by_placa, get_all_veiculos, update_veiculos_KM
from backend.services.Service_Email import send_email_alert
from backend.services.Service_Google_Drive import create_subfolder, upload_images_to_drive, get_folder_id_by_name, list_files_in_folder

# 🔹 ID da pasta principal dos checklists no Google Drive
PASTA_CHECKLISTS_ID = "10T2UHhc-wQXWRDj-Kc5F_dAHUM5F1TrK"

def checklist_create_screen():
    """Tela para preenchimento de checklists de veículos."""
    
    st.title("📋 Preenchimento de Checklist")
    
    # Verifica se o usuário está logado
    if "user_id" not in st.session_state:
        st.error("Você precisa estar logado para acessar esta tela.")
        return
    
    user_id = st.session_state["user_id"]
    user_type = st.session_state["user_type"]

    if user_type not in ["ADMIN", "OPE"]:
        st.error("Você não tem permissão para acessar esta tela.")
        return

    # 🔹 Seleção do veículo
    veiculos = get_all_veiculos()
    placas = [veiculo["placa"] for veiculo in veiculos]
    placa = st.selectbox("🔹 Selecione a Placa do Veículo", placas)
    
    veiculo = get_veiculo_by_placa(placa)
    km_atual = veiculo["hodometro_atual"] if veiculo else 0

    if "km_atual_aux" not in st.session_state or st.session_state.get("placa_selecionada") != placa:
        st.session_state["km_atual_aux"] = km_atual
        st.session_state["placa_selecionada"] = placa

    st.text(f"📌 KM Atual do Veículo: {st.session_state['km_atual_aux']} km")
    km_informado = st.number_input("📌 KM Informado", min_value=st.session_state["km_atual_aux"], step=1)

    # 🔹 Tipo de checklist (INICIO ou FIM)
    tipo_checklist = st.radio("📝 Tipo de Checklist", ["INICIO", "FIM"], horizontal=True)

    # 🔹 Perguntas organizadas em colunas para melhor apresentação
    col1, col2 = st.columns(2)
    with col1:
        pneus_ok = st.radio("🛞 Pneus em boas condições?", ["SIM", "NÃO"], horizontal=True) == "SIM"
        farois_setas_ok = st.radio("💡 Faróis e Setas Funcionando?", ["SIM", "NÃO"], horizontal=True) == "SIM"
        freios_ok = st.radio("🛑 Sistema de freio em boas condições?", ["SIM", "NÃO"], horizontal=True) == "SIM"
    
    with col2:
        oleo_ok = st.radio("🛢️ Nível do Óleo Adequado?", ["SIM", "NÃO"], horizontal=True) == "SIM"
        vidros_retrovisores_ok = st.radio("🚗 Vidros e Retrovisores Ajustados?", ["SIM", "NÃO"], horizontal=True) == "SIM"
        itens_seguranca_ok = st.radio("🦺 Itens de Segurança Completos?", ["SIM", "NÃO"], horizontal=True) == "SIM"
    
    # 🔹 Observações gerais
    observacoes = st.text_area("📝 Observações (Opcional)")

    # 🔹 Upload de fotos (as fotos são carregadas, mas o processamento é feito após o clique no botão)
    fotos = st.file_uploader("📸 Adicionar Fotos do Veículo", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    # 🔹 Ações executadas somente ao submeter o checklist
    if st.button("✅ Submeter Checklist"):
        # 🔹 Criar ou verificar a pasta no Google Drive para o veículo
        itens_pasta = list_files_in_folder(PASTA_CHECKLISTS_ID)
        pasta_veiculo_id = None
        for item in itens_pasta:
            if item.get("name") == placa:
                pasta_veiculo_id = item.get("id")
                break

        if pasta_veiculo_id:
            st.info(f"A pasta para a placa {placa} já existe no Google Drive.")
        else:
            pasta_veiculo_id = create_subfolder(PASTA_CHECKLISTS_ID, placa)
            if pasta_veiculo_id:
                st.success(f"Pasta para {placa} criada no Google Drive.")
            else:
                st.error("❌ Erro ao criar/verificar pasta do veículo no Google Drive.")
                return
        
        # 🔹 Criar nomes para as imagens antes do upload
        data_hora_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        imagens_paths = []
        for foto in fotos:
            extensao = os.path.splitext(foto.name)[1]
            nome_arquivo = f"{placa}_{data_hora_str}{extensao}"
            temp_path = os.path.join("/tmp", nome_arquivo)
            with open(temp_path, "wb") as temp_file:
                temp_file.write(foto.read())
            imagens_paths.append(temp_path)
        
        imagens_ids = upload_images_to_drive(imagens_paths, pasta_veiculo_id)
        for temp_path in imagens_paths:
            os.remove(temp_path)
        imagens_ids_str = "|".join(imagens_ids) if imagens_ids else ""
        
        # 🔹 Submeter checklist
        sucesso = create_checklist(
            id_usuario=user_id,
            tipo=tipo_checklist,
            placa=placa,
            km_atual=st.session_state["km_atual_aux"],
            km_informado=km_informado,
            pneus_ok=pneus_ok,
            farois_setas_ok=farois_setas_ok,
            freios_ok=freios_ok,
            oleo_ok=oleo_ok,
            vidros_retrovisores_ok=vidros_retrovisores_ok,
            itens_seguranca_ok=itens_seguranca_ok,
            observacoes=observacoes,
            fotos=imagens_ids_str
        )
        
        if sucesso:
            update_veiculos_KM(placa, km_informado)
            
            # Envio de alerta por email, caso haja algum problema no veículo
            if not all([pneus_ok, farois_setas_ok, freios_ok, oleo_ok, vidros_retrovisores_ok, itens_seguranca_ok]):
                problemas = []
                if not pneus_ok: problemas.append("🛞 Pneus desgastados")
                if not farois_setas_ok: problemas.append("💡 Faróis ou setas com defeito")
                if not freios_ok: problemas.append("🛑 Problema nos freios")
                if not oleo_ok: problemas.append("🛢️ Nível do óleo inadequado")
                if not vidros_retrovisores_ok: problemas.append("🚗 Vidros ou retrovisores desalinhados")
                if not itens_seguranca_ok: problemas.append("🦺 Itens de segurança incompletos")
                
                email_mensagem = f"""
🚨 **Alerta de Problema no Veículo**
- 📌 **Placa:** {placa}
- 🕒 **Data/Hora:** {data_hora_str}
- 📝 **Problemas Identificados:**
{"\n".join(problemas)}
- 👤 **Usuário:** {st.session_state['user_id']}
                """
                send_email_alert(f"⚠ Alerta de Problema no Veículo {placa}", email_mensagem)
            
            st.success("✅ Checklist submetido com sucesso!")
            st.session_state["km_atual_aux"] = km_informado
        else:
            st.error("❌ Erro ao submeter checklist. Tente novamente.")

if __name__ == "__main__":
    checklist_create_screen()
