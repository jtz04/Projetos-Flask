"""
Arquivo principal da aplicação Flask.
Responsável por:
- Criar e configurar a instância Flask
- Inicializar extensões (banco de dados, autenticação, migrations)
- Registrar blueprints (rotas modulares)
- Criar banco de dados e usuário admin padrão
- Configurar tratadores de erro
"""

from flask import Flask, render_template
from config import config
from extensions import db, login_manager, migrate
from models import User, UserRole
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.users import users_bp
from blueprints.devices import devices_bp
from blueprints.logs import logs_bp
from blueprints.alerts import alerts_bp
from werkzeug.security import generate_password_hash


def create_app(config_name='default'):
    """
    Função factory para criar a aplicação Flask.
    
    Args:
        config_name (str): Nome da configuração ('development', 'production', etc)
    
    Returns:
        Flask: Instância da aplicação configurada
    """
    app = Flask(__name__)
    
    # Carregar configurações do arquivo config.py baseado no ambiente
    app.config.from_object(config[config_name])
    
    # ========== INICIALIZAR EXTENSÕES ==========
    # SQLAlchemy: ORM para banco de dados
    # LoginManager: Gerenciador de autenticação/sessão
    # Migrate: Controle de versão do banco (alembic)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # ========== CONFIGURAR LOGIN MANAGER ==========
    # Define a rota de login, mensagens de autenticação e carregamento de usuário
    login_manager.login_view = 'auth.login'  # Rota para redirecionar usuários não autenticados
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Função de callback para carregar usuário por ID (usado em sessões)
    @login_manager.user_loader
    def load_user(user_id):
        """Busca usuário pelo ID na sessão"""
        return User.query.get(int(user_id))
    
    # ========== REGISTRAR BLUEPRINTS ==========
    # Blueprints são módulos reutilizáveis com rotas e funções
    # auth: Autenticação (login/logout)
    # main: Dashboard principal
    # users: Gerenciamento de usuários (admin only)
    # devices: Gerenciamento de dispositivos
    # logs: Visualização e análise de logs de acesso
    # alerts: Gerenciamento de alertas de segurança
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp, url_prefix='/admin')  # Rotas prefixadas com /admin
    app.register_blueprint(devices_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(alerts_bp)
    
    # ========== CRIAR BANCO DE DADOS E USUÁRIO ADMIN ==========
    # Executa dentro do contexto da aplicação para acessar o banco
    with app.app_context():
        # Cria todas as tabelas definidas em models.py
        db.create_all()
    
    # ========== TRATADORES DE ERRO ==========
    # Retorna páginas customizadas para erros HTTP
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Erro 404: Página não encontrada"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Erro 500: Erro interno do servidor (reverte transações pendentes)"""
        db.session.rollback()
        return render_template('500.html'), 500
    
    return app


if __name__ == '__main__':
    # Executa a aplicação em modo debug quando rodado diretamente
    app = create_app()
    app.run(debug=True)