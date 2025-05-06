# C:\Users\Novaes Engenharia\frotas\frontend\screens\Screen_Checklist_lists.py
# ---------------------------------------------------------------------------
#  Lista, exibe e gerencia check-lists
#  • Busca todas as fotos cujas “chaves” (ID ou nome) estão salvas no campo
#    ck["fotos"]  — exibe link individual para cada imagem
# ---------------------------------------------------------------------------

import streamlit as st
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Models
from backend.db_models.DB_Models_checklists import (
    get_all_checklists, get_checklists_by_placa, delete_checklist
)
from backend.db_models.DB_Models_Veiculo import get_all_veiculos
from backend.db_models.DB_Models_User import get_user_by_id

# 🔹 Google Drive helpers
from backend.services.Service_Google_Drive import (
    search_files, get_google_drive_service
)

PASTA_CHECKLISTS_ID = "10T2UHhc-wQXWRDj-Kc5F_dAHUM5F1TrK"


# ---------------------------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------------------------
def _find_folder_inside(parent_id: str, folder_name: str):
    q = (
        "mimeType='application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and name='{folder_name}' and trashed=false"
    )
    res = search_files(q)
    return res[0]["id"] if res else None


def _file_metadata_by_id(file_id: str):
    """Tenta obter metadados (id, name, webViewLink) via ID; retorna None se falhar."""
    try:
        srv = get_google_drive_service()
        if not srv:
            return None
        return srv.files().get(
            fileId=file_id,
            fields="id,name,webViewLink,trashed"
        ).execute()
    except Exception:
        return None


def localizar_pasta_imagens(placa: str, checklist_id: int, data_hora: str):
    pasta_placa = _find_folder_inside(PASTA_CHECKLISTS_ID, placa)
    if not pasta_placa:
        return None
    sub_id = _find_folder_inside(pasta_placa, str(checklist_id))
    if not sub_id:
        sub_id = _find_folder_inside(pasta_placa, data_hora.split(" ")[0].replace("/", "-"))
    return sub_id or pasta_placa


# ---------------------------------------------------------------------------
# Tela principal
# ---------------------------------------------------------------------------
def checklist_list_screen():
    st.title("📋 Listagem e Gerenciamento de Checklists")

    # --- segurança ---
    if "user_id" not in st.session_state or st.session_state.get("user_type") != "ADMIN":
        st.error("Acesso restrito.")
        return

    # --- filtros ---
    c1, c2, c3 = st.columns(3)
    with c1:
        placa_filter = st.selectbox(
            "Filtrar Placa",
            ["Todas"] + [v["placa"] for v in get_all_veiculos()]
        )
    with c2:
        data_filter = st.date_input("Filtrar Data", value=None)
    with c3:
        usuario_filter = st.text_input("Filtrar Usuário (ID ou Nome)")

    checklists = (
        get_checklists_by_placa(placa_filter) if placa_filter != "Todas"
        else get_all_checklists()
    )
    if data_filter:
        dia = data_filter.strftime("%d/%m/%Y")
        checklists = [c for c in checklists if c["data_hora"].startswith(dia)]
    if usuario_filter:
        f = usuario_filter.lower()
        checklists = [c for c in checklists if f in str(c["id_usuario"]).lower()]

    st.subheader("📑 Resultados")
    if not checklists:
        st.info("Nenhum checklist encontrado.")
        return

    for ck in checklists:
        with st.expander(f"ID {ck['id']} | {ck['placa']} | {ck['data_hora']}"):
            user = dict(get_user_by_id(ck["id_usuario"]) or {})
            st.write(f"👤 **Usuário:** {user.get('nome_completo','Desconhecido')} (ID {ck['id_usuario']})")
            st.write(f"🕒 **Data/Hora:** {ck['data_hora']}")

            # --------------------  Fotos  --------------------
            st.subheader("📸 Fotos")
            if not ck["fotos"]:
                st.info("Nenhuma chave de foto armazenada.")
            else:
                chaves = [p.strip() for p in ck["fotos"].split("|") if p.strip()]
                pasta_imgs = localizar_pasta_imagens(ck["placa"], ck["id"], ck["data_hora"])

                for idx, chave in enumerate(chaves, 1):
                    meta = None

                    # 1) Tenta tratar a chave como ID diretamente
                    if len(chave) >= 25:  # IDs do Drive costumam ter 25+ chars
                        meta = _file_metadata_by_id(chave)

                    # 2) Se não for ID ou não achou, trata como NOME dentro da pasta
                    if not meta and pasta_imgs:
                        q = (
                            f"name='{chave}' and "
                            f"'{pasta_imgs}' in parents and trashed=false"
                        )
                        res = search_files(q)
                        if res:
                            meta = res[0]

                    # 3) Feedback ao usuário
                    if meta and not meta.get("trashed", False):
                        st.markdown(
                            f"<a href='{meta['webViewLink']}' target='_blank'>🖼️ Foto {idx} — {meta['name']}</a>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning(f"🔍 Foto '{chave}' não encontrada no Drive.")

            # --------------------  Excluir  -------------------
            if st.button(f"Excluir Checklist {ck['id']}", key=f"del_{ck['id']}"):
                delete_checklist(ck["id"])
                st.success("Checklist excluído.")
                st.rerun()


if __name__ == "__main__":
    checklist_list_screen()
