import os
import json
import sqlite3
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

# =============================================================================
# Função para extrair somente o texto da resposta, removendo prefixos e metadados.
# =============================================================================
def extract_response_text(response):
    """
    Remove o prefixo 'content=' e quaisquer metadados adicionais,
    retornando apenas o texto da resposta.
    """
    if isinstance(response, dict):
        text = response.get("content", "")
    elif isinstance(response, str):
        text = response
    else:
        text = str(response)
    
    if text.startswith("content="):
        text = text[len("content="):].strip()
    if text.startswith("'") and text.endswith("'"):
        text = text[1:-1].strip()
    idx = text.find("additional_kwargs=")
    if idx != -1:
        text = text[:idx].strip()
    return text

# =============================================================================
# Função para carregar o banco de dados SQLite e retornar seu conteúdo como JSON.
# =============================================================================
def load_database_as_json(db_path):
    """Carrega todas as informações do banco de dados em um objeto JSON."""
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

# =============================================================================
# Função para listar modelos disponíveis na Groq.
# =============================================================================
def list_available_models(api_key):
    """Lista todos os modelos disponíveis na Groq."""
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json()["data"]
        return [model["id"] for model in models]
    except Exception as e:
        st.error("❌ Erro ao listar modelos disponíveis na Groq.")
        st.write(f"Detalhes do erro: {e}")
        return []

# =============================================================================
# Função para construir a cadeia de conversação (chain) usando um prompt estruturado.
# =============================================================================
def build_chain(db_json, selected_llm):
    """
    Cria a cadeia de conversação utilizando um prompt estruturado.
    Escapa as chaves do JSON para que não sejam interpretadas como placeholders.
    """
    db_json_escaped = db_json.replace("{", "{{").replace("}", "}}")
    system_message = f"""
Você é um assistente amigável chamado Águia que responde com base no JSON completo do banco de dados.
Aqui está o contexto:
{db_json_escaped}

Utilize essas informações para responder de forma clara, objetiva e natural. 

Nunca revele a senha dos usuários, quando for perguntado, responda: Não posso lhe dar essa informação.
Conheça nosso banco de dados:

### Tabela: `users`
- **Descrição**: Armazena informações dos usuários do sistema.
- **Campos**:
  - `id` (INTEGER): Identificador único do usuário.
  - `nome_completo` (TEXT): Nome completo do usuário.
  - `data_nascimento` (TEXT): Data de nascimento do usuário.
  - `email` (TEXT): E-mail do usuário.
  - `usuario` (TEXT): Nome de usuário.
  - `cnh` (TEXT): Número da CNH (Carteira Nacional de Habilitação).
  - `contato` (TEXT): Número de contato do usuário.
  - `validade_cnh` (TEXT): Data de validade da CNH.
  - `funcao` (TEXT): Função do usuário no sistema.
  - `empresa` (TEXT): Empresa à qual o usuário pertence.
  - `senha` (TEXT): Senha do usuário.
  - `tipo` (TEXT): Tipo de usuário (ex: ADMINISTRAÇÃO, OPE).

### Tabela: `veiculos`
- **Descrição**: Armazena informações sobre os veículos da frota.
- **Campos**:
  - `id` (INTEGER): Identificador único do veículo.
  - `placa` (TEXT): Placa do veículo.
  - `renavam` (TEXT): Número do RENAVAM do veículo.
  - `modelo` (TEXT): Modelo do veículo.
  - `ano_fabricacao` (INTEGER): Ano de fabricação do veículo.
  - `capacidade_tanque` (REAL): Capacidade do tanque de combustível (em litros).
  - `hodometro_atual` (INTEGER): Quilometragem atual do veículo.
  - `fotos` (TEXT): Caminho ou link para fotos do veículo (opcional).

### Tabela: `checklists`
- **Descrição**: Armazena checklists realizados para os veículos.
- **Campos**:
  - `id` (INTEGER): Identificador único do checklist.
  - `id_usuario` (INTEGER): ID do usuário que realizou o checklist.
  - `tipo` (TEXT): Tipo de checklist.
  - `data_hora` (TEXT): Data e hora do checklist.
  - `placa` (TEXT): Placa do veículo associado ao checklist.
  - `km_atual` (INTEGER): Quilometragem atual do veículo no momento do checklist.
  - `km_informado` (INTEGER): Quilometragem informada pelo usuário.
  - `pneus_ok` (BOOLEAN): Estado dos pneus (OK ou não).
  - `farois_setas_ok` (BOOLEAN): Estado dos faróis e setas (OK ou não).
  - `freios_ok` (BOOLEAN): Estado dos freios (OK ou não).
  - `oleo_ok` (BOOLEAN): Estado do óleo (OK ou não).
  - `vidros_retrovisores_ok` (BOOLEAN): Estado dos vidros e retrovisores (OK ou não).
  - `itens_seguranca_ok` (BOOLEAN): Estado dos itens de segurança (OK ou não).
  - `observacoes` (TEXT): Observações adicionais.
  - `fotos` (TEXT): Caminho ou link para fotos do checklist (opcional).

### Tabela: `abastecimentos`
- **Descrição**: Armazena informações sobre abastecimentos de combustível.
- **Campos**:
  - `id` (INTEGER): Identificador único do abastecimento.
  - `id_usuario` (INTEGER): ID do usuário que realizou o abastecimento.
  - `placa` (TEXT): Placa do veículo abastecido.
  - `data_hora` (TEXT): Data e hora do abastecimento.
  - `km_atual` (INTEGER): Quilometragem atual do veículo no momento do abastecimento.
  - `km_abastecimento` (INTEGER): Quilometragem no momento do abastecimento.
  - `quantidade_litros` (REAL): Quantidade de litros abastecidos.
  - `tipo_combustivel` (TEXT): Tipo de combustível (ex: Gasolina, Diesel).
  - `valor_total` (REAL): Valor total do abastecimento.
  - `valor_por_litro` (REAL): Valor por litro do combustível.
  - `nota_fiscal` (TEXT): Número da nota fiscal (opcional).
  - `observacoes` (TEXT): Observações adicionais.

Utilize essas informações para responder de forma clara, objetiva e natural. 
Não ultrapasse 300 caracteres nas respostas.

"""
    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    chain = template | selected_llm
    return chain

# =============================================================================
# Função para formatar a resposta em Markdown, incluindo tabelas.
# =============================================================================
def format_response_markdown(response_text):
    """
    Formata a resposta para um estilo Markdown bonito.
    Se a resposta contiver uma tabela Markdown, exibe-a como uma tabela no Streamlit.
    Caso contrário, formata como texto comum.
    """
    if "|" in response_text and "-" in response_text:  # Verifica se é uma tabela Markdown
        # Remove linhas vazias ou duplicadas
        lines = [line.strip() for line in response_text.split("\n") if line.strip()]
        cleaned_response = "\n".join(lines)
        st.markdown("**Resposta:**")
        st.markdown(cleaned_response)  # Exibe a tabela Markdown
        return cleaned_response
    else:
        return f"**Resposta:**\n\n> {response_text}"

# =============================================================================
# Função principal que monta a interface do chatbot.
# =============================================================================
def screen_ia():
    """Tela do Chatbot IA que utiliza o JSON do banco e um prompt estruturado para respostas naturais."""
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("❌ Chave da API Groq não encontrada. Verifique seu arquivo .env.")
        return

    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "fleet_management.db"))
    if not os.path.exists(db_path):
        st.error(f"❌ Banco de dados não encontrado em: {db_path}")
        return

    db_json = load_database_as_json(db_path)

    # Listar modelos disponíveis
    available_models = list_available_models(GROQ_API_KEY)
    if not available_models:
        st.error("❌ Não foi possível carregar os modelos disponíveis.")
        return

    # O widget st.selectbox usa a chave "selected_model" para persistir seu valor
    selected_model = st.selectbox(
        "Selecione o modelo para resposta:",
        options=available_models,
        index=available_models.index(st.session_state.get("selected_model", available_models[0])),
        key="selected_model"
    )

    # Use uma chave separada para controlar se o modelo atual mudou
    if "chain" not in st.session_state or st.session_state.get("current_model") != selected_model:
        selected_llm = ChatGroq(api_key=GROQ_API_KEY, model_name=selected_model)
        st.session_state["chain"] = build_chain(db_json, selected_llm)
        st.session_state["current_model"] = selected_model

    chain = st.session_state["chain"]

    st.title("🦅 IA Águia - Respostas com Base no Banco de Dados 🚛")
    st.markdown("### Faça suas perguntas sobre os dados da frota:")

    with st.expander("Visualizar JSON do banco de dados"):
        st.json(json.loads(db_json))

    if "memoria" not in st.session_state:
        st.session_state["memoria"] = ConversationBufferMemory()
    memoria = st.session_state["memoria"]

    if st.button("Limpar memória"):
        st.session_state["memoria"] = ConversationBufferMemory()
        memoria = st.session_state["memoria"]
        st.success("Memória limpa.")

    for mensagem in memoria.buffer_as_messages:
        with st.chat_message(mensagem.type):
            st.markdown(mensagem.content)

    user_input = st.chat_input("Digite sua pergunta sobre os dados da frota...")
    if user_input:
        with st.chat_message("human"):
            st.markdown(user_input)
        memoria.chat_memory.add_user_message(user_input)
        try:
            resposta = chain.invoke({"input": user_input, "chat_history": memoria.buffer_as_messages})
            resposta_text = extract_response_text(resposta)
            resposta_formatada = format_response_markdown(resposta_text)
            memoria.chat_memory.add_ai_message(resposta_formatada)
            with st.chat_message("assistant"):
                st.markdown(resposta_formatada)
            st.session_state["memoria"] = memoria
        except Exception as e:
            st.error("❌ Ocorreu um erro ao processar sua pergunta. Por favor, tente novamente mais tarde.")
            st.write(f"Detalhes do erro: {e}")

# =============================================================================
# Para rodar o chatbot, chame a função screen_ia()
# =============================================================================
if __name__ == "__main__":
    screen_ia()
