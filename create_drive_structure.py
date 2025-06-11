"""
create_drive_structure.py

Este script cria toda a estrutura de diretórios necessária no Google Drive para o projeto fleet_management.

Estrutura criada no Google Drive:

📂 Fleet Management (Pasta principal)
    ├── 📂 Imagens Veículos (Guarda todas as imagens dos veículos)
    │   ├── 📂 Placa_ABC1234 (Cada veículo terá uma pasta própria)
    │   │   ├── frente.jpg
    │   │   ├── traseira.jpg
    │   │   ├── lateral_direita.jpg
    │   │   ├── lateral_esquerda.jpg
    │   │   ├── interior1.jpg
    │   │   └── interior2.jpg
    │   ├── 📂 Placa_DEF5678 (Outro veículo)
    │   │   ├── frente.jpg
    │   │   ├── traseira.jpg
    │   │   ├── ...
    │   │   ├── interior2.jpg
    │   └── 📂 (outros veículos)
    │
    ├── 📂 Checklists (Guarda os checklists diários em PDF)
    │   ├── 📂 Data_YYYY-MM-DD (Cada data terá sua pasta)
    │   │   ├── checklist_usuario1.pdf
    │   │   ├── checklist_usuario2.pdf
    │   │   ├── ...
    │   └── 📂 (outros dias)
    │
    ├── 📂 Notas Fiscais (Guarda os comprovantes de abastecimento)
    │   ├── nota_12345.jpg
    │   ├── nota_67890.jpg
    │   ├── ...
    │
    └── 📂 Relatórios (PDFs gerados com métricas e gráficos)
"""

from services.google_drive_service import authenticate_google_drive

def create_drive_folder(folder_name, parent_folder_id=None):
    """
    Cria uma pasta no Google Drive se ela ainda não existir.

    Parâmetros:
        folder_name (str): Nome da pasta a ser criada.
        parent_folder_id (str, opcional): ID da pasta onde a nova pasta será criada.
    
    Retorna:
        str: ID da pasta criada ou existente.
    """
    service = authenticate_google_drive()

    # Verifica se a pasta já existe
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])

    if files:
        folder_id = files[0]['id']
        print(f"Pasta '{folder_name}' já existe no Google Drive. ID: {folder_id}")
    else:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder['id']
        print(f"Pasta '{folder_name}' criada com sucesso. ID: {folder_id}")

    return folder_id

def create_drive_structure():
    """
    Cria toda a estrutura de diretórios no Google Drive para o projeto fleet_management.
    """
    # Criando a pasta principal
    fleet_management_folder_id = create_drive_folder("Fleet Management")

    # Criando subpastas dentro de Fleet Management
    images_folder_id = create_drive_folder("Imagens Veículos", fleet_management_folder_id)
    checklists_folder_id = create_drive_folder("Checklists", fleet_management_folder_id)
    invoices_folder_id = create_drive_folder("Notas Fiscais", fleet_management_folder_id)
    reports_folder_id = create_drive_folder("Relatórios", fleet_management_folder_id)

    print("\nEstrutura de diretórios no Google Drive criada com sucesso!")

    return {
        "fleet_management": fleet_management_folder_id,
        "images_veiculos": images_folder_id,
        "checklists": checklists_folder_id,
        "invoices": invoices_folder_id,
        "reports": reports_folder_id
    }

def create_vehicle_folder(license_plate, parent_folder_id):
    """
    Cria uma pasta para um veículo no Google Drive.

    Parâmetros:
        license_plate (str): Placa do veículo.
        parent_folder_id (str): ID da pasta 'Imagens Veículos' onde a nova pasta será criada.
    
    Retorna:
        str: ID da pasta criada.
    """
    return create_drive_folder(license_plate, parent_folder_id)

def register_vehicle(license_plate):
    """
    Função chamada sempre que um novo veículo for cadastrado no sistema.
    Ela cria automaticamente uma pasta no Google Drive para armazenar as imagens do veículo.

    Parâmetros:
        license_plate (str): Placa do veículo.
    """
    # Obtém o ID da pasta "Imagens Veículos"
    drive_folders = create_drive_structure()
    images_folder_id = drive_folders["images_veiculos"]

    # Criando pasta do veículo
    vehicle_folder_id = create_vehicle_folder(license_plate, images_folder_id)

    # Aqui, você pode salvar o vehicle_folder_id no banco de dados
    print(f"Pasta para o veículo {license_plate} foi criada com sucesso no Google Drive. ID: {vehicle_folder_id}")

    return vehicle_folder_id

if __name__ == "__main__":
    # Criando a estrutura principal
    create_drive_structure()

    # Testando o cadastro de um veículo (Exemplo)
    register_vehicle("XYZ5678")

    print("\nEstrutura de diretórios no Google Drive criada com sucesso!")