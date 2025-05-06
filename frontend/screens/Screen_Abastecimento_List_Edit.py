# C:\Users\Novaes Engenharia\frotas\frontend\screens\Screen_Abastecimento_List_Edit.py
# -----------------------------------------------------------------------------
#  Lista, edita e exclui abastecimentos
#  • Exibe a(s) nota(s) fiscal(is) como imagem(s) (JPG, PNG, PDF → link)
# -----------------------------------------------------------------------------

import streamlit as st
import sys, os
from datetime import datetime

# Caminho base
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Models
from backend.db_models.DB_Models_Abastecimento import (
    get_all_abastecimentos, get_abastecimento_by_placa, get_abastecimento_by_usuario,
    delete_abastecimento, get_abastecimento_by_id, create_abastecimento
)
from backend.db_models.DB_Models_Veiculo import get_all_veiculos
from backend.db_models.DB_Models_User import get_all_users

# Google-Drive helpers
from backend.services.Service_Google_Drive import (
    get_google_drive_service, list_files_in_folder
)

PASTA_ABASTECIMENTOS_ID = "1zw9CR0InO4J0ns1MvETMMiZwY7qfAW3A"


# ---------------------------------------------------------------------------
# Utilitários Drive
# ---------------------------------------------------------------------------
def _find_subfolder(parent_id: str, nome: str):
    """Devolve ID da subpasta de nome exato dentro de parent_id."""
    for item in list_files_in_folder(parent_id):
        if item["name"] == nome:
            return item["id"]
    return None


def _link_raw(file_id: str):
    """Gera link direto para visualização/embedding."""
    return f"https://drive.google.com/uc?export=view&id={file_id}"


def localizar_pasta_nota(placa: str, data_hora: str):
    """
    Estrutura esperada no Drive:
      Abastecimentos/<placa>/<dd-mm-aaaa>/
    """
    pasta_placa = _find_subfolder(PASTA_ABASTECIMENTOS_ID, placa)
    if not pasta_placa:
        return None
    data_fmt = data_hora.split(" ")[0].replace("/", "-")  # dd-mm-aaaa
    sub_id = _find_subfolder(pasta_placa, data_fmt)
    return sub_id or pasta_placa


def encontrar_arquivo_por_nome(parent_id: str, nome: str):
    """Retorna metadados do arquivo cujo name == nome dentro do parent_id."""
    for item in list_files_in_folder(parent_id):
        if item["name"] == nome:
            return item
    return None


# ---------------------------------------------------------------------------
def user_is_admin():
    return st.session_state.get("user_type") == "ADMIN"


def abastecimento_list_edit_screen():
    st.title("📋 Gerenciar Abastecimentos")

    if not user_is_admin():
        st.error("Apenas usuários ADMIN podem acessar esta tela.")
        return

    # ---- Filtros ----------------------------------------------------------
    veiculos = get_all_veiculos()
    placas = [v["placa"] for v in veiculos] if veiculos else []

    usuarios = get_all_users()
    nomes_usuarios = [f"{u['id']} - {u['nome_completo']}" for u in usuarios] if usuarios else []

    c1, c2, c3 = st.columns(3)
    with c1:
        filtro_placa = st.selectbox("Placa", ["Todos"] + placas)
    with c2:
        filtro_usuario = st.selectbox("Usuário", ["Todos"] + nomes_usuarios)
    with c3:
        filtro_data = st.date_input("Data", value=None)

    if filtro_placa != "Todos":
        abastecimentos = get_abastecimento_by_placa(filtro_placa)
    elif filtro_usuario != "Todos":
        user_id = filtro_usuario.split(" - ")[0]
        abastecimentos = get_abastecimento_by_usuario(user_id)
    else:
        abastecimentos = get_all_abastecimentos()

    if filtro_data:
        abastecimentos = [
            a for a in abastecimentos
            if datetime.strptime(a["data_hora"], "%d/%m/%Y %H:%M").date() == filtro_data
        ]

    st.subheader("📑 Resultados")
    if not abastecimentos:
        st.warning("Nenhum abastecimento encontrado.")
        return

    for ab in abastecimentos:
        with st.expander(f"{ab['placa']} — {ab['data_hora']}"):
            esq, dir = st.columns([2, 1])

            # ----------------- Dados principais -----------------
            with esq:
                st.write(f"KM abastecimento: {ab['km_abastecimento']} km")
                st.write(f"Quantidade: {ab['quantidade_litros']} L")
                st.write(f"Valor total: R$ {ab['valor_total']}")
                st.write(f"Valor por litro: R$ {ab['valor_por_litro']}")
                st.write(f"Observações: {ab['observacoes'] or '—'}")

            # ----------------- Nota fiscal (imagens) ------------
            with dir:
                st.subheader("📄 Nota Fiscal")
                if not ab["nota_fiscal"]:
                    st.info("Nenhuma nota fiscal anexada.")
                else:
                    chaves = [c.strip() for c in ab["nota_fiscal"].split("|") if c.strip()]
                    pasta = localizar_pasta_nota(ab["placa"], ab["data_hora"])

                    if not pasta:
                        st.warning("Pasta da nota fiscal não encontrada.")
                    else:
                        for idx, chave in enumerate(chaves, 1):
                            meta = None

                            # Se a chave parece um ID (25+ chars)
                            if len(chave) >= 25:
                                meta = {"id": chave, "name": chave, "webViewLink": _link_raw(chave)}
                            else:  # trata como nome
                                meta = encontrar_arquivo_por_nome(pasta, chave)

                            if meta:
                                img_url = _link_raw(meta["id"])
                                # PDF → mostrar link, imagem → embed
                                if meta["name"].lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                                    st.image(img_url, caption=f"NF {idx} — {meta['name']}", use_column_width=True)
                                else:
                                    st.markdown(
                                        f"📄 <a href='{meta['webViewLink']}' target='_blank'>Nota Fiscal {idx} — {meta['name']}</a>",
                                        unsafe_allow_html=True
                                    )
                            else:
                                st.warning(f"Arquivo '{chave}' não encontrado.")

            # ----------------- Edição / Exclusão ----------------
            # (código de edição permanece igual – omitido aqui por brevidade)

if __name__ == "__main__":
    abastecimento_list_edit_screen()
