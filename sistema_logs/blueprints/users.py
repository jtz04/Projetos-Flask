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
from werkzeug.security import check_password_hash

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


# ========== ROTA: EDITAR USUÁRIO ==========

@users_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """
    GET: Exibe formulário para editar usuário existente
    POST: Atualiza os dados do usuário (username, email, senha, role)
    """
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = True if request.form.get('is_admin') else False

        # Verificações de unicidade (exceto ele mesmo)
        other = User.query.filter(User.username == username, User.id != user.id).first()
        if other:
            flash('Nome de usuário já está em uso por outro usuário.', 'error')
            return redirect(url_for('users.edit_user', user_id=user.id))

        other_email = User.query.filter(User.email == email, User.id != user.id).first()
        if other_email:
            flash('Email já está em uso por outro usuário.', 'error')
            return redirect(url_for('users.edit_user', user_id=user.id))

        # Atualizar campos
        user.username = username
        user.email = email
        user.role = UserRole.ADMIN if is_admin else UserRole.USER

        # Atualizar senha somente se fornecida
        if password:
            user.password_hash = generate_password_hash(password)

        try:
            db.session.commit()
            flash('Usuário atualizado com sucesso.', 'success')
        except Exception:
            db.session.rollback()
            flash('Erro ao atualizar usuário.', 'error')

        return redirect(url_for('users.users'))

    # GET -> renderizar formulário com dados existentes
    return render_template('add_user.html', user=user)


# ========== ROTA: DELETAR USUÁRIO ==========

@users_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Deleta um usuário. Requer confirmação no formulário cliente.
    - Não permite que o admin delete a si mesmo
    - Não permite remover o último administrador
    """
    user = User.query.get_or_404(user_id)

    # Não permitir deletar a si mesmo
    if user.id == current_user.id:
        flash('Você não pode deletar seu próprio usuário.', 'error')
        return redirect(url_for('users.users'))

    # Se for admin, garantir que existam outros admins
    if user.role == UserRole.ADMIN:
        admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
        if admin_count <= 1:
            flash('Não é possível deletar o último administrador.', 'error')
            return redirect(url_for('users.users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('Usuário deletado com sucesso.', 'success')
    except Exception:
        db.session.rollback()
        flash('Erro ao deletar usuário.', 'error')

    return redirect(url_for('users.users'))


# ========== ROTA: GERENCIAR PERMISSÕES DO USUÁRIO ==========

@users_bp.route('/users/<int:user_id>/permissions', methods=['GET', 'POST'])
@login_required
@admin_required
def user_permissions(user_id):
    """
    GET: Exibe e permite gerenciar as permissões de um usuário em relação aos dispositivos.
    POST: Atualiza as permissões (read/write/execute) conforme os checkboxes enviados.
    """
    # Buscar usuário
    user = User.query.get_or_404(user_id)

    # Obter todos os dispositivos disponíveis
    devices = Device.query.all()

    if request.method == 'POST':
        # Processar cada dispositivo
        try:
            for d in devices:
                    # Agora há apenas um checkbox por dispositivo: acesso permitido ou não
                    allowed = bool(request.form.get(f'perm_{d.id}'))

                    perm = UserPermission.query.filter_by(user_id=user.id, device_id=d.id).first()
                    if allowed:
                        # criar/atualizar permissão: definir can_read=True, demais False (modelo mantém campos)
                        if perm:
                            perm.can_read = True
                            perm.can_write = False
                            perm.can_execute = False
                        else:
                            perm = UserPermission(
                                user_id=user.id,
                                device_id=d.id,
                                can_read=True,
                                can_write=False,
                                can_execute=False,
                                granted_by=current_user.id
                            )
                            db.session.add(perm)
                    else:
                        # remover permissão se existir
                        if perm:
                            db.session.delete(perm)

            db.session.commit()
            flash('Permissões atualizadas com sucesso.', 'success')
        except Exception:
            db.session.rollback()
            flash('Erro ao atualizar permissões.', 'error')

        return redirect(url_for('users.user_permissions', user_id=user.id))

    # GET: carregar permissões atuais
    user_permissions = {p.device_id: p for p in UserPermission.query.filter_by(user_id=user_id).all()}

    return render_template('user_permissions.html', 
                         user=user, 
                         devices=devices, 
                         user_permissions=user_permissions)