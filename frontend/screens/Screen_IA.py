import os
import json
import sqlite3
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

def split_large_json(db_json, max_tokens=4000):
    """Divide um JSON grande em partes menores se exceder o limite de tokens."""
    json_data = json.loads(db_json)
    json_parts = []
    current_part = {}
    current_size = 0

    for table, rows in json_data.items():
        table_json = json.dumps({table: rows}, ensure_ascii=False)
        table_size = len(table_json)
        
        if current_size + table_size > max_tokens:
            json_parts.append(json.dumps(current_part, ensure_ascii=False, indent=2))
            current_part = {table: rows}
            current_size = table_size
        else:
            current_part[table] = rows
            current_size += table_size
    
    if current_part:
        json_parts.append(json.dumps(current_part, ensure_ascii=False, indent=2))
    
    return json_parts

def load_database_as_json(db_path):
    """Carrega todas as informações do banco de dados corretamente e retorna um JSON válido."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [table[0] for table in cursor.fetchall()]
        db_data = {}
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            cursor.execute(f"SELECT * FROM {table};")
            rows = cursor.fetchall()
            table_data = [dict(zip(columns, row)) for row in rows]
            db_data[table] = table_data
        
        conn.close()
        full_json = json.dumps(db_data, ensure_ascii=False, indent=2)
        return split_large_json(full_json)
    except sqlite3.Error as e:
        st.error("❌ Erro ao carregar dados do banco de dados.")
        st.write(f"Detalhes do erro: {e}")
        return ["{}"]

def build_chain(db_json_parts, selected_llm):
    """Cria a cadeia de conversação garantindo que o JSON seja bem tratado."""
    db_json_combined = "\n".join(db_json_parts)
    db_json_escaped = db_json_combined.replace("{", "{{").replace("}", "}}").replace("\"", "\\\"")
    system_message = f"""
    Você é um assistente chamado Águia que responde com base no JSON do banco de dados.
    Aqui está o contexto:
    {db_json_escaped}
    Responda de forma clara e objetiva.
    """
    
    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    return template | selected_llm

def screen_ia():
    """Tela do Chatbot IA que utiliza o JSON do banco e um prompt estruturado."""
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("❌ Chave da API Groq não encontrada. Verifique seu arquivo .env.")
        return

    db_path = os.path.abspath("fleet_management.db")
    if not os.path.exists(db_path):
        st.error(f"❌ Banco de dados não encontrado em: {db_path}")
        return

    db_json_parts = load_database_as_json(db_path)
    
    selected_model = "groq-llm"
    selected_llm = ChatGroq(api_key=GROQ_API_KEY, model_name=selected_model)
    chain = build_chain(db_json_parts, selected_llm)

    st.title("🦅 IA Águia - Respostas Baseadas no Banco de Dados 🚛")
    st.markdown("### Faça suas perguntas sobre os dados da frota:")

    with st.expander("Visualizar JSON do banco de dados"):
        for idx, part in enumerate(db_json_parts):
            st.json(json.loads(part))

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
            resposta = chain.invoke({"input": user_input, "chat_history": memoria.buffer_as_messages})
            st.chat_message("assistant").markdown(resposta)
            memoria.chat_memory.add_ai_message(resposta)
        except Exception as e:
            st.error("❌ Erro ao processar sua pergunta. Tente novamente.")
            st.write(f"Detalhes do erro: {e}")

if __name__ == "__main__":
    screen_ia()
