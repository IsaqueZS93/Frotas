# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\Dashboards\Dash_Checklists.py

import streamlit as st
import pandas as pd
import plotly.express as px
from Dash_Utils import load_checklists
import plotly.graph_objects as go
from backend.db_models.DB_Models_User import get_user_name_by_id  # Função para buscar nome do usuário pelo ID

# -------------------------------
# 📊 Status Checklists
# -------------------------------
def status_checklists():
    """Exibe os cards com estatísticas de checklists."""
    df = load_checklists()

    if df.empty:
        st.warning("🚨 Nenhum checklist disponível.")
        return df

    # 🔹 Verifica se todas as colunas necessárias estão no DataFrame antes de usá-las
    required_columns = [
        'pneus_ok', 'farois_setas_ok', 'freios_ok', 'oleo_ok', 
        'vidros_retrovisores_ok', 'itens_seguranca_ok'
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"🚨 Erro: As seguintes colunas não estão no DataFrame: {missing_columns}")
        return df  # Retorna o DataFrame vazio para evitar mais erros
    
    # ✅ Aplica a filtragem agora que garantimos que as colunas existem
    checklists_com_problema = df[
        (~df['pneus_ok']) | (~df['farois_setas_ok']) | (~df['freios_ok']) |
        (~df['oleo_ok']) | (~df['vidros_retrovisores_ok']) | (~df['itens_seguranca_ok'])
    ]

    total_checklists = len(df)
    percentual_problemas = (len(checklists_com_problema) / total_checklists) * 100 if total_checklists > 0 else 0
    
    col1, col2 = st.columns(2)
    col1.metric("📋 Total de Checklists", f"{total_checklists}")
    col2.metric("⚠️ Percentual com Problemas", f"{percentual_problemas:.2f} %")

    return df


# -------------------------------
# 📈 Gráfico de Problemas Encontrados
# -------------------------------
def grafico_problemas(df):
    """Gera um gráfico interativo mostrando os problemas mais frequentes nos checklists."""
    
    problemas = {
        'Pneus': (~df['pneus_ok']).sum(),
        'Faróis e Setas': (~df['farois_setas_ok']).sum(),
        'Freios': (~df['freios_ok']).sum(),
        'Óleo': (~df['oleo_ok']).sum(),
        'Vidros e Retrovisores': (~df['vidros_retrovisores_ok']).sum(),
        'Itens de Segurança': (~df['itens_seguranca_ok']).sum()
    }

    df_problemas = pd.DataFrame(list(problemas.items()), columns=['Problema', 'Ocorrências'])

    if df_problemas['Ocorrências'].sum() == 0:
        st.warning("📌 Nenhum problema encontrado nos checklists.")
        return

    fig = px.bar(df_problemas, x='Problema', y='Ocorrências', text_auto=True, 
                 title="Problemas Mais Comuns nos Checklists", color='Ocorrências')
    
    st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def dashboard_checklists():
    """Função principal para exibir estatísticas de checklists e rankings."""
    
    st.title("📋 Estatísticas de Checklists")
    df = status_checklists()

    if not df.empty:
        grafico_problemas(df)
        rank_checklists(df)
        projecao_consumo(df)
    else:
        st.warning("🚨 Nenhum checklist disponível.")

# -------------------------------
# 🏆 Rank de Condutores e Veículos (PÓDIO)
# -------------------------------
def rank_checklists(df):
    """Exibe os rankings de condutores e veículos com visualização em pódio lado a lado."""

    st.subheader("🏆 Ranking de Checklists")

    # 🔹 Ranking de condutores
    top_condutores = df['id_usuario'].value_counts().head(3).reset_index()
    top_condutores.columns = ['ID Usuário', 'Checklists Realizados']
    top_condutores['Nome Usuário'] = top_condutores['ID Usuário'].apply(get_user_name_by_id)

    # 🔹 Ranking de veículos mais econômicos
    df_consumo = df.groupby('placa').agg({'km_informado': 'sum', 'id': 'count'}).reset_index()
    df_consumo['KM por Checklist'] = df_consumo['km_informado'] / df_consumo['id']

    # ✅ Garante que a coluna esteja corretamente nomeada para evitar KeyError
    df_consumo.rename(columns={'placa': 'Placa'}, inplace=True)

    df_consumo = df_consumo[['Placa', 'KM por Checklist']].sort_values(by='KM por Checklist', ascending=False).head(3)

    # 🔹 Exibição lado a lado
    col1, col2 = st.columns(2)

    with col1:
        if not top_condutores.empty and len(top_condutores) >= 3:
            st.write("👤 **Condutores com mais Checklists**")
            plot_podio(top_condutores, "Nome Usuário", "Checklists Realizados")
        else:
            st.warning("📌 Dados insuficientes para o pódio de condutores.")

    with col2:
        if not df_consumo.empty and len(df_consumo) >= 3:
            st.write("🚗 **Veículos mais econômicos**")
            plot_podio(df_consumo, "Placa", "KM por Checklist")
        else:
            st.warning("📌 Dados insuficientes para o pódio de veículos.")

# -------------------------------
# 🎨 Função para Criar Pódio (Genérico)
# -------------------------------
def plot_podio(df, categoria, valor):
    """Cria um gráfico de pódio para destacar os três primeiros colocados."""

    if df.shape[0] < 3:
        st.warning("🚨 Dados insuficientes para gerar um pódio completo.")
        return

    # 🔹 Ordenação fixa para garantir que o 1º lugar fique no centro
    df = df.sort_values(by=valor, ascending=False).reset_index(drop=True)

    # 🔹 Posições fixas no eixo X para garantir o formato de pódio
    positions = ["2º Lugar", "1º Lugar", "3º Lugar"]
    x_positions = [1, 2, 3]  # Mantém o 1º lugar no meio

    # 🔹 Altura proporcional ao valor do ranking
    heights = [df.iloc[1][valor], df.iloc[0][valor], df.iloc[2][valor]]

    # 🔹 Definição de cores (Ouro, Prata, Bronze)
    colors = ["silver", "gold", "brown"]

    fig = go.Figure()

    for i in range(3):
        fig.add_trace(go.Bar(
            x=[positions[i]],
            y=[heights[i]],
            text=[f"{df.iloc[i][categoria]}<br>{df.iloc[i][valor]:.1f}"],
            textposition="outside",
            marker=dict(color=colors[i]),
            name=positions[i]
        ))

    # 🔹 Ajuste do layout
    fig.update_layout(
        title=f"Pódio - {categoria}",
        xaxis=dict(title="Posição"),
        yaxis=dict(title=valor),
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------------
# 📊 Projeção de Consumo Futuro
# -------------------------------
def projecao_consumo(df):
    """Exibe um gráfico de projeção de consumo para os próximos meses."""
    st.subheader("📈 Projeção de Consumo para os Próximos Meses")

    # ✅ Converte 'data_hora' para datetime se necessário
    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')

    # ✅ Garante que os meses sejam strings, não `Period`
    df['mes'] = df['data_hora'].dt.strftime('%Y-%m')  # 🔹 Agora é string

    # ✅ Agrupar por mês e contar os checklists
    df_grouped = df.groupby('mes').count()['id'].reset_index()
    df_grouped.columns = ['Mês', 'Total Checklists']

    # ✅ Criar gráfico interativo com Plotly
    import plotly.express as px
    fig = px.bar(df_grouped, x='Mês', y='Total Checklists',
                 title="📊 Projeção de Checklists para os Próximos Meses",
                 text_auto=True)

    # ✅ Exibir o gráfico
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------
# 🚀 Execução do Dashboard
# -------------------------------


if __name__ == "__main__":
    dashboard_checklists()
