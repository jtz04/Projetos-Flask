"""
Arquivo de modelos de dados (ORM).
Define a estrutura das tabelas do banco de dados usando SQLAlchemy.

Modelos inclusos:
- User: Usuários do sistema
- Device: Dispositivos a serem monitorados
- UserPermission: Permissões de usuários em dispositivos
- AccessLog: Log de acessos aos dispositivos
- Alert: Alertas de segurança
"""

from extensions import db
from flask_login import UserMixin
from datetime import datetime
import enum


# ========== ENUMS (Valores predefinidos) ==========

class UserRole(enum.Enum):
    """Papéis de usuário no sistema"""
    ADMIN = "admin"      # Administrador (acesso total)
    USER = "user"        # Usuário comum (acesso limitado)


class DeviceType(enum.Enum):
    """Tipos de dispositivos a monitorar"""
    COMPUTER = "computer"  # Computador
    SERVER = "server"      # Servidor
    CAMERA = "camera"      # Câmera de segurança
    SWITCH = "switch"      # Switch de rede
    ROUTER = "router"      # Roteador


class AlertLevel(enum.Enum):
    """Níveis de severidade de alertas"""
    LOW = "low"          # Baixo
    MEDIUM = "medium"    # Médio
    HIGH = "high"        # Alto


# ========== MODELO: USER ==========

class User(UserMixin, db.Model):
    """
    Modelo de usuário do sistema.
    Herda de UserMixin para compatibilidade com Flask-Login.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Usuário ativo ou desativado?
    
    # Relacionamentos (um usuário tem muitas permissões e logs)
    # foreign_keys especifica qual coluna usar como chave estrangeira
    user_permissions = db.relationship('UserPermission', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='UserPermission.user_id')
    permissions_granted = db.relationship('UserPermission', backref='granted_by_user', lazy=True, foreign_keys='UserPermission.granted_by')
    logs = db.relationship('AccessLog', backref='user', lazy=True, cascade='all, delete-orphan')


# ========== MODELO: DEVICE ==========

class Device(db.Model):
    """
    Modelo de dispositivo a ser monitorado.
    Pode ser computador, servidor, câmera, etc.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv4 ou IPv6
    device_type = db.Column(db.Enum(DeviceType), nullable=False)
    description = db.Column(db.Text)  # Descrição livre do dispositivo
    location = db.Column(db.String(200))  # Localização física
    is_active = db.Column(db.Boolean, default=True)  # Dispositivo ativo ou inativo?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos (um dispositivo tem muitas permissões e logs)
    user_permissions = db.relationship('UserPermission', backref='device', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('AccessLog', backref='device', lazy=True, cascade='all, delete-orphan')


# ========== MODELO: USER PERMISSION ==========

class UserPermission(db.Model):
    """
    Modelo de permissão: Define o que cada usuário pode fazer em cada dispositivo.
    Implementa controle de acesso baseado em papéis (RBAC).
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=True)  # Opcional para logs de login
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)  # Quando a permissão foi concedida
    granted_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Qual admin concedeu?
    
    # Permissões específicas
    can_read = db.Column(db.Boolean, default=True)    # Pode ler/visualizar?
    can_write = db.Column(db.Boolean, default=False)  # Pode modificar?
    can_execute = db.Column(db.Boolean, default=False)  # Pode executar ações?


# ========== MODELO: ACCESS LOG ==========

class AccessLog(db.Model):
    """
    Modelo de log de acesso.
    Registra todo acesso de usuários aos dispositivos para auditoria e segurança.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=True)  # Opcional para logs de login
    access_time = db.Column(db.DateTime, default=datetime.utcnow)  # Quando aconteceu?
    action = db.Column(db.String(50), nullable=False)  # Qual ação (login, read, write, etc)
    status = db.Column(db.String(20), nullable=False)  # Sucesso ou falha?
    ip_address = db.Column(db.String(45))  # IP do usuário
    user_agent = db.Column(db.Text)  # Browser/cliente usado
    details = db.Column(db.Text)  # Detalhes adicionais
    is_suspicious = db.Column(db.Boolean, default=False)  # Acesso suspeito? (gera alerta)


# ========== MODELO: ALERT ==========

class Alert(db.Model):
    """
    Modelo de alerta de segurança.
    Alertas são criados automaticamente para acessos suspeitos ou erros.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Título do alerta
    description = db.Column(db.Text)  # Descrição detalhada
    alert_level = db.Column(db.Enum(AlertLevel), default=AlertLevel.MEDIUM)  # Severidade
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)  # Quando foi resolvido?
    is_resolved = db.Column(db.Boolean, default=False)  # Alerta já foi tratado?
    
    # Relacionamento com o log que gerou o alerta (pode ser None)
    log_id = db.Column(db.Integer, db.ForeignKey('access_log.id'))
    log = db.relationship('AccessLog', backref='alerts')