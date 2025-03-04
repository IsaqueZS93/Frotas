import sqlite3
import pandas as pd
import plotly.express as px

def get_dataframe_from_db(query: str, db_path: str) -> pd.DataFrame:
    """
    Conecta-se ao banco de dados SQLite especificado e retorna um DataFrame com o resultado da query.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def plot_abastecimento_range_slider(db_path: str) -> None:
    """
    Gera um gráfico de linha interativo com range slider para os gastos de abastecimento.
    Usa os campos 'data_hora' e 'valor_total' da tabela 'abastecimentos'.
    """
    query = "SELECT data_hora, valor_total FROM abastecimentos"
    df = get_dataframe_from_db(query, db_path)
    
    # Converte a coluna de data e ordena os dados
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    df = df.sort_values('data_hora')
    
    # Agregação diária (ou ajuste conforme a granularidade desejada)
    df_grouped = df.groupby(df['data_hora'].dt.date).sum().reset_index()
    df_grouped['data_hora'] = pd.to_datetime(df_grouped['data_hora'])
    
    # Cria o gráfico de linha com range slider
    fig = px.line(df_grouped, x='data_hora', y='valor_total',
                  title="Gastos de Abastecimento com Range Slider",
                  labels={'data_hora': 'Data', 'valor_total': 'Valor Total (R$)'})
    fig.update_layout(xaxis_rangeslider_visible=True, template='plotly_white')
    fig.show()

def plot_histogram_ano_fabricacao(db_path: str) -> None:
    """
    Gera um histograma da distribuição do ano de fabricação dos veículos, 
    utilizando o campo 'ano_fabricacao' da tabela 'veiculos'.
    """
    query = "SELECT ano_fabricacao FROM veiculos"
    df = get_dataframe_from_db(query, db_path)
    
    fig = px.histogram(df, x='ano_fabricacao',
                       nbins=20,
                       title="Distribuição do Ano de Fabricação dos Veículos",
                       labels={'ano_fabricacao': 'Ano de Fabricação', 'count': 'Frequência'})
    fig.update_layout(template='plotly_white')
    fig.show()

def plot_line_chart_comparativo_veiculos(db_path: str, placa1: str, placa2: str) -> None:
    """
    Gera um gráfico de linha comparativo dos gastos de abastecimento de dois veículos,
    com base no campo 'placa' da tabela 'abastecimentos'.
    
    A função agrupa os dados por mês e soma os gastos ('valor_total') para cada veículo.
    """
    query = f"""
        SELECT data_hora, placa, valor_total 
        FROM abastecimentos 
        WHERE placa IN ('{placa1}', '{placa2}')
    """
    df = get_dataframe_from_db(query, db_path)
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    
    # Cria uma coluna Ano-Mês para agregação
    df['AnoMes'] = df['data_hora'].dt.to_period('M').astype(str)
    df_grouped = df.groupby(['AnoMes', 'placa']).sum().reset_index()
    
    fig = px.line(df_grouped, x='AnoMes', y='valor_total', color='placa',
                  markers=True,
                  title=f"Comparativo de Gastos de Abastecimento: {placa1} vs {placa2}",
                  labels={'AnoMes': 'Ano-Mês', 'valor_total': 'Valor Total (R$)', 'placa': 'Placa'})
    fig.update_layout(template='plotly_white')
    fig.show()

def plot_3d_scatter_abastecimentos(db_path: str) -> None:
    """
    Gera um gráfico 3D interativo a partir dos dados de abastecimentos.
    
    Utiliza:
      - Eixo X: km_atual (hodômetro atual)
      - Eixo Y: quantidade_litros (litros abastecidos)
      - Eixo Z: valor_total (gasto total)
      
    A cor dos pontos representa a placa do veículo.
    """
    query = "SELECT km_atual, quantidade_litros, valor_total, placa FROM abastecimentos"
    df = get_dataframe_from_db(query, db_path)
    
    fig = px.scatter_3d(df, x='km_atual', y='quantidade_litros', z='valor_total',
                        color='placa',
                        title="Análise 3D dos Abastecimentos",
                        labels={
                            'km_atual': 'Quilometragem Atual', 
                            'quantidade_litros': 'Quantidade de Litros', 
                            'valor_total': 'Valor Total (R$)', 
                            'placa': 'Placa'
                        })
    fig.update_layout(template='plotly_white')
    fig.show()

# Exemplo de uso das funções:
if __name__ == '__main__':
    # Caminho para o banco de dados SQLite
    db_path = r"C:\Users\Novaes Engenharia\github - deploy\Frotas\fleet_management.db"
    
    # Gera o gráfico com range slider para abastecimentos
    plot_abastecimento_range_slider(db_path)
    
    # Gera o histograma do ano de fabricação dos veículos
    plot_histogram_ano_fabricacao(db_path)
    
    # Gera o gráfico comparativo de gastos de abastecimento para dois veículos
    # Substitua 'ABC1234' e 'XYZ5678' pelas placas reais existentes na tabela 'abastecimentos'
    plot_line_chart_comparativo_veiculos(db_path, 'ABC1234', 'XYZ5678')
    
    # Gera o gráfico 3D de abastecimentos
    plot_3d_scatter_abastecimentos(db_path)
