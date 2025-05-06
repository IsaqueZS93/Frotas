# C:\Users\Novaes Engenharia\frotas\frontend\screens\Screen_Checklist_lists.py
# ---------------------------------------------------------------------------
#  Lista, exibe e gerencia check-lists – agora corrigido para Row → dict
#  (evita AttributeError: 'sqlite3.Row' object has no attribute 'get')
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
    search_files, get_folder_id_by_name
)

# Pasta “Checklists” no Drive
PASTA_CHECKLISTS_ID = "10T2UHhc-wQXWRDj-Kc5F_dAHUM5F1TrK"


# ---------------------------------------------------------------------------
# Função auxiliar – encontra pasta com imagens
# ---------------------------------------------------------------------------
def localizar_pasta_imagens(placa: str, checklist_id: int, data_hora: str):
    """Retorna o ID da pasta com as fotos do checklist."""
    pasta_placa_id = get_folder_id_by_name(placa, parent_id=PASTA_CHECKLISTS_ID)
    if not pasta_placa_id:
        return None

    # tenta subpasta pelo ID
    subpasta_id = get_folder_id_by_name(str(checklist_id), parent_id=pasta_placa_id)

    # tenta subpasta pela data se ID não existir
    if not subpasta_id:
        data_fmt = datetime.strptime(data_hora, "%d/%m/%Y %H:%M:%S").strftime("%d-%m-%Y")
        subpasta_id = get_folder_id_by_name(data_fmt, parent_id=pasta_placa_id)

    return subpasta_id or pasta_placa_id


# ---------------------------------------------------------------------------
# Tela principal
# ---------------------------------------------------------------------------
def checklist_list_screen():
    st.title("📋 Listagem e Gerenciamento de Checklists")

    # ---- Autenticação / permissão ------------------------------------------
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

    # ---- Recupera check-lists ---------------------------------------------
    checklists = (
        get_checklists_by_placa(placa_filter) if placa_filter != "Todas"
        else get_all_checklists()
    )
    if data_filter:
        checklists = [
            c for c in checklists
            if c["data_hora"].startswith(data_filter.strftime("%d/%m/%Y"))
        ]
    if usuario_filter:
        uf = usuario_filter.lower()
        checklists = [
            c for c in checklists
            if uf in str(c["id_usuario"]).lower()
        ]

    # ---- Exibição ---------------------------------------------------------
    st.subheader("📑 Checklists Registrados")
    if not checklists:
        st.info("Nenhum checklist encontrado com os filtros selecionados.")
        return

    for ck in checklists:
        with st.expander(
            f"📌 Checklist ID: {ck['id']} | Placa: {ck['placa']} | Data: {ck['data_hora']}"
        ):
            # -------- Dados do usuário (corrigido) --------------------------
            user_row = get_user_by_id(ck["id_usuario"])
            user = dict(user_row) if user_row else {}
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
                st.write(f"🦺 **Itens de Segurança:** {'✅' if ck['itens_seguranca_ok'] else '❌'}")
                st.write(f"📝 **Observações:** {ck['observacoes'] or '—'}")

            # -------- Imagens ------------------------------------------------
            with col_dir:
                st.subheader("📸 Fotos")
                if not ck["fotos"]:
                    st.info("Nenhuma imagem anexada.")
                else:
                    nomes_esperados = [os.path.basename(p) for p in ck["fotos"].split("|")]
                    pasta_imgs_id = localizar_pasta_imagens(ck["placa"], ck["id"], ck["data_hora"])
                    if not pasta_imgs_id:
                        st.info("Pasta de imagens não encontrada no Drive.")
                    else:
                        q = f"'{pasta_imgs_id}' in parents and trashed=false and mimeType contains 'image/'"
                        arquivos = search_files(q, fields="files(id,name,webViewLink)")
                        imgs = [a for a in arquivos if a["name"] in nomes_esperados]

                        if not imgs:
                            st.info("Imagens não localizadas.")
                        else:
                            for i, img in enumerate(imgs, 1):
                                st.markdown(
                                    f"<a href='{img['webViewLink']}' target='_blank'>🖼️ Imagem {i}</a>",
                                    unsafe_allow_html=True
                                )

            # -------- Exclusão ----------------------------------------------
            if st.button(f"🗑️ Excluir Checklist {ck['id']}", key=f"del_{ck['id']}"):
                delete_checklist(ck["id"])
                st.success(f"Checklist {ck['id']} excluído!")
                st.rerun()


# Execução stand-alone
if __name__ == "__main__":
    checklist_list_screen()
