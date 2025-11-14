"""
Script para resetar banco de dados e recriar tabelas
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models import User, UserRole
from werkzeug.security import generate_password_hash

# Remove banco antigo
db_path = 'instance/app.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✓ Banco de dados antigo deletado: {db_path}")

# Criar app e contexto
app = create_app()

with app.app_context():
    # Criar todas tabelas
    db.create_all()
    print("✓ Tabelas criadas com sucesso")
    
    # Criar usuário admin
    admin = User(
        username='admin',
        email='admin@sistema.com',
        password_hash=generate_password_hash('admin123'),
        role=UserRole.ADMIN
    )
    db.session.add(admin)
    db.session.commit()
    print("✓ Usuário admin criado (admin / admin123)")
    
print("\n✓ Banco de dados resetado com sucesso!")
