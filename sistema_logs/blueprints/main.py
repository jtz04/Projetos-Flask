"""
Blueprint principal (main).
Responsável por:
- Página inicial/dashboard
- Exibição de estatísticas gerais
- Resumo de logs e alertas recentes
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User, Device, AccessLog, Alert, UserRole

# Criação do blueprint
main_bp = Blueprint('main', __name__)


# ========== ROTA: DASHBOARD ==========

@main_bp.route('/')
@login_required  # Requer autenticação
def dashboard():
    """
    Página de dashboard principal.
    Exibe:
    - Total de usuários
    - Total de dispositivos
    - Últimos 10 acessos registrados
    - Número de alertas não resolvidos
    """
    # Contar total de usuários e dispositivos
    total_users = User.query.count()
    total_devices = Device.query.count()
    
    # Pegar últimos 10 acessos (ordenados por data mais recente)
    recent_logs = AccessLog.query.order_by(AccessLog.access_time.desc()).limit(10).all()
    
    # Contar alertas não resolvidos
    active_alerts = Alert.query.filter_by(is_resolved=False).count()
    
    return render_template('dashboard.html',
                         total_users=total_users,
                         total_devices=total_devices,
                         recent_logs=recent_logs,
                         active_alerts=active_alerts)