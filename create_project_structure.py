"""
create_project_structure.py

Este script cria toda a estrutura de diretórios necessária para o projeto fleet_management.
A estrutura definida é a seguinte:

fleet_management/
├── app.py                      
├── config.py                   
├── requirements.txt            
├── README.md                   
├── database/
│   ├── __init__.py             
│   ├── connection.py           
│   └── models/
│       ├── __init__.py         
│       ├── models_usuarios.py  
│       ├── models_veiculos.py  
│       ├── models_abastecimentos.py  
│       └── models_checklists.py      
├── pages/
│   ├── login.py                
│   ├── dashboard/
│   │   ├── __init__.py         
│   │   ├── dashboard_main.py   
│   │   ├── dashboard_charts.py 
│   │   └── dashboard_alerts.py 
│   ├── crud_usuarios.py        
│   ├── crud_veiculos.py        
│   ├── crud_abastecimentos.py  
│   ├── checklist_inicio.py     
│   ├── checklist_final.py      
│   └── reports.py              
├── services/
│   ├── __init__.py
│   ├── auth_service.py         
│   ├── email_service.py        
│   └── google_drive_service.py 
├── utils/
│   ├── __init__.py
│   ├── image_utils.py          
│   ├── km_calculations.py      
│   └── helpers.py              
└── static/
    ├── css/                    
    └── images/                 
└── uploads/  (para armazenamento local de arquivos, se necessário)
"""

import os

def create_directories():
    """
    Cria a estrutura de diretórios necessária para o projeto fleet_management.
    Se o diretório já existir, ele não será recriado.
    """
    directories = [
        "database",
        "database/models",
        "pages",
        "pages/dashboard",
        "services",
        "utils",
        "static",
        "static/css",
        "static/images",
        "uploads"
    ]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Diretório criado ou já existente: {directory}")
        except Exception as e:
            print(f"Erro ao criar o diretório {directory}: {e}")

if __name__ == "__main__":
    create_directories()
