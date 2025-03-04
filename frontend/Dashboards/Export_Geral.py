# C:\Users\Novaes Engenharia\github - deploy\Frotas\frontend\Dashboards\Export_Geral.py

import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
import re

# 🔹 Função para remover emojis e caracteres não suportados
def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # Emojis
                               u"\U0001F300-\U0001F5FF"  # Símbolos e pictogramas
                               u"\U0001F680-\U0001F6FF"  # Transporte e mapas
                               u"\U0001F700-\U0001F77F"  # Símbolos diversos
                               u"\U0001F780-\U0001F7FF"  # Geometria
                               u"\U0001F800-\U0001F8FF"  # Suplemento de flechas
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# 🔹 Substitui emojis por palavras
def replace_emojis(text):
    replacements = {
        "📊": "[Gráfico]",
        "✅": "[OK]",
        "⚠️": "[Atenção]",
        "🚗": "[Carro]",
        "🔍": "[Busca]",
        "🏆": "[Ranking]",
        "📋": "[Lista]",
        "📄": "[Documento]"
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    return text

def generate_pdf(data, filename="relatorio_frotas.pdf"):
    """
    Gera um PDF contendo as estatísticas e gráficos apresentados nos dashboards.

    Parâmetros:
        data (dict): Dicionário contendo as informações dos dashboards.
        filename (str): Nome do arquivo de saída.

    Retorna:
        str: Caminho do arquivo gerado.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 🔹 Título do Relatório
    pdf.set_font("Arial", style="B", size=16)
    title = "Relatório de Frotas"
    pdf.cell(200, 10, title.encode('latin-1', 'ignore').decode('latin-1'), ln=True, align="C")

    # 🔹 Data da Geração
    pdf.set_font("Arial", size=12)
    date_generated = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    pdf.cell(200, 10, date_generated.encode('latin-1', 'ignore').decode('latin-1'), ln=True, align="C")
    pdf.ln(10)

    # 🔹 Estatísticas Gerais
    pdf.set_font("Arial", style="B", size=14)
    title_stats = "📊 Estatísticas Gerais"
    pdf.cell(200, 10, replace_emojis(title_stats).encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.set_font("Arial", size=12)
    for key, value in data["estatisticas"].items():
        line = f"{replace_emojis(key)}: {value}"
        pdf.cell(200, 8, line.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.ln(10)

    # 🔹 Tabela de Consumo e Custos
    pdf.set_font("Arial", style="B", size=14)
    title_costs = "📋 Consumo e Custos"
    pdf.cell(200, 10, replace_emojis(title_costs).encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.set_font("Arial", size=12)
    for row in data["tabela_consumo"]:
        pdf.cell(200, 8, row.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.ln(10)

    # 🔹 Problemas nos Checklists
    pdf.set_font("Arial", style="B", size=14)
    title_problems = "⚠️ Problemas Mais Comuns nos Checklists"
    pdf.cell(200, 10, replace_emojis(title_problems).encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.set_font("Arial", size=12)
    for key, value in data["problemas_checklist"].items():
        line = f"{replace_emojis(key)}: {value} ocorrências"
        pdf.cell(200, 8, line.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.ln(10)

    # 🔹 Ranking de Condutores
    pdf.set_font("Arial", style="B", size=14)
    title_ranking = "🏆 Ranking de Condutores"
    pdf.cell(200, 10, replace_emojis(title_ranking).encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.set_font("Arial", size=12)
    for row in data["ranking_condutores"]:
        pdf.cell(200, 8, row.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.ln(10)

    # 🔹 Salvar Arquivo
    pdf_dir = "pdf_reports"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, filename)
    pdf.output(pdf_path)

    return pdf_path

def export_dashboard():
    """
    Interface no Streamlit para exportação dos dashboards para PDF.
    """
    st.title("📄 Exportação de Relatórios")

    # 🔹 Simulação de Dados
    data = {
        "estatisticas": {
            "Total de Litros Abastecidos": "5000 L",
            "Custo Total": "R$ 200.000",
            "KM Total Percorrido": "150.000 km"
        },
        "tabela_consumo": [
            "Placa | KM/L | Custo/KM",
            "ABC-1234 | 8.5 KM/L | R$ 0.80",
            "XYZ-9876 | 7.2 KM/L | R$ 1.10"
        ],
        "problemas_checklist": {
            "Pneus": 10,
            "Faróis e Setas": 8,
            "Óleo": 5,
            "Freios": 3
        },
        "ranking_condutores": [
            "Condutor 1 - 25 checklists",
            "Condutor 2 - 20 checklists",
            "Condutor 3 - 18 checklists"
        ]
    }

    # 🔹 Botão para Gerar PDF
    if st.button("📥 Gerar PDF"):
        pdf_path = generate_pdf(data)
        with open(pdf_path, "rb") as file:
            st.download_button("📄 Baixar Relatório", file, file_name="relatorio_frotas.pdf", mime="application/pdf")
        st.success("✅ PDF gerado com sucesso!")

if __name__ == "__main__":
    export_dashboard()
