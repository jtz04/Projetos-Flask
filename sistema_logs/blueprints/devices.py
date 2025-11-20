"""
Blueprint de gerenciamento de dispositivos (devices).
Responsável por:
- Listar dispositivos
- Controlar acesso aos dispositivos (verificar permissões)
- Registrar acessos aos dispositivos nos logs
- Criar alertas para acessos não autorizados
- Adicionar novos dispositivos (admin only)
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Device, UserPermission, AccessLog, Alert, AlertLevel, UserRole, DeviceType, User
from blueprints.auth import log_access

# Criação do blueprint
devices_bp = Blueprint('devices', __name__)


# ========== FUNÇÃO AUXILIAR: VERIFICAR PERMISSÃO ==========

def has_permission(user_id, device_id):
    """
    Verifica se um usuário tem permissão para acessar um dispositivo.
    Administradores sempre têm permissão.
    
    Args:
        user_id: ID do usuário
        device_id: ID do dispositivo
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    # Usuários admin sempre têm permissão
    if current_user.role == UserRole.ADMIN:
        return True
    
    # Verificar se existe um registro de permissão
    permission = UserPermission.query.filter_by(
        user_id=user_id, 
        device_id=device_id
    ).first()
    return permission is not None


# ========== ROTA: LISTAR DISPOSITIVOS ==========

@devices_bp.route('/devices')
@login_required
def devices():
    """
    Exibe lista de dispositivos disponíveis.
    Marca quais dispositivos o usuário tem acesso.
    """
    # Obter todos os dispositivos
    devices_list = Device.query.all()
    
    # Para usuários não-admin, obter apenas dispositivos que tem permissão
    user_permissions = UserPermission.query.filter_by(user_id=current_user.id).all()
    permitted_devices = [perm.device_id for perm in user_permissions]
    
    return render_template('devices.html', 
                         devices=devices_list, 
                         permitted_devices=permitted_devices,
                         DeviceType=DeviceType)


# ========== ROTA: ACESSAR DISPOSITIVO ==========

@devices_bp.route('/devices/access/<int:device_id>')
@login_required
def access_device(device_id):
    """
    Controla o acesso a um dispositivo específico.
    - Verifica permissões
    - Registra o acesso no log
    - Cria alerta se acesso não autorizado
    """
    device = Device.query.get_or_404(device_id)
    
    # Verificar se usuário tem permissão
    if not has_permission(current_user.id, device_id):
        # Acesso negado - registrar como suspeito
        log_access(
            user_id=current_user.id,
            device_id=device_id,
            action='unauthorized_access_attempt',
            status='failed',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f'Tentativa de acesso não autorizada ao dispositivo {device.name}',
            is_suspicious=True  # Gera alerta automático
        )
        
        flash('Acesso negado! Você não tem permissão para este dispositivo.', 'error')
        return redirect(url_for('devices.devices'))
    
    # Acesso autorizado - registrar no log
    access_log = log_access(
        user_id=current_user.id,
        device_id=device_id,
        action='device_access',
        status='success',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=f'Acesso autorizado ao dispositivo {device.name}'
    )

    # Passa o log recém-criado para o template para exibir detalhes do acesso
    return render_template('device_access.html', device=device, access_log=access_log)


# ========== ROTA: ADICIONAR DISPOSITIVO ==========

@devices_bp.route('/devices/add', methods=['GET', 'POST'])
@login_required
def add_device():
    """
    GET: Formulário para adicionar novo dispositivo
    POST: Processa criação do novo dispositivo
    Apenas administradores podem criar dispositivos.
    """
    # Verificar se é admin (usando o decorator do blueprint users)
    if current_user.role != UserRole.ADMIN:
        flash('Acesso negado! Apenas administradores.', 'error')
        return redirect(url_for('devices.devices'))
    
    if request.method == 'POST':
        # Deleção (botão deletar no modo edição)
        if 'delete_device_id' in request.form:
            try:
                did = int(request.form['delete_device_id'])
                dev = Device.query.get(did)
                if dev:
                    # Remove permissões relacionadas automaticamente por cascade
                    db.session.delete(dev)
                    db.session.commit()
                    flash('Dispositivo deletado com sucesso.', 'success')
                else:
                    flash('Dispositivo não encontrado.', 'error')
            except Exception:
                db.session.rollback()
                flash('Erro ao deletar dispositivo.', 'error')
            return redirect(url_for('devices.devices'))

        # Obter dados do formulário para criar/atualizar
        device_id = request.form.get('device_id')
        name = request.form.get('name')
        ip_address = request.form.get('ip_address')
        device_type_value = request.form.get('device_type')
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        is_active = bool(request.form.get('is_active'))

        # Converter tipo
        try:
            device_type = DeviceType(device_type_value)
        except Exception:
            flash('Tipo de dispositivo inválido.', 'error')
            return redirect(url_for('devices.add_device'))

        # Criar ou atualizar
        if device_id:
            device = Device.query.get(device_id)
            if not device:
                flash('Dispositivo não encontrado.', 'error')
                return redirect(url_for('devices.devices'))
            device.name = name
            device.ip_address = ip_address
            device.device_type = device_type
            device.description = description
            device.location = location
            device.is_active = is_active
        else:
            device = Device(
                name=name,
                ip_address=ip_address,
                device_type=device_type,
                description=description,
                location=location,
                is_active=is_active,
            )
            db.session.add(device)
        
        # Garantir flush para obter device.id antes de criar permissões
        try:
            db.session.flush()
        except Exception:
            db.session.rollback()
            flash('Erro ao salvar dispositivo.', 'error')
            return redirect(url_for('devices.devices'))

        # Processar permissões por usuário (se o template enviou)
        users_all = User.query.all()
        for u in users_all:
            can_read = bool(request.form.get(f'perm_{u.id}_read'))
            can_write = bool(request.form.get(f'perm_{u.id}_write'))
            can_execute = bool(request.form.get(f'perm_{u.id}_execute'))

            perm = UserPermission.query.filter_by(user_id=u.id, device_id=device.id).first()
            if can_read or can_write or can_execute:
                if perm:
                    perm.can_read = can_read
                    perm.can_write = can_write
                    perm.can_execute = can_execute
                else:
                    perm = UserPermission(
                        user_id=u.id,
                        device_id=device.id,
                        can_read=can_read,
                        can_write=can_write,
                        can_execute=can_execute,
                        granted_by=current_user.id
                    )
                    db.session.add(perm)
            else:
                # se não marcou nenhuma perm, remover registro existente
                if perm:
                    db.session.delete(perm)

        # Commit final
        try:
            db.session.commit()
            flash('Dispositivo salvo com sucesso!', 'success')
        except Exception:
            db.session.rollback()
            flash('Erro ao salvar dispositivo/permissões.', 'error')

        return redirect(url_for('devices.devices'))

    # GET: se for edição, carregar dados
    device = None
    device_permitted_users = {}
    users = None
    device_id = request.args.get('id') or request.args.get('device_id')
    if device_id:
        device = Device.query.get(device_id)
        if device:
            users = User.query.all()
            perms = UserPermission.query.filter_by(device_id=device.id).all()
            device_permitted_users = {p.user_id: p for p in perms}

    # Passar lista de usuários e mapa de permissões para o template (opcional)
    return render_template('add_device.html', device_types=DeviceType, device=device, users=users, device_permitted_users=device_permitted_users)