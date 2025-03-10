import os
import json
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings  # Ou outro modelo de embeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq

def load_database_as_json(db_path):
    """Carrega todas as informações do banco de dados e retorna o conteúdo como JSON."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        db_data = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            table_data = [dict(zip(columns, row)) for row in rows]
            db_data[table_name] = table_data
        conn.close()
        return json.dumps(db_data, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error("❌ Erro ao carregar dados do banco de dados.")
        st.write(f"Detalhes do erro: {e}")
        return "{}"

def create_vectorstore_from_json(db_json):
    """Cria uma base de dados vetorial (vectorstore) a partir do JSON do banco."""
    # Aqui, assumimos que o documento completo é transformado em um único objeto Document.
    # Para bases maiores, você pode dividir o JSON em partes menores.
    docs = [Document(page_content=db_json)]
    embeddings = OpenAIEmbeddings()  # Certifique-se de ter configurado a chave da API para o modelo de embeddings
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore

def build_rag_chain(db_json, selected_llm):
    """Constrói a cadeia de RAG combinando o LLM com o retriever."""
    vectorstore = create_vectorstore_from_json(db_json)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})  # Recupera os 2 documentos mais relevantes (ajuste conforme necessário)
    # Cria o chain conversacional de recuperação
    rag_chain = ConversationalRetrievalChain.from_llm(selected_llm, retriever=retriever)
    return rag_chain

def screen_ia():
    """Interface do Chatbot IA utilizando RAG."""
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("❌ Chave da API Groq não encontrada. Verifique seu arquivo .env.")
        return

    db_path = os.path.abspath("fleet_management.db")
    if not os.path.exists(db_path):
        st.error(f"❌ Banco de dados não encontrado em: {db_path}")
        return

    db_json = load_database_as_json(db_path)

    # Inicializa o modelo LLM (no seu caso, usando ChatGroq)
    selected_llm = ChatGroq(api_key=GROQ_API_KEY, model_name="groq-llm")
    # Constrói o chain RAG
    rag_chain = build_rag_chain(db_json, selected_llm)

    st.title("🦅 IA Águia - Respostas com RAG")
    st.markdown("### Faça suas perguntas sobre os dados da frota:")

    if "memoria" not in st.session_state:
        st.session_state["memoria"] = ConversationBufferMemory()
    memoria = st.session_state["memoria"]

    if st.button("Limpar memória"):
        st.session_state["memoria"] = ConversationBufferMemory()
        memoria = st.session_state["memoria"]
        st.success("Memória limpa.")

    user_input = st.chat_input("Digite sua pergunta sobre os dados da frota...")
    if user_input:
        st.chat_message("human").markdown(user_input)
        memoria.chat_memory.add_user_message(user_input)
        try:
            # O chain RAG já lida com a recuperação do contexto relevante
            resposta = rag_chain({"question": user_input, "chat_history": memoria.buffer})
            resposta_text = resposta["answer"]
            st.chat_message("assistant").markdown(resposta_text)
            memoria.chat_memory.add_ai_message(resposta_text)
        except Exception as e:
            st.error("❌ Ocorreu um erro ao processar sua pergunta.")
            st.write(f"Detalhes do erro: {e}")

if __name__ == "__main__":
    screen_ia()
