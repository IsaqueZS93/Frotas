"""
utils/image_utils.py

Este módulo contém funções utilitárias para manipulação de imagens no sistema.

Funcionalidades:
- Validação do formato e tamanho de imagens.
- Redimensionamento e compressão de imagens antes do upload.
- Conversão de imagens para formatos padronizados.
"""

import os
import io
from PIL import Image

# Configuração de tamanho máximo da imagem (em bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
VALID_IMAGE_FORMATS = ["JPEG", "PNG", "JPG"]


def validate_image(imagem):
    """
    Valida se a imagem enviada atende aos requisitos de formato e tamanho.

    Parâmetros:
        imagem (UploadedFile): Arquivo de imagem enviado pelo usuário.

    Retorna:
        bool: True se a imagem for válida, False caso contrário.
    """
    if not imagem:
        return False

    try:
        img = Image.open(imagem)
        formato = img.format.upper()

        if formato not in VALID_IMAGE_FORMATS:
            return False  # Formato inválido

        if imagem.size > MAX_IMAGE_SIZE:
            return False  # Tamanho acima do permitido

        return True

    except Exception as e:
        print(f"Erro ao validar imagem: {e}")
        return False

def validar_imagem(imagem):
    """
    Valida se o arquivo enviado é uma imagem válida.

    Parâmetros:
        imagem (bytes): Arquivo de imagem carregado.

    Retorna:
        bool: True se for uma imagem válida, False caso contrário.
    """
    try:
        img = Image.open(imagem)
        img.verify()
        return True
    except Exception:
        return False

def redimensionar_imagem(imagem, tamanho=(800, 600)):
    """
    Redimensiona uma imagem para o tamanho especificado.

    Parâmetros:
        imagem (bytes): Arquivo de imagem carregado.
        tamanho (tuple): Dimensão desejada (largura, altura).

    Retorna:
        bytes: Imagem redimensionada em formato de bytes.
    """
    try:
        img = Image.open(imagem)
        img = img.resize(tamanho, Image.ANTIALIAS)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        return img_bytes.getvalue()
    except Exception as e:
        print(f"Erro ao redimensionar imagem: {e}")
        return None

def redimensionar_comprimir_imagem(imagem, qualidade=80):
    """
    Redimensiona e comprime uma imagem para otimizar o espaço de armazenamento.

    Parâmetros:
        imagem (UploadedFile): Arquivo de imagem enviado pelo usuário.
        qualidade (int): Qualidade da compressão (padrão: 80).

    Retorna:
        bytes: Imagem otimizada em formato binário.
    """
    try:
        img = Image.open(imagem)
        img = img.convert("RGB")  # Garante compatibilidade com JPEG

        # Redimensionamento se a imagem for muito grande
        max_dimensao = 1024  # Máximo de 1024px no maior lado
        width, height = img.size
        if width > max_dimensao or height > max_dimensao:
            img.thumbnail((max_dimensao, max_dimensao))

        # Compressão e conversão para JPEG
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG", quality=qualidade)
        img_bytes.seek(0)

        return img_bytes

    except Exception as e:
        print(f"Erro ao redimensionar/comprimir imagem: {e}")
        return None


def salvar_imagem_temporaria(imagem):
    """
    Salva a imagem temporariamente no servidor antes do upload para o Google Drive.

    Parâmetros:
        imagem (UploadedFile): Arquivo de imagem enviado pelo usuário.

    Retorna:
        str: Caminho do arquivo salvo temporariamente.
    """
    try:
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)

        caminho_temp = os.path.join(temp_dir, imagem.name)
        with open(caminho_temp, "wb") as f:
            f.write(imagem.getbuffer())

        return caminho_temp

    except Exception as e:
        print(f"Erro ao salvar imagem temporária: {e}")
        return None
