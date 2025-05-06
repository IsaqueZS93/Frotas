# C:\Users\Novaes Engenharia\frotas\frontend\screens\Screen_Checklist_lists.py
# ---------------------------------------------------------------------------
#  Lista, exibe e gerencia check-lists (exibe TODAS as fotos como links)
# ---------------------------------------------------------------------------

import streamlit as st
import sys, os
from datetime import datetime

# 🔹 Caminho base do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Modelos
from backend.db_models.DB_Models_checklists import (
    get_all_checklists, get_checklists_by_placa, delete_checklist
)
from backend.db_models.DB_Models_Veiculo import get_all_veiculos
from backend.db_models.DB_Models_User import get_user_by_id

# 🔹 Serviços Google Drive
from backend.services.Service_Google_Drive import search_files

# Pasta “Checklists” no Drive
PASTA_CHECKLISTS_ID = "10T2UHhc-wQXWRDj-Kc5F_dAHUM5F1TrK"


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def _find_folder_inside(parent_id: str, folder_name: str):
    query = (
        "mimeType='application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and name='{folder_name}' and trashed=false"
    )
    res = search_files(query)
    return res[0]["id"] if res else None


def localizar_pasta_imagens(placa: str, checklist_id: int, data_hora: str):
    """Retorna ID da pasta que contém as fotos do checklist."""
    pasta_placa = _find_folder_inside(PASTA_CHECKLISTS_ID, placa)
    if not pasta_placa:
        return None

    sub_id = _find_folder_inside(pasta_placa, str(checklist_id))
    if not sub_id:
        data_fmt = data_hora.split(" ")[0].replace("/", "-")  # dd-mm-aaaa
        sub_id = _find_folder_inside(pasta_placa, data_fmt)

    return sub_id or pasta_placa


# ---------------------------------------------------------------------------
# Tela principal
# ---------------------------------------------------------------------------
def checklist_list_screen():
    st.title("📋 Listagem e Gerenciamento de Checklists")

    # --- Autorização ---
    if "user_id" not in st.session_state or st.session_state.get("user_type") != "ADMIN":
        st.error("Acesso restrito.")
        return

    # --- Filtros ---
    st.subheader("🔍 Filtros de Busca")
    c1, c2, c3 = st.columns(3)
    with c1:
        placa_filter = st.selectbox(
            "📌 Filtrar por Placa",
            ["Todas"] + [v["placa"] for v in get_all_veiculos()]
        )
    with c2:
        data_filter = st.date_input("📅 Filtrar por Data", value=None)
    with c3:
        usuario_filter = st.text_input("👤 Filtrar por ID Usuário ou Nome")

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

    # --- Lista ---
    st.subheader("📑 Checklists Registrados")
    if not checklists:
        st.info("Nenhum checklist encontrado.")
        return

    for ck in checklists:
        cabe = f"📌 ID {ck['id']} | Placa {ck['placa']} | {ck['data_hora']}"
        with st.expander(cabe):
            usr = dict(get_user_by_id(ck["id_usuario"]) or {})
            nome_usuario = usr.get("nome_completo", "Desconhecido")

            esq, dir = st.columns([2, 1])
            with esq:
                st.write(f"👤 **Usuário:** {nome_usuario} (ID {ck['id_usuario']})")
                st.write(f"🕒 **Data/Hora:** {ck['data_hora']}")
                st.write(f"📊 **KM Atual / Informado:** {ck['km_atual']} / {ck['km_informado']} km")
                st.write(f"🛞 **Pneus:** {'✅' if ck['pneus_ok'] else '❌'}")
                st.write(f"💡 **Faróis/Setas:** {'✅' if ck['farois_setas_ok'] else '❌'}")
                st.write(f"🛑 **Freios:** {'✅' if ck['freios_ok'] else '❌'}")
                st.write(f"🛢️ **Óleo:** {'✅' if ck['oleo_ok'] else '❌'}")
                st.write(f"🚗 **Vidros/Retrovisores:** {'✅' if ck['vidros_retrovisores_ok'] else '❌'}")
                st.write(f"🦺 **Itens Segurança:** {'✅' if ck['itens_seguranca_ok'] else '❌'}")
                st.write(f"📝 **Observações:** {ck['observacoes'] or '—'}")

            # --- Fotos (todos os arquivos) ---
            with dir:
                st.subheader("📸 Fotos")
                pasta = localizar_pasta_imagens(ck["placa"], ck["id"], ck["data_hora"])
                if not pasta:
                    st.info("Pasta de imagens não encontrada no Drive.")
                else:
                    q = f"mimeType contains 'image/' and '{pasta}' in parents and trashed=false"
                    fotos = search_files(q)
                    if not fotos:
                        st.info("Nenhuma imagem na pasta.")
                    else:
                        for i, foto in enumerate(fotos, 1):
                            st.markdown(
                                f"<a href='{foto['webViewLink']}' target='_blank'>🖼️ Imagem {i} — {foto['name']}</a>",
                                unsafe_allow_html=True
                            )

            # --- Botão excluir ---
            if st.button(f"🗑️ Excluir Checklist {ck['id']}", key=f"del_{ck['id']}"):
                delete_checklist(ck["id"])
                st.success("Checklist excluído.")
                st.rerun()


if __name__ == "__main__":
    checklist_list_screen()
