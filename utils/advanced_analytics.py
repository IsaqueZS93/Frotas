"""
utils/advanced_analytics.py

Este módulo contém funções avançadas para análise de dados do sistema de gestão de frota.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

def calcular_evolucao_km(abastecimentos: List[Dict], checklists: List[Dict], veiculo_id: int) -> pd.DataFrame:
    """
    Calcula a evolução de quilometragem de um veículo com base em abastecimentos e checklists.
    
    Args:
        abastecimentos: Lista de dicionários com dados de abastecimentos
        checklists: Lista de dicionários com dados de checklists
        veiculo_id: ID do veículo
        
    Returns:
        DataFrame com a evolução da quilometragem
    """
    # Converter para DataFrame
    df_abast = pd.DataFrame(abastecimentos)
    df_check = pd.DataFrame(checklists)
    
    # Filtrar por veículo
    df_abast = df_abast[df_abast['veiculo_id'] == veiculo_id]
    df_check = df_check[df_check['veiculo_id'] == veiculo_id]
    
    # Preparar dados de abastecimentos
    df_abast['data'] = pd.to_datetime(df_abast['data_abastecimento'])
    df_abast['tipo'] = 'abastecimento'
    df_abast = df_abast[['data', 'km_abastecimento', 'tipo']]
    df_abast.columns = ['data', 'km', 'tipo']
    
    # Preparar dados de checklists
    df_check['data'] = pd.to_datetime(df_check['data_vistoria'])
    df_check['tipo'] = 'checklist'
    df_check = df_check[['data', 'km_atual', 'tipo']]
    df_check.columns = ['data', 'km', 'tipo']
    
    # Combinar dados
    df_evolucao = pd.concat([df_abast, df_check])
    df_evolucao = df_evolucao.sort_values('data')
    
    # Calcular médias móveis
    df_evolucao['km_media_7d'] = df_evolucao['km'].rolling(window=7, min_periods=1).mean()
    df_evolucao['km_media_30d'] = df_evolucao['km'].rolling(window=30, min_periods=1).mean()
    
    return df_evolucao

def detectar_inconsistencias_km(df_evolucao: pd.DataFrame) -> List[Dict]:
    """
    Detecta inconsistências na evolução da quilometragem.
    
    Args:
        df_evolucao: DataFrame com a evolução da quilometragem
        
    Returns:
        Lista de dicionários com inconsistências detectadas
    """
    inconsistencias = []
    
    # Verificar quilometragem negativa
    df_evolucao['km_diff'] = df_evolucao['km'].diff()
    km_negativos = df_evolucao[df_evolucao['km_diff'] < 0]
    
    for _, row in km_negativos.iterrows():
        inconsistencias.append({
            'data': row['data'],
            'tipo': 'km_negativo',
            'km_atual': row['km'],
            'km_anterior': row['km'] - row['km_diff'],
            'diferenca': row['km_diff']
        })
    
    # Verificar saltos muito grandes
    km_saltos = df_evolucao[df_evolucao['km_diff'] > 1000]  # Mais de 1000km em um dia
    
    for _, row in km_saltos.iterrows():
        inconsistencias.append({
            'data': row['data'],
            'tipo': 'salto_grande',
            'km_atual': row['km'],
            'km_anterior': row['km'] - row['km_diff'],
            'diferenca': row['km_diff']
        })
    
    return inconsistencias

def calcular_metricas_eficiencia(df_evolucao: pd.DataFrame, abastecimentos: List[Dict]) -> Dict:
    """
    Calcula métricas de eficiência do veículo.
    
    Args:
        df_evolucao: DataFrame com a evolução da quilometragem
        abastecimentos: Lista de dicionários com dados de abastecimentos
        
    Returns:
        Dicionário com métricas de eficiência
    """
    if df_evolucao.empty or not abastecimentos:
        return {}
    
    # Calcular quilometragem total
    km_total = df_evolucao['km'].max() - df_evolucao['km'].min()
    
    # Calcular consumo total
    df_abast = pd.DataFrame(abastecimentos)
    litros_total = df_abast['quantidade_litros'].sum()
    valor_total = df_abast['valor_total'].sum()
    
    # Calcular métricas
    km_por_litro = km_total / litros_total if litros_total > 0 else 0
    custo_por_km = valor_total / km_total if km_total > 0 else 0
    
    # Calcular tendências
    df_evolucao['km_diario'] = df_evolucao['km'].diff()
    km_medio_diario = df_evolucao['km_diario'].mean()
    
    return {
        'km_total': km_total,
        'litros_total': litros_total,
        'valor_total': valor_total,
        'km_por_litro': km_por_litro,
        'custo_por_km': custo_por_km,
        'km_medio_diario': km_medio_diario
    }

def prever_manutencao(df_evolucao: pd.DataFrame, km_ultima_manutencao: int = 0) -> Dict:
    """
    Prevê quando será necessária a próxima manutenção baseada na quilometragem.
    
    Args:
        df_evolucao: DataFrame com a evolução da quilometragem
        km_ultima_manutencao: Quilometragem da última manutenção
        
    Returns:
        Dicionário com previsões de manutenção
    """
    if df_evolucao.empty:
        return {}
    
    km_atual = df_evolucao['km'].max()
    km_restante = 10000 - (km_atual - km_ultima_manutencao)  # Exemplo: manutenção a cada 10.000km
    
    # Calcular dias até a próxima manutenção
    df_evolucao['km_diario'] = df_evolucao['km'].diff()
    km_medio_diario = df_evolucao['km_diario'].mean()
    
    dias_ate_manutencao = km_restante / km_medio_diario if km_medio_diario > 0 else float('inf')
    
    return {
        'km_atual': km_atual,
        'km_ultima_manutencao': km_ultima_manutencao,
        'km_restante': km_restante,
        'dias_ate_manutencao': dias_ate_manutencao,
        'data_prevista': datetime.now() + timedelta(days=dias_ate_manutencao) if dias_ate_manutencao != float('inf') else None
    } 