import streamlit as st
import sys, os
from datetime import datetime

# 🔹 Caminho base
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Modelos e serviços
from backend.db_models.DB_Models_checklists import (
    get_all_checklists, get_checklists_by_placa,
    get_checklists_by_id, delete_checklist)
from backend.db_models.DB_Models_Veiculo import get_all_veiculos
from backend.db_models.DB_Models_User import get_user_by_id
from backend.services.Service_Google_Drive import (
    search_files, get_folder_id_by_name)
from backend.services.Service_Email import send_email  # opcional

# Pasta “Checklists” no Drive
PASTA_CHECKLISTS_ID = "10T2UHhc-wQXWRDj-Kc5F_dAHUM5F1TrK"


# ---------------------------------------------------------------------------
# Função auxiliar – encontra a subpasta correta no Drive
# ---------------------------------------------------------------------------
def localizar_pasta_imagens(placa: str, checklist_id: int, data_hora: str):
    """
    Retorna o ID da pasta onde estão as imagens do checklist.

    Estrutura esperada no Drive:
    Checklists/
        └── <PLACA>/
              ├── <ID_CHECKLIST> (ou parte da data)/
              │      └── fotos...
              └── fotos soltas...
    """
    # 1) Pasta da placa (dentro da pasta-mãe)
    pasta_placa_id = get_folder_id_by_name(placa, parent_id=PASTA_CHECKLISTS_ID)
    if not pasta_placa_id:
        return None

    # 2) Tenta subpasta que contenha o ID do checklist
    subpasta_id = get_folder_id_by_name(str(checklist_id), parent_id=pasta_placa_id)

    # 3) Se não achar, tenta subpasta pela data (DD-MM-AAAA)
    if not subpasta_id:
        data_formatada = datetime.strptime(data_hora, "%d/%m/%Y %H:%M:%S").strftime("%d-%m-%Y")
        subpasta_id = get_folder_id_by_name(data_formatada, parent_id=pasta_placa_id)

    # 4) Retorna a pasta encontrada (ou None)
    return subpasta_id or pasta_placa_id  # cai para a pasta da placa se não houver subpasta


# ---------------------------------------------------------------------------
# Tela principal
# ---------------------------------------------------------------------------
def checklist_list_screen():
    st.title("📋 Listagem e Gerenciamento de Checklists")

    # 🔒 Autenticação e permissão
    if "user_id" not in st.session_state:
        st.error("Você precisa estar logado para acessar esta tela.")
        return
    if st.session_state["user_type"] != "ADMIN":
        st.error("Você não tem permissão para acessar esta tela.")
        return

    # -----------------------------------------------------------------------
    # Filtros
    # -----------------------------------------------------------------------
    st.subheader("🔍 Filtros de Busca")
    col1, col2, col3 = st.columns(3)
    with col1:
        placa_filter = st.selectbox(
            "📌 Filtrar por Placa",
            ["Todas"] + [v["placa"] for v in get_all_veiculos()]
        )
    with col2:
        data_filter = st.date_input("📅 Filtrar por Data", value=None)
    with col3:
        usuario_filter = st.text_input("👤 Filtrar por ID Usuário ou Nome")

    # Busca inicial
    checklists = (
        get_checklists_by_placa(placa_filter) if placa_filter != "Todas"
        else get_all_checklists()
    )

    # Aplica filtros adicionais
    if data_filter:
        checklists = [
            c for c in checklists
            if c["data_hora"].startswith(data_filter.strftime("%d/%m/%Y"))
        ]
    if usuario_filter:
        usuario_filter = usuario_filter.lower()
        checklists = [
            c for c in checklists
            if usuario_filter in str(c["id_usuario"]).lower()
        ]

    # -----------------------------------------------------------------------
    # Lista de checklists
    # -----------------------------------------------------------------------
    st.subheader("📑 Checklists Registrados")
    if not checklists:
        st.info("Nenhum checklist encontrado com os filtros selecionados.")
        return

    for ck in checklists:
        with st.expander(
            f"📌 Checklist ID: {ck['id']} | Placa: {ck['placa']} | Data: {ck['data_hora']}"
        ):
            user = get_user_by_id(ck["id_usuario"]) or {}
            nome_usuario = user.get("nome_completo", "Desconhecido")

            # -- Dados principais -------------------------------------------------
            col_esq, col_dir = st.columns([2, 1])
            with col_esq:
                st.write(f"👤 **Usuário:** {nome_usuario} (ID {ck['id_usuario']})")
                st.write(f"🕒 **Data/Hora:** {ck['data_hora']}")
                st.write(f"📌 **Placa:** {ck['placa']}")
                st.write(f"📊 **KM Atual / Informado:** {ck['km_atual']} km / {ck['km_informado']} km")
                st.write(f"🛞 **Pneus:** {'✅' if ck['pneus_ok'] else '❌'}")
                st.write(f"💡 **Faróis/Setas:** {'✅' if ck['farois_setas_ok'] else '❌'}")
                st.write(f"🛑 **Freios:** {'✅' if ck['freios_ok'] else '❌'}")
                st.write(f"🛢️ **Óleo:** {'✅' if ck['oleo_ok'] else '❌'}")
                st.write(f"🚗 **Vidros/Retrovisores:** {'✅' if ck['vidros_retrovisores_ok'] else '❌'}")
                st.write(f"🦺 **Itens de Segurança:** {'✅' if ck['itens_seguranca_ok'] else '❌'}")
                st.write(f"📝 **Observações:** {ck['observacoes'] or '—'}")

            # -- Imagens ----------------------------------------------------------
            with col_dir:
                st.subheader("📸 Fotos")
                if not ck["fotos"]:
                    st.info("Nenhuma imagem anexada a este checklist.")
                else:
                    nomes_esperados = [os.path.basename(p) for p in ck["fotos"].split("|")]

                    # 1) Localiza pasta correta
                    pasta_imgs_id = localizar_pasta_imagens(
                        ck["placa"], ck["id"], ck["data_hora"]
                    )
                    if not pasta_imgs_id:
                        st.info("Pasta de imagens não encontrada no Drive.")
                    else:
                        # 2) Busca arquivos que batem com os nomes esperados
                        query = (
                            f"'{pasta_imgs_id}' in parents and trashed=false "
                            f"and mimeType contains 'image/'"
                        )
                        arquivos = search_files(
                            query=query,
                            fields="files(id,name,webViewLink,thumbnailLink)"
                        )
                        imagens = [
                            arq for arq in arquivos if arq["name"] in nomes_esperados
                        ]

                        if not imagens:
                            st.info("Imagens não encontradas na pasta.")
                        else:
                            for idx, img in enumerate(imagens, 1):
                                st.markdown(
                                    f"<a href='{img['webViewLink']}' target='_blank'>"
                                    f"🖼️ Imagem {idx}</a>",
                                    unsafe_allow_html=True,
                                )

            # -- Exclusão ---------------------------------------------------------
            if st.button(f"🗑️ Excluir Checklist {ck['id']}", key=f"del_{ck['id']}"):
                delete_checklist(ck["id"])
                st.success(f"Checklist {ck['id']} excluído!")
                st.rerun()


if __name__ == "__main__":
    checklist_list_screen()
