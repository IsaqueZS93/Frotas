import os
import sys

# Diretório raiz do projeto
base_path = os.path.dirname(os.path.abspath(__file__))

# Percorre todos os diretórios e subdiretórios e adiciona ao sys.path
for root, dirs, files in os.walk(base_path):
    if root not in sys.path:
        sys.path.append(root)
