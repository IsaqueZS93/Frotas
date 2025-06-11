"""
pages/dashboard/dashboard_alerts.py

Módulo responsável por exibir alertas e notificações importantes no Dashboard.

Funcionalidades:
- Exibe alertas de veículos com alta quilometragem.
- Exibe alertas de abastecimentos inconsistentes.
- Exibe alertas de usuários inativos há muito tempo.
- Exibe alertas de inconsistências na quilometragem.
- Exibe previsões de manutenção.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.models.models_veiculos import get_all_veiculos
from database.models.models_abastecimentos import get_all_abastecimentos
from database.models.models_usuarios import get_all_usuarios
from utils.advanced_analytics import (
    calcular_evolucao_km,
    detectar_inconsistencias_km,
    prever_manutencao
)

# ==============================
# 📢 Função Principal - Renderiza Alertas no Dashboard
# ==============================
def render_alerts():
    """
    Exibe alertas baseados nos dados do sistema.
    """
    st.markdown("### 🔔 Alertas do Sistema")

    # Carregar dados
    veiculos = get_all_veiculos()
    abastecimentos = get_all_abastecimentos()
    usuarios = get_all_usuarios()

    df_veiculos = pd.DataFrame(veiculos)
    df_abastecimentos = pd.DataFrame(abastecimentos)
    df_usuarios = pd.DataFrame(usuarios)

    # ==============================
    # 🚗 ALERTA: Veículos com Alta Quilometragem
    # ==============================
    if not df_veiculos.empty:
        veiculos_acima_km = df_veiculos[df_veiculos["km_atual"] > 200000]  # Definir limite de alerta

        if not veiculos_acima_km.empty:
            st.warning("⚠️ **Veículos com alta quilometragem (> 200.000 km):**")
            for _, row in veiculos_acima_km.iterrows():
                st.text(f"🚗 {row['modelo']} ({row['placa']}) - {row['km_atual']} km")
    else:
        st.info("📌 Nenhum veículo cadastrado no sistema.")

    # ==============================
    # ⛽ ALERTA: Abastecimentos Suspeitos
    # ==============================
    if not df_abastecimentos.empty:
        df_abastecimentos["data_abastecimento"] = pd.to_datetime(df_abastecimentos["data_abastecimento"])
        df_abastecimentos["consumo_km_litro"] = df_abastecimentos["km_abastecimento"] / df_abastecimentos["quantidade_litros"]

        # Define um limite de consumo irreal (ex.: acima de 50 km/L ou abaixo de 2 km/L)
        abastecimentos_suspeitos = df_abastecimentos[
            (df_abastecimentos["consumo_km_litro"] > 50) | (df_abastecimentos["consumo_km_litro"] < 2)
        ]

        if not abastecimentos_suspeitos.empty:
            st.error("🚨 **Abastecimentos suspeitos detectados:**")
            for _, row in abastecimentos_suspeitos.iterrows():
                st.text(f"⛽ {row['placa']} - {row['tipo_combustivel']} | {row['consumo_km_litro']:.2f} km/L")
        else:
            st.success("✅ Nenhum abastecimento suspeito foi detectado.")
    else:
        st.info("📌 Nenhum abastecimento registrado ainda.")

    # ==============================
    # 👤 ALERTA: Usuários Inativos
    # ==============================
    if not df_usuarios.empty:
        df_usuarios["ultimo_login"] = pd.to_datetime(df_usuarios["ultimo_login"])
        usuarios_inativos = df_usuarios[df_usuarios["ultimo_login"] < datetime.now() - timedelta(days=60)]

        if not usuarios_inativos.empty:
            st.warning("⚠️ **Usuários inativos há mais de 60 dias:**")
            for _, row in usuarios_inativos.iterrows():
                st.text(f"👤 {row['nome']} ({row['email']}) - Último login: {row['ultimo_login'].date()}")
    else:
        st.info("📌 Nenhum usuário cadastrado no sistema.")

    # ==============================
    # 📏 ALERTA: Inconsistências na Quilometragem
    # ==============================
    if not df_veiculos.empty:
        inconsistencias_gerais = []
        for _, veiculo in df_veiculos.iterrows():
            df_evolucao = calcular_evolucao_km(abastecimentos, [], veiculo['id'])
            if not df_evolucao.empty:
                inconsistencias = detectar_inconsistencias_km(df_evolucao)
                for inc in inconsistencias:
                    inc['placa'] = veiculo['placa']
                    inconsistencias_gerais.append(inc)

        if inconsistencias_gerais:
            st.error("🚨 **Inconsistências na quilometragem detectadas:**")
            for inc in inconsistencias_gerais:
                st.text(f"🚗 {inc['placa']} - {inc['data'].strftime('%d/%m/%Y')} - {inc['tipo']} - Diferença: {inc['diferenca']} km")

    # ==============================
    # 🔧 ALERTA: Previsões de Manutenção
    # ==============================
    if not df_veiculos.empty:
        manutencoes_proximas = []
        for _, veiculo in df_veiculos.iterrows():
            df_evolucao = calcular_evolucao_km(abastecimentos, [], veiculo['id'])
            if not df_evolucao.empty:
                previsao = prever_manutencao(df_evolucao)
                if previsao and previsao['dias_ate_manutencao'] <= 30:  # Alerta para manutenções nos próximos 30 dias
                    previsao['placa'] = veiculo['placa']
                    manutencoes_proximas.append(previsao)

        if manutencoes_proximas:
            st.warning("🔧 **Manutenções próximas:**")
            for manut in manutencoes_proximas:
                st.text(f"🚗 {manut['placa']} - Data prevista: {manut['data_prevista'].strftime('%d/%m/%Y')} (Faltam {manut['km_restante']:,.0f} km)")

    # ==============================
    # 📌 Rodapé
    # ==============================
    st.markdown("<p class='footer'>© 2024 Fleet Management</p>", unsafe_allow_html=True)

