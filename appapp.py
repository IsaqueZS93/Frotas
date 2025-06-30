# frontend/app.py
# ------------------------------------------------------------------
# Explorer-mock com tree_select + grid; clique direto na pasta abre a pasta
# Requer:  pip install streamlit streamlit-tree-select

import streamlit as st
from streamlit_tree_select import tree_select
from pathlib import Path

# ── 1. Dados-dummy -----------------------------------------------------------
TREE = {
    "Contrato 1": {
        "Unidade 001": {
            "Fotos": {"instalacao.jpg": None},
            "Documentos": {"relatorio.pdf": None},
        },
        "Unidade 002": {},
    },
    "Contrato 2": {
        "Unidade Alfa": {},
        "Unidade Beta": {},
    },
}

ICON = {"folder": "📁", "file": "📄"}

# ── 2. Helpers ---------------------------------------------------------------
def build_tree(data: dict, prefix: str = "") -> list:
    nodes = []
    for key, val in data.items():
        path = f"{prefix}/{key}" if prefix else key
        if isinstance(val, dict):               # pasta
            nodes.append(
                {"label": f"{ICON['folder']} {key}", "value": path, "children": build_tree(val, path)}
            )
        else:                                   # arquivo
            nodes.append({"label": f"{ICON['file']} {key}", "value": path})
    return nodes


def get_node(parts: list[str]):
    node = TREE
    for p in parts:
        node = node[p]
    return node


def parts(path_str: str) -> list[str]:
    return [p for p in path_str.split("/") if p]


# ── 3. Estado de navegação ---------------------------------------------------
if "selected_path" not in st.session_state:
    st.session_state.selected_path = ""     # raiz

# ── 4. Página ----------------------------------------------------------------
st.set_page_config(page_title="Explorer mock", layout="wide")
left, right = st.columns([1, 3])

# ---- 4A. Pane da esquerda (árvore) -----------------------------------------
with left:
    st.write("### Pastas")
    result = tree_select(
        nodes=build_tree(TREE),
        check_model="leaf",
        only_leaf_checkboxes=False,
        show_expand_all=True,
    )

    # Se o usuário clicou na árvore, atualize o caminho ativo
    if result and result.get("checked"):
        st.session_state.selected_path = result["checked"][0]

# ---- 4B. Pane da direita (grade) ------------------------------------------
sel_parts = parts(st.session_state.selected_path)
breadcrumb = " / ".join(["**Início**"] + [f"**{p}**" for p in sel_parts])
with right:
    st.markdown(breadcrumb)
    st.divider()

    node = get_node(sel_parts) if sel_parts else TREE
    if node is None:                      # arquivo folha
        st.info("Arquivo selecionado — placeholder para preview/download.")
    else:                                 # pasta
        cols = st.columns(6)
        for i, (name, child) in enumerate(node.items()):
            is_folder = isinstance(child, dict)
            full_path = "/".join(sel_parts + [name])  # caminho da pasta/arquivo

            with cols[i % 6]:
                # ── botão invisível captura clique e muda de pasta ──
                if st.button(" ", key=f"btn-{full_path}", help="Abrir" if is_folder else name):
                    if is_folder:
                        st.session_state.selected_path = full_path
                        st.experimental_rerun()
                    else:
                        st.info(f"Arquivo '{name}' selecionado.")  # placeholder

                # ── ícone grande + rótulo ──
                st.markdown(
                    f"<div style='text-align:center;font-size:48px'>{ICON['folder' if is_folder else 'file']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='text-align:center;font-size:0.75rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap'>{name}</div>",
                    unsafe_allow_html=True,
                )

st.caption(
    "• Clique numa pasta na ÁRVORE *ou* na GRADE para navegar.\n"
    "• Para produção: troque o dicionário TREE por dados vindos do Google Drive."
)
