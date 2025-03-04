import os
import sys
import streamlit as st
import pandas as pd
from datetime import date
from dotenv import load_dotenv

# Ajusta o PYTHONPATH para incluir o diretório raiz do projeto.
# Isso é útil para que o Python encontre o pacote 'backend'.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Verifique se a estrutura de pastas está conforme:
# Frotas/
# ├── backend/
# │   ├── __init__.py           <-- Crie este arquivo se não existir.
# │   └── db_models/
# │       ├── __init__.py       <-- Crie este arquivo se não existir.
# │       └── BD_Graficos_IA.py
# ├── frontend/
# │   └── screens/
# │       └── Screen_Graficos_IA.py
# └── .env

# Carrega as variáveis do arquivo .env (localizado na raiz do projeto)
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

# Exemplo: obter a chave da API (caso seja necessário em alguma lógica futura)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
st.write("GROQ_API_KEY carregada:", GROQ_API_KEY)

# Importa as funções de gráficos do módulo backend.
# IMPORTANTE: As funções devem retornar a figura Plotly (ex.: return fig)
from backend.db_models.BD_Graficos_IA import (
    plot_abastecimento_range_slider,
    plot_histogram_ano_fabricacao,
    plot_line_chart_comparativo_veiculos,
    plot_3d_scatter_abastecimentos
)

def get_vehicle_plates(db_path: str) -> list:
    """
    Conecta ao banco de dados e retorna uma lista com as placas dos veículos.
    """
    import sqlite3
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT placa FROM veiculos", conn)
    conn.close()
    return df['placa'].unique().tolist()

def screen_graficos_ia():
    st.title("Tela de Gráficos IA")
    st.write("Selecione o tipo de gráfico que deseja visualizar e interaja com os dados reais do banco de dados.")
    
    # Caminho do banco de dados (ajuste conforme necessário)
    db_path = r"C:\Users\Novaes Engenharia\github - deploy\Frotas\fleet_management.db"
    
    # Seletor de tipo de gráfico
    graph_type = st.selectbox("Escolha o tipo de gráfico:", 
                              ["Selecione...", 
                               "Abastecimento com Range Slider", 
                               "Histograma do Ano de Fabricação", 
                               "Comparativo de Gastos entre Veículos", 
                               "Gráfico 3D de Abastecimentos"])
    
    if graph_type != "Selecione...":
        if graph_type == "Abastecimento com Range Slider":
            st.subheader("Abastecimento com Range Slider")
            # Permite escolher um intervalo de datas (a função pode ser adaptada para filtrar esses dados)
            start_date = st.date_input("Data Inicial", value=date(2023, 1, 1))
            end_date = st.date_input("Data Final", value=date.today())
            st.write(f"Exibindo dados de {start_date} até {end_date}")
            # Neste exemplo, a função não recebe os parâmetros start_date/end_date.
            # Em uma versão aprimorada, esses parâmetros podem ser utilizados na query.
            fig = plot_abastecimento_range_slider(db_path)
            st.plotly_chart(fig, use_container_width=True)
            
        elif graph_type == "Histograma do Ano de Fabricação":
            st.subheader("Histograma do Ano de Fabricação dos Veículos")
            fig = plot_histogram_ano_fabricacao(db_path)
            st.plotly_chart(fig, use_container_width=True)
            
        elif graph_type == "Comparativo de Gastos entre Veículos":
            st.subheader("Comparativo de Gastos entre Veículos")
            # Obtém as placas disponíveis no banco de dados para permitir a seleção dinâmica
            plates = get_vehicle_plates(db_path)
            if len(plates) < 2:
                st.warning("Não há veículos suficientes para comparação.")
            else:
                placa1 = st.selectbox("Escolha o veículo 1 (Placa):", plates, index=0)
                # Remove a placa selecionada para a primeira escolha
                remaining_plates = [p for p in plates if p != placa1]
                placa2 = st.selectbox("Escolha o veículo 2 (Placa):", remaining_plates, index=0)
                fig = plot_line_chart_comparativo_veiculos(db_path, placa1, placa2)
                st.plotly_chart(fig, use_container_width=True)
            
        elif graph_type == "Gráfico 3D de Abastecimentos":
            st.subheader("Gráfico 3D de Abastecimentos")
            fig = plot_3d_scatter_abastecimentos(db_path)
            st.plotly_chart(fig, use_container_width=True)
        
        st.info("Interaja com o gráfico usando as ferramentas integradas (zoom, hover, etc.).")

# Esta função pode ser importada e chamada pela aplicação principal
if __name__ == '__main__':
    screen_graficos_ia()
