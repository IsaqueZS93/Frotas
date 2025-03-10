import streamlit as st
import sys
import os
from datetime import datetime
from backend.services.Service_Google_Drive import get_folder_id_by_name, list_files_in_folder

# 🔹 Adiciona o caminho base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔹 Importações dos módulos do projeto
from backend.db_models.DB_Models_Abastecimento import (
    get_all_abastecimentos, get_abastecimento_by_placa, get_abastecimento_by_usuario, 
    delete_abastecimento, get_abastecimento_by_id, create_abastecimento
)
from backend.db_models.DB_Models_Veiculo import get_all_veiculos, get_veiculo_by_placa
from backend.db_models.DB_Models_User import get_all_users

# 🔹 ID da pasta principal "Abastecimentos" no Google Drive
PASTA_ABASTECIMENTOS_ID = "1zw9CR0InO4J0ns1MvETMMiZwY7qfAW3A"

def user_is_admin():
    """Verifica se o usuário é ADMIN."""
    return "user_type" in st.session_state and st.session_state.user_type == "ADMIN"

def abastecimento_list_edit_screen():
    """Tela para listar, editar e excluir abastecimentos."""
    
    st.title("📋 Gerenciar Abastecimentos")

    # 🔹 Verificação de permissão
    if not user_is_admin():
        st.error("⚠️ Apenas usuários ADMIN podem acessar esta tela.")
        return

    # 🔹 Buscar lista de veículos e usuários para os filtros
    veiculos = get_all_veiculos()
    lista_placas = [veiculo["placa"] for veiculo in veiculos] if veiculos else []

    usuarios = get_all_users()
    lista_usuarios = [f"{user['id']} - {user['nome_completo']}" for user in usuarios] if usuarios else []

    # 🔹 Filtros
    st.subheader("🔍 Filtros de Busca")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_placa = st.selectbox("🚗 Filtrar por Placa", ["Todos"] + lista_placas)
    with col2:
        filtro_usuario = st.selectbox("👤 Filtrar por Usuário", ["Todos"] + lista_usuarios)
    with col3:
        filtro_data = st.date_input("📅 Filtrar por Data", value=None)

    # 🔹 Buscar abastecimentos com base nos filtros aplicados
    if filtro_placa != "Todos":
        abastecimentos = get_abastecimento_by_placa(filtro_placa)
    elif filtro_usuario != "Todos":
        user_id_str = filtro_usuario.split(" - ")[0]
        abastecimentos = get_abastecimento_by_usuario(user_id_str)
    else:
        abastecimentos = get_all_abastecimentos()

    # 🔹 Aplicar filtro de data
    if filtro_data:
        abastecimentos = [a for a in abastecimentos if datetime.strptime(a["data_hora"], "%d/%m/%Y %H:%M").date() == filtro_data]

    # 🔹 Exibir lista de abastecimentos
    st.subheader("📋 Lista de Abastecimentos")
    if not abastecimentos:
        st.warning("⚠️ Nenhum abastecimento encontrado.")
        return

    for abastecimento in abastecimentos:
        with st.expander(f"🚗 {abastecimento['placa']} - {abastecimento['data_hora']}"):
            col1, col2 = st.columns([2, 1])

            # Obter o KM atual do veículo usando a função get_veiculo_by_placa
            veiculo = get_veiculo_by_placa(abastecimento["placa"])
            km_atual = veiculo["hodometro_atual"] if veiculo else 0

            with col1:
                st.write(f"📍 **KM Abastecimento:** {km_atual('km_abastecimento')} km")
                st.write(f"⛽ **Quantidade:** {abastecimento['quantidade_litros']} L")
                st.write(f"💰 **Valor Total:** R$ {abastecimento['valor_total']}")
                st.write(f"💲 **Valor por Litro:** R$ {abastecimento['valor_por_litro']}")
                st.write(f"📝 **Observações:** {abastecimento.get('observacoes', 'Nenhuma')}")
            
            # 🔹 Removida a lógica de exibição de nota fiscal/imagens

            # 🔹 Edição do abastecimento
            st.subheader("✏️ Editar Abastecimento")
            novo_km_abastecimento = st.number_input(
                "📍 Novo KM Abastecimento",
                min_value=km_atual,
                step=1,
                value=abastecimento.get("km_abastecimento", km_atual),
                key=f"km_{abastecimento['id']}"
            )

            nova_quantidade_litros = st.number_input(
                "⛽ Nova Quantidade Abastecida (L)",
                min_value=0.1,
                step=0.1,
                value=abastecimento["quantidade_litros"],
                key=f"litros_{abastecimento['id']}"
            )

            novo_valor_total = st.number_input(
                "💰 Novo Valor Total Pago (R$)",
                min_value=0.01,
                step=0.01,
                value=abastecimento["valor_total"],
                key=f"total_{abastecimento['id']}"
            )

            novas_observacoes = st.text_area(
                "📝 Novas Observações",
                value=abastecimento.get("observacoes", ""),
                key=f"obs_{abastecimento['id']}"
            )

            novo_valor_por_litro = round(novo_valor_total / nova_quantidade_litros, 2) if nova_quantidade_litros > 0 else 0
            st.write(f"💲 **Novo Valor por Litro:** R$ {novo_valor_por_litro}")

            if st.button(f"💾 Salvar Alterações {abastecimento['placa']} ({abastecimento['data_hora']})", key=f"edit_{abastecimento['id']}"):
                delete_abastecimento(abastecimento['id'])
                create_abastecimento(
                    id_usuario=abastecimento["id_usuario"],
                    placa=abastecimento["placa"],
                    data_hora=abastecimento["data_hora"],
                    km_atual=km_atual,
                    km_abastecimento=novo_km_abastecimento,
                    quantidade_litros=nova_quantidade_litros,
                    tipo_combustivel=abastecimento["tipo_combustivel"],
                    valor_total=novo_valor_total,
                    nota_fiscal=abastecimento["nota_fiscal"],
                    observacoes=novas_observacoes
                )
                st.success("✅ Abastecimento atualizado com sucesso!")
                st.rerun()

            if st.button(f"🗑️ Excluir {abastecimento['placa']} ({abastecimento['data_hora']})", key=f"delete_{abastecimento['id']}"):
                delete_abastecimento(abastecimento['id'])
                st.success("✅ Abastecimento excluído com sucesso!")
                st.rerun()

if __name__ == "__main__":
    abastecimento_list_edit_screen()
