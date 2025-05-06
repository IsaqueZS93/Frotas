# C:\Users\Novaes Engenharia\frotas\frontend\screens\Screen_Checklist_lists.py
# ---------------------------------------------------------------------------
#  Lista, exibe e gerencia check-lists – compatível com Service_Google_Drive
#  • Usa search_files() e list_files_in_folder() conforme assinatura real
# ---------------------------------------------------------------------------

import streamlit as st
import sys, os
from datetime import datetime

# 🔹 Caminho base do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Models
from backend.db_models.DB_Models_checklists import (
    get_all_checklists, get_checklists_by_placa, delete_checklist
)
from backend.db_models.DB_Models_Veiculo import get_all_veiculos
from backend.db_models.DB_Models_User import get_user_by_id

# 🔹 Serviços Google Drive
from backend.services.Service_Google_Drive import (
    search_files, get_folder_id_by_name, list_files_in_folder
)

# Pasta “Checklists” no Drive
PASTA_CHECKLISTS_ID = "10T2UHhc-wQXWRDj-Kc5F_dAHUM5F1TrK"


# ---------------------------------------------------------------------------
# Funções auxiliares para Google Drive
# ---------------------------------------------------------------------------
def _find_folder_inside(parent_id: str, folder_name: str):
    """
    Retorna o ID de uma subpasta de nome exato dentro de parent_id.
    Utiliza search_files() sem parâmetro extra.
    """
    query = (
        "mimeType='application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and name='{folder_name}' and trashed=false"
    )
    resultado = search_files(query)  # retorna lista de dicts com id e name
    return resultado[0]["id"] if resultado else None


def localizar_pasta_imagens(placa: str, checklist_id: int, data_hora: str):
    """
    Localiza a pasta das imagens:
      Checklists/ <placa>/  ( opcional : <id>  ou  <dd-mm-aaaa> )
    """
    pasta_placa_id = _find_folder_inside(PASTA_CHECKLISTS_ID, placa)
    if not pasta_placa_id:
        return None

    # Subpasta por ID
    subpasta_id = _find_folder_inside(pasta_placa_id, str(checklist_id))

    # Subpasta por data se não achar ID
    if not subpasta_id:
        data_fmt = datetime.strptime(data_hora, "%d/%m/%Y %H:%M:%S").strftime("%d-%m-%Y")
        subpasta_id = _find_folder_inside(pasta_placa_id, data_fmt)

    return subpasta_id or pasta_placa_id


# ---------------------------------------------------------------------------
# Tela principal
# ---------------------------------------------------------------------------
def checklist_list_screen():
    st.title("📋 Listagem e Gerenciamento de Checklists")

    # ---- Autenticação ------------------------------------------------------
    if "user_id" not in st.session_state:
        st.error("Você precisa estar logado para acessar esta tela.")
        return
    if st.session_state["user_type"] != "ADMIN":
        st.error("Você não tem permissão para acessar esta tela.")
        return

    # ---- Filtros -----------------------------------------------------------
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

    # ---- Busca inicial -----------------------------------------------------
    checklists = (
        get_checklists_by_placa(placa_filter) if placa_filter != "Todas"
        else get_all_checklists()
    )
    if data_filter:
        dia = data_filter.strftime("%d/%m/%Y")
        checklists = [c for c in checklists if c["data_hora"].startswith(dia)]
    if usuario_filter:
        uf = usuario_filter.lower()
        checklists = [c for c in checklists if uf in str(c["id_usuario"]).lower()]

    # ---- Exibição ----------------------------------------------------------
    st.subheader("📑 Checklists Registrados")
    if not checklists:
        st.info("Nenhum checklist encontrado.")
        return

    for ck in checklists:
        titulo = f"📌 ID: {ck['id']} | Placa: {ck['placa']} | Data: {ck['data_hora']}"
        with st.expander(titulo):
            # ---- Usuário ----------------------------------------------------
            row = get_user_by_id(ck["id_usuario"])
            user = dict(row) if row else {}
            nome_usuario = user.get("nome_completo", "Usuário desconhecido")

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
                st.write(f"🦺 **Itens Segurança:** {'✅' if ck['itens_seguranca_ok'] else '❌'}")
                st.write(f"📝 **Observações:** {ck['observacoes'] or '—'}")

            # ---- Imagens ----------------------------------------------------
            with col_dir:
                st.subheader("📸 Fotos")
                if not ck["fotos"]:
                    st.info("Nenhuma imagem anexada.")
                else:
                    nomes = [os.path.basename(p) for p in ck["fotos"].split("|")]
                    pasta = localizar_pasta_imagens(ck["placa"], ck["id"], ck["data_hora"])
                    if not pasta:
                        st.info("Pasta não encontrada no Drive.")
                    else:
                        q = (
                            f"mimeType contains 'image/' and '{pasta}' in parents "
                            f"and trashed=false"
                        )
                        arquivos = search_files(q)
                        imgs = [a for a in arquivos if a["name"] in nomes]

                        if not imgs:
                            st.info("Imagens não localizadas.")
                        else:
                            for i, img in enumerate(imgs, 1):
                                st.markdown(
                                    f"<a href='{img['webViewLink']}' target='_blank'>🖼️ Imagem {i}</a>",
                                    unsafe_allow_html=True,
                                )

            # ---- Exclusão ---------------------------------------------------
            if st.button(f"🗑️ Excluir Checklist {ck['id']}", key=f"del_{ck['id']}"):
                delete_checklist(ck["id"])
                st.success(f"Checklist {ck['id']} excluído!")
                st.rerun()


if __name__ == "__main__":
    checklist_list_screen()
