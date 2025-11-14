"""
Blueprint de gerenciamento de usuários (users).
Acesso restrito apenas a administradores.
Responsável por:
- Listar todos os usuários
- Criar novos usuários
- Ativar/desativar usuários
- Gerenciar permissões de usuários em dispositivos
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, UserRole, UserPermission, Device

# Criação do blueprint com url_prefix (todas as rotas começam com /admin)
users_bp = Blueprint('users', __name__)


# ========== DECORATOR: ADMIN_REQUIRED ==========

def admin_required(func):
    """
    Decorator que verifica se o usuário é administrador.
    Se não for, redireciona para dashboard com mensagem de erro.
    """
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.role != UserRole.ADMIN:
            flash('Acesso negado! Apenas administradores.', 'error')
            return redirect(url_for('main.dashboard'))
        return func(*args, **kwargs)
    return decorated_view


# ========== ROTA: LISTAR USUÁRIOS ==========

@users_bp.route('/users')
@login_required
@admin_required
def users():
    """
    Exibe lista de todos os usuários cadastrados.
    Apenas administradores podem acessar.
    """
    users_list = User.query.all()
    return render_template('users.html', users=users_list)


# ========== ROTA: ADICIONAR USUÁRIO ==========

@users_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """
    GET: Formulário para adicionar novo usuário
    POST: Processa criação do novo usuário
    """
    if request.method == 'POST':
        # Obter dados do formulário
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # Determina se o novo usuário será admin ou usuário comum
        role = UserRole.ADMIN if request.form.get('is_admin') else UserRole.USER
        
        # Verificar se username já existe
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe!', 'error')
            return redirect(url_for('users.add_user'))
        
        # Criar novo usuário (senha é hasheada por segurança)
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('users.users'))
    
    return render_template('add_user.html')


# ========== ROTA: ATIVAR/DESATIVAR USUÁRIO ==========

@users_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """
    Ativa ou desativa um usuário (alterna is_active).
    Usuários desativados não conseguem fazer login.
    """
    user = User.query.get_or_404(user_id)
    
    # Inverter status ativo/inativo
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "ativado" if user.is_active else "desativado"
    flash(f'Usuário {status} com sucesso!', 'success')
    return redirect(url_for('users.users'))


# ========== ROTA: GERENCIAR PERMISSÕES DO USUÁRIO ==========

@users_bp.route('/users/<int:user_id>/permissions')
@login_required
@admin_required
def user_permissions(user_id):
    """
    Exibe e permite gerenciar as permissões de um usuário em relação aos dispositivos.
    Mostra quais dispositivos o usuário tem acesso e quais permissões (read, write, execute).
    """
    # Buscar usuário
    user = User.query.get_or_404(user_id)
    
    # Obter todos os dispositivos disponíveis
    devices = Device.query.all()
    
    # Obter permissões do usuário
    user_permissions = UserPermission.query.filter_by(user_id=user_id).all()
    
    return render_template('user_permissions.html', 
                         user=user, 
                         devices=devices, 
                         user_permissions=user_permissions)