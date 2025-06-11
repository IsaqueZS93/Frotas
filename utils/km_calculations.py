"""
utils/km_calculations.py

Este módulo contém funções para cálculos relacionados ao consumo de combustível e quilometragem dos veículos.

Funcionalidades:
- Cálculo do custo médio por KM rodado.
- Cálculo da eficiência de combustível (KM/L).
- Validação de registros inconsistentes de quilometragem.
"""

from database.models.models_abastecimentos import get_all_abastecimentos
from database.models.models_veiculos import get_veiculo_by_id


def calcular_custo_por_km(abastecimentos, veiculo_id):
    """
    Calcula o custo médio por KM rodado baseado no histórico de abastecimentos.

    Parâmetros:
        abastecimentos (list | pd.DataFrame): Lista de dicionários ou DataFrame contendo abastecimentos.
        veiculo_id (int): ID do veículo.

    Retorna:
        float | None: Custo médio por KM ou None se não houver dados suficientes.
    """
    if isinstance(abastecimentos, pd.DataFrame):
        if abastecimentos.empty:
            return None
        abastecimentos = abastecimentos.to_dict(orient="records")

    abastecimentos_filtrados = [a for a in abastecimentos if a["veiculo_id"] == veiculo_id]

    if len(abastecimentos_filtrados) < 2:
        return None  # Não há dados suficientes para calcular

    km_inicial = abastecimentos_filtrados[0]["km_abastecimento"]
    km_final = abastecimentos_filtrados[-1]["km_abastecimento"]
    total_gasto = sum(a["valor_total"] for a in abastecimentos_filtrados)

    if km_final > km_inicial:
        custo_por_km = total_gasto / (km_final - km_inicial)
        return round(custo_por_km, 2)

    return None


def calcular_consumo_km_por_litro(veiculo_id):
    """
    Calcula a eficiência de combustível do veículo (KM/L).

    Parâmetros:
        veiculo_id (int): ID do veículo.

    Retorna:
        float | None: Média de KM/L ou None se não houver dados suficientes.
    """
    abastecimentos = get_all_abastecimentos()
    abastecimentos = [a for a in abastecimentos if a["veiculo_id"] == veiculo_id]

    if len(abastecimentos) < 2:
        return None  # Sem dados suficientes

    km_inicial = abastecimentos[0]["km_abastecimento"]
    km_final = abastecimentos[-1]["km_abastecimento"]
    total_litros = sum(a["quantidade_litros"] for a in abastecimentos)

    if km_final > km_inicial and total_litros > 0:
        consumo = (km_final - km_inicial) / total_litros
        return round(consumo, 2)

    return None

def atualizar_km_veiculo(veiculo_id, novo_km):
    """
    Atualiza a quilometragem de um veículo no banco de dados.

    Parâmetros:
        veiculo_id (int): ID do veículo.
        novo_km (int): Nova quilometragem a ser registrada.

    Retorna:
        bool: True se a atualização foi bem-sucedida, False caso contrário.
    """
    query = """
    UPDATE veiculos
    SET km_atual = ?
    WHERE id = ?
    """

    try:
        execute_query(query, (novo_km, veiculo_id))
        return True
    except Exception as e:
        print(f"Erro ao atualizar quilometragem do veículo {veiculo_id}: {e}")
        return False


def validar_km_abastecimento(veiculo_id, km_atual):
    """
    Valida se o KM informado para abastecimento é consistente.

    Parâmetros:
        veiculo_id (int): ID do veículo.
        km_atual (int): Quilometragem informada no abastecimento.

    Retorna:
        bool: True se o KM for válido, False caso contrário.
    """
    veiculo = get_veiculo_by_id(veiculo_id)
    if not veiculo:
        return False

    km_ultimo_abastecimento = max(
        [a["km_abastecimento"] for a in get_all_abastecimentos() if a["veiculo_id"] == veiculo_id], 
        default=0
    )

    return km_atual >= km_ultimo_abastecimento
def verificar_inconsistencia_km(veiculo_id):
    """
    Verifica se há inconsistências nos registros de quilometragem do veículo.

    Parâmetros:
        veiculo_id (int): ID do veículo.

    Retorna:
        list: Lista de inconsistências encontradas, se houver.
    """
    abastecimentos = get_all_abastecimentos()
    abastecimentos = [a for a in abastecimentos if a["veiculo_id"] == veiculo_id]
    inconsistencias = []

    if len(abastecimentos) < 2:
        return inconsistencias  # Sem dados suficientes para verificar inconsistências

    for i in range(1, len(abastecimentos)):
        if abastecimentos[i]["km_abastecimento"] < abastecimentos[i - 1]["km_abastecimento"]:
            inconsistencias.append({
                "data": abastecimentos[i]["data_abastecimento"],
                "km_registrado": abastecimentos[i]["km_abastecimento"],
                "km_anterior": abastecimentos[i - 1]["km_abastecimento"],
            })

    return inconsistencias