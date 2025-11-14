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
from models import Device, UserPermission, AccessLog, Alert, AlertLevel, UserRole, DeviceType
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
    log_access(
        user_id=current_user.id,
        device_id=device_id,
        action='device_access',
        status='success',
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=f'Acesso autorizado ao dispositivo {device.name}'
    )
    
    return render_template('device_access.html', device=device)


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
        # Obter dados do formulário
        name = request.form['name']
        ip_address = request.form['ip_address']
        device_type = DeviceType(request.form['device_type'])
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        
        # Criar novo dispositivo
        new_device = Device(
            name=name,
            ip_address=ip_address,
            device_type=device_type,
            description=description,
            location=location
        )
        
        db.session.add(new_device)
        db.session.commit()
        
        flash('Dispositivo adicionado com sucesso!', 'success')
        return redirect(url_for('devices.devices'))
    
    return render_template('add_device.html', device_types=DeviceType)