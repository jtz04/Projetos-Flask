"""
Blueprint de autenticação (auth).
Responsável por:
- Login de usuários
- Logout de usuários  
- Registro de logs de acesso/autenticação
- Detecção de tentativas suspeitas (senhas incorretas, etc)
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from extensions import db
from models import User, AccessLog

# Criação do blueprint
auth_bp = Blueprint('auth', __name__)


def log_access(user_id, device_id, action, status, ip_address, user_agent, details="", is_suspicious=False):
    """
    Função utilitária para registrar acessos no banco de dados.
    Cria um log de acesso e um alerta se for suspeito.
    
    Args:
        user_id: ID do usuário que acessou
        device_id: ID do dispositivo acessado (pode ser None para login no sistema)
        action: Tipo de ação ('system_login', 'device_access', 'failed_login', etc)
        status: Resultado da ação ('success' ou 'failed')
        ip_address: IP do cliente que acessou
        user_agent: Info do navegador/cliente
        details: Descrição adicional opcional
        is_suspicious: Se True, cria um alerta de segurança
    
    Returns:
        AccessLog: Objeto de log criado
    """
    from models import AccessLog, Alert, AlertLevel
    
    # Criar e adicionar log
    log = AccessLog(
        user_id=user_id,
        device_id=device_id,
        action=action,
        status=status,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
        is_suspicious=is_suspicious
    )
    db.session.add(log)
    
    # Se suspeito, criar alerta automático
    if is_suspicious:
        alert = Alert(
            title=f"Acesso suspeito detectado - Usuário: {user_id}",
            description=f"Tentativa de acesso suspeito. Detalhes: {details}",
            alert_level=AlertLevel.HIGH,
            log_id=log.id
        )
        db.session.add(alert)
    
    db.session.commit()
    return log


# ========== ROTA: LOGIN ==========

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota de login de usuários.
    GET: Exibe formulário de login
    POST: Processa credenciais
    """
    if request.method == 'POST':
        # Obter credenciais do formulário
        username = request.form['username']
        password = request.form['password']
        
        # Buscar usuário no banco
        user = User.query.filter_by(username=username).first()
        
        # Verificar se usuário existe, senha está correta e conta está ativa
        if user and check_password_hash(user.password_hash, password) and user.is_active:
            # Login bem-sucedido
            login_user(user)  # Flask-Login cria a sessão
            
            # Registrar log de acesso bem-sucedido
            log_access(
                user_id=user.id,
                device_id=None,
                action='system_login',
                status='success',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # Login falhou - tentar registrar com usuário se encontrado
            if user:
                log_access(
                    user_id=user.id,
                    device_id=None,
                    action='failed_login',
                    status='failed',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    details='Tentativa de login com senha incorreta',
                    is_suspicious=True  # Marca como suspeito -> gera alerta
                )
            flash('Usuário ou senha inválidos!', 'error')
    
    return render_template('login.html')


# ========== ROTA: LOGOUT ==========

@auth_bp.route('/logout')
@login_required  # Requer que usuário esteja logado
def logout():
    """
    Rota de logout de usuários.
    Encerra sessão e registra no log.
    """
    # Registrar log de saída
    log_access(
        user_id=current_user.id,
        device_id=None,
        action='system_logout',
        status='success',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    logout_user()  # Flask-Login destroi a sessão
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('auth.login'))