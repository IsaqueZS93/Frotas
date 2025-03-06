import streamlit as st

# 🔹 ID do arquivo no Google Drive
FILE_ID = "1u-kwDCVRq-fNRRv1NsUbpiqOM8rz_LeW"

# 🔹 Gerar o link de download direto
DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

st.title("📥 Baixar Banco de Dados do Google Drive")

st.markdown(f"🔗 [Clique aqui para baixar o banco de dados]( {DOWNLOAD_URL} )", unsafe_allow_html=True)

# 🔹 Criar um botão de download estilizado
if st.button("📥 Baixar Banco de Dados"):
    st.success("✅ Clique no link acima para baixar diretamente do Google Drive!")
