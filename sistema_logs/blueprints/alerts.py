"""
Blueprint de alertas de segurança (alerts).
Acesso restrito apenas a administradores.
Responsável por:
- Exibir alertas de segurança gerados automaticamente
- Resolver alertas (marcar como tratados)
- Visualizar detalhes de cada alerta
"""

from flask import Blueprint, flash, redirect, render_template, request, jsonify, url_for
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models import Alert, UserRole, AlertLevel

# Criação do blueprint
alerts_bp = Blueprint('alerts', __name__)


# ========== ROTA: LISTAR ALERTAS ==========

@alerts_bp.route('/alerts')
@login_required
def alerts():
    """
    Exibe lista de alertas de segurança.
    Apenas administradores podem ver alertas.
    Permite filtrar por alertas resolvidos/não resolvidos.
    """
    # Verificar se é administrador
    if current_user.role != UserRole.ADMIN:
        flash('Acesso negado! Apenas administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Verificar se deve mostrar alertas já resolvidos (parâmetro GET)
    show_resolved = request.args.get('show_resolved', False, type=bool)
    
    # Construir query
    query = Alert.query
    
    # Se não quer ver resolvidos, filtrar apenas não-resolvidos
    if not show_resolved:
        query = query.filter_by(is_resolved=False)
    
    # Obter alertas ordenados pelos mais recentes
    alerts_list = query.order_by(Alert.created_at.desc()).all()
    
    return render_template('alerts.html', alerts=alerts_list, AlertLevel=AlertLevel)


# ========== ROTA: RESOLVER ALERTA ==========

@alerts_bp.route('/alerts/resolve/<int:alert_id>', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """
    Marca um alerta como resolvido.
    Apenas administradores podem resolver alertas.
    Pode responder com JSON ou redirecionar.
    """
    # Verificar se é administrador
    if current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Buscar alerta
    alert = Alert.query.get_or_404(alert_id)
    
    # Marcar como resolvido
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    
    # Responder com JSON se for requisição AJAX
    if request.is_json:
        return jsonify({'success': True})
    
    # Caso contrário, redirecionar com mensagem
    flash('Alerta marcado como resolvido!', 'success')
    return redirect(url_for('alerts.alerts'))


# ========== ROTA: VER DETALHES DO ALERTA ==========

@alerts_bp.route('/alerts/<int:alert_id>')
@login_required
def alert_details(alert_id):
    """
    Exibe detalhes completos de um alerta específico.
    Mostra informações do alerta e do log de acesso associado (se houver).
    Apenas administradores podem ver detalhes.
    """
    # Verificar se é administrador
    if current_user.role != UserRole.ADMIN:
        flash('Acesso negado!', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Buscar alerta
    alert = Alert.query.get_or_404(alert_id)
    return render_template('alert_details.html', alert=alert)