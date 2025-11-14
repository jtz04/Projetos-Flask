"""
Blueprint de visualização de logs (logs).
Responsável por:
- Visualizar logs de acesso aos dispositivos
- Filtrar logs por usuário, dispositivo, data e suspeita
- Exibir estatísticas de logs (admin only)
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import AccessLog, UserRole
from datetime import datetime, timedelta

# Criação do blueprint
logs_bp = Blueprint('logs', __name__)


# ========== ROTA: VISUALIZAR LOGS ==========

@logs_bp.route('/logs')
@login_required
def logs():
    """
    Exibe logs de acesso com suporte a filtros:
    - user_id: Filtrar por usuário (admin only)
    - device_id: Filtrar por dispositivo
    - date_from: Data inicial (formato: YYYY-MM-DD)
    - date_to: Data final (formato: YYYY-MM-DD)
    - suspicious: Mostrar apenas acessos suspeitos (True/False)
    
    Usuários comuns veem apenas seus próprios logs.
    Administradores veem todos os logs.
    """
    # ========== OBTER PARÂMETROS DE FILTRO ==========
    user_filter = request.args.get('user_id', type=int)
    device_filter = request.args.get('device_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    suspicious_only = request.args.get('suspicious', type=bool)
    
    # Começar com query base
    query = AccessLog.query
    
    # Se não é admin, mostrar apenas seus próprios logs
    if current_user.role != UserRole.ADMIN:
        query = query.filter_by(user_id=current_user.id)
    
    # Filtro por usuário (apenas se admin solicitou)
    if user_filter and current_user.role == UserRole.ADMIN:
        query = query.filter_by(user_id=user_filter)
    
    # Filtro por dispositivo
    if device_filter:
        query = query.filter_by(device_id=device_filter)
    
    # Filtro por data inicial
    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(AccessLog.access_time >= date_from)
    
    # Filtro por data final
    if date_to:
        # Adiciona 1 dia para incluir todas as horas do último dia
        date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(AccessLog.access_time <= date_to)
    
    # Filtro para acessos suspeitos
    if suspicious_only:
        query = query.filter_by(is_suspicious=True)
    
    # Obter resultados ordenados pelos mais recentes
    logs_list = query.order_by(AccessLog.access_time.desc()).all()
    
    return render_template('logs.html', logs=logs_list)


# ========== ROTA: ESTATÍSTICAS DE LOGS ==========

@logs_bp.route('/logs/stats')
@login_required
def logs_stats():
    """
    Retorna estatísticas de logs em formato JSON.
    Apenas administradores podem acessar.
    
    Retorna:
    - total_logs: Total de logs no sistema
    - suspicious_logs: Logs marcados como suspeitos
    - failed_logins: Tentativas de login falhadas
    - recent_logs_24h: Logs das últimas 24 horas
    """
    # Verificar se é administrador
    if current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # ========== CALCULAR ESTATÍSTICAS ==========
    
    # Total de logs
    total_logs = AccessLog.query.count()
    
    # Logs suspeitos
    suspicious_logs = AccessLog.query.filter_by(is_suspicious=True).count()
    
    # Tentativas de login falhadas
    failed_logins = AccessLog.query.filter_by(action='failed_login', status='failed').count()
    
    # Logs das últimas 24 horas
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_logs = AccessLog.query.filter(AccessLog.access_time >= last_24h).count()
    
    # Retornar como JSON
    return jsonify({
        'total_logs': total_logs,
        'suspicious_logs': suspicious_logs,
        'failed_logins': failed_logins,
        'recent_logs_24h': recent_logs
    })