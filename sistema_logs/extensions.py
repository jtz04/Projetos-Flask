"""
Arquivo de extensões Flask.
Define instâncias de extensões que são inicializadas depois em app.py.
Isso evita problemas de importação circular (circular imports).

Extensões incluídas:
- SQLAlchemy: ORM para gerenciar banco de dados
- LoginManager: Autenticação e gerenciamento de sessão
- Migrate: Controle de versão do banco (Alembic)
"""

from flask_sqlalchemy import SQLAlchemy  # ORM para banco de dados
from flask_login import LoginManager      # Gerenciador de autenticação
from flask_migrate import Migrate         # Migrations do banco de dados

# Instância do SQLAlchemy (ORM)
db = SQLAlchemy()

# Gerenciador de login (autenticação e sessões)
login_manager = LoginManager()

# Sistema de migrations/versionamento do banco
migrate = Migrate()