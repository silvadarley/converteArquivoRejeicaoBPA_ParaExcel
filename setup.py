from setuptools import setup, find_packages
import os

# Ler o conteúdo do requirements.txt se existir
def read_requirements():
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="ProcessadorTXT-SUS",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'pandas>=1.3.0',
        'openpyxl>=3.0.0',
        'tkinter>=0.0.0'  # Geralmente já vem com Python
    ],
    entry_points={
        'console_scripts': [
            'processador-sus=ConverteProducaoRejeitada:main',
        ],
    },
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    description="Aplicativo para processar arquivos TXT do SUS e converter para Excel",
    long_description=open('README.md', 'r').read() if os.path.exists('README.md') else "",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Utilities"
    ],
    python_requires='>=3.6',
    keywords='sus, health, data processing, excel, txt',
    #https://github.com/silvadarley/converteArquivoRejeicaoBPA_ParaExcel.git
    project_urls={
        'Source': 'https://github.com/seuusuario/processador-sus',
    },
)