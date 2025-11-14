"""
Arquivo de configurações da aplicação Flask.
Define configurações para diferentes ambientes:
- Development: Debug ativo, ambiente de desenvolvimento
- Production: Debug desativo, com HTTPS, produção
- Testing: Configuração para testes unitários
"""

import os
from datetime import timedelta


class Config:
    """
    Configurações base comuns a todos os ambientes.
    """
    # Chave secreta para sessões e tokens (alterada em produção via variável de ambiente)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-super-segura-aqui'
    
    # URI do banco de dados (SQLite por padrão)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sistema_logs.db'
    
    # Desativa aviso de modificações de modelos (melhora performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ========== CONFIGURAÇÕES DE SESSÃO ==========
    # Tempo de expiração da sessão: 2 horas
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # ========== CONFIGURAÇÕES DE SEGURANÇA ==========
    # SESSION_COOKIE_SECURE: True apenas com HTTPS (produção)
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    
    # HttpOnly: Cookie não acessível via JavaScript (proteção contra XSS)
    SESSION_COOKIE_HTTPONLY = True
    
    # SameSite: Proteção contra CSRF ('Lax' ou 'Strict')
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """
    Configuração para desenvolvimento local.
    """
    DEBUG = True  # Modo debug ativo (auto-reload, erros detalhados)
    TESTING = False


class ProductionConfig(Config):
    """
    Configuração para ambiente de produção.
    """
    DEBUG = False  # Modo debug desativo
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Requer HTTPS


class TestingConfig(Config):
    """
    Configuração para testes unitários.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'  # Banco separado para testes


# Dicionário mapeando nomes de configurações para classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig  # Configuração padrão
}