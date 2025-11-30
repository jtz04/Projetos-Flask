# 📊 Sistema de Logs e Monitoramento de Dispositivos
## Apresentação do Projeto

---

## 📑 Índice
1. [Visão Geral](#visão-geral)
2. [Problema e Solução](#problema-e-solução)
3. [Funcionalidades Principais](#funcionalidades-principais)
4. [Arquitetura do Sistema](#arquitetura-do-sistema)
5. [Modelo de Dados](#modelo-de-dados)
6. [Recursos de Segurança](#recursos-de-segurança)
7. [Fluxo de Uso](#fluxo-de-uso)
8. [Stack Tecnológico](#stack-tecnológico)
9. [Diferenciais](#diferenciais)

---

## 🎯 Visão Geral

### O que é o Sistema?

Um **sistema web moderno de auditoria e monitoramento de dispositivos** que centraliza:
- ✅ **Gestão de usuários** com controle de acesso baseado em papéis (RBAC)
- ✅ **Inventário de dispositivos** (computadores, servidores, câmeras, switches, roteadores)
- ✅ **Rastreamento de acessos** em tempo real com auditoria completa
- ✅ **Detecção de anomalias** com alertas automáticos de segurança

### Objetivo Principal
**Fornecer visibilidade total sobre quem acessa qual dispositivo, quando, de onde e com qual resultado** — tudo em um painel intuitivo.

---

## 🔍 Problema e Solução

### Problemas que o Sistema Resolve

#### ❌ **Problema 1: Falta de Auditoria**
- Ninguém sabe quem acessou qual dispositivo
- Sem registro de tentativas de acesso
- Impossível rastrear atividades suspeitas

**✅ Solução:** Log completo de todas ações com timestamp, IP, navegador e detalhes

#### ❌ **Problema 2: Controle de Acesso Manual**
- Difícil gerenciar quem tem permissão para qual dispositivo
- Sem rastreamento de quem concedeu a permissão
- Acesso desorganizado e propenso a erros

**✅ Solução:** RBAC centralizado — admin configura permissões por usuário/dispositivo

#### ❌ **Problema 3: Sem Alertas de Segurança**
- Tentativas de acesso não autorizado passam despercebidas
- Nenhuma notificação de comportamento anormal
- Resposta lenta a incidentes

**✅ Solução:** Alertas automáticos para acessos suspeitos (HIGH, MEDIUM, LOW)

#### ❌ **Problema 4: Falta de Controle de Usuários**
- Sem bloqueio temporário de usuários comprometidos
- Sem histórico de permissões concedidas
- Sem forma de saber quem é administrador

**✅ Solução:** Gestão completa com roles (ADMIN/USER), ativação/desativação, histórico

---

## ⚙️ Funcionalidades Principais

### 👥 **1. Gerenciamento de Usuários (Admin)**

#### Criar Usuário
```
Admin → Menu Usuários → Novo Usuário
  ├─ Nome de usuário (único)
  ├─ Email (único)
  ├─ Senha segura (hash bcrypt)
  └─ Tipo: ADMIN ou USUÁRIO COMUM
```

#### Editar Usuário
```
Admin → Usuários → Clicar em Lápis
  ├─ Atualizar nome, email, senha
  ├─ Mudar role (ADMIN ↔ USER)
  └─ Salvar alterações
```

#### Deletar Usuário
```
Admin → Usuários → Clicar em Lixeira
  ├─ Confirmação obrigatória
  ├─ Proteção: não deleta último admin
  ├─ Proteção: não deleta a si mesmo
  └─ Deleta automaticamente logs e permissões associadas
```

#### Ativar/Desativar Usuário
```
Admin → Usuários → Toggle Status
  ├─ Bloqueia login temporariamente
  ├─ Mantém histórico intacto
  └─ Pode ser reativado depois
```

---

### 🖥️ **2. Gerenciamento de Dispositivos (Admin)**

#### Criar Dispositivo
```
Admin → Dispositivos → Novo Dispositivo
  ├─ Nome (ex: "Servidor Web")
  ├─ IP/IPv6 (192.168.1.10)
  ├─ Tipo: COMPUTER / SERVER / CAMERA / SWITCH / ROUTER
  ├─ Localização (sala, andar, etc)
  ├─ Descrição
  └─ Status: Ativo ou Inativo
```

#### Editar Dispositivo
```
Admin → Dispositivos → Editar
  ├─ Alterar dados
  ├─ Atribuir permissões direto
  └─ Deletar com confirmação
```

#### Atribuir Permissões
```
Admin → Dispositivo → Aba Permissões
  └─ Marcar: "Acesso Permitido" para cada usuário
     (Simples: permitido ou não — sem granularidade)
```

---

### 🔐 **3. Permissões de Acesso (RBAC)**

#### Fluxo de Permissão
```
Admin define: User "João" → pode acessar "Servidor Web"
                 ↓
         Registrado em USER_PERMISSION
                 ↓
         João agora vê o dispositivo em /devices
                 ↓
         João pode clicar "Acessar"
                 ↓
         Acesso registrado em ACCESS_LOG
```

#### Tipos de Acesso
- ✅ **PERMITIDO**: Usuário tem permissão → acesso bem-sucedido
- ❌ **NEGADO**: Sem permissão → acesso bloqueado + alerta

---

### 📋 **4. Auditoria e Logs**

#### Cada Acesso Registra:
```
┌─ Usuário: Quem tentou acessar?
├─ Dispositivo: Qual dispositivo?
├─ Data/Hora: Quando?
├─ IP: De qual IP?
├─ Navegador (User-Agent): Qual cliente?
├─ Ação: login / device_access / unauthorized_access_attempt / etc
├─ Status: success / failed
├─ Detalhes: Contexto adicional
└─ is_suspicious: Flag de anomalia? (sim/não)
```

#### Visualização de Logs
```
Admin → Menu Logs
  ├─ Tabela com todos os acessos
  ├─ Filtros: usuário, dispositivo, data, suspeito
  ├─ Exportar para CSV
  └─ Estatísticas: total, suspeitos, falhas hoje, etc

Usuário Comum → Menu Logs
  └─ Vê apenas seus próprios logs
```

---

### 🚨 **5. Alertas de Segurança**

#### Quando um Alerta é Criado?
```
ACCESS_LOG com is_suspicious = True
        ↓
      ALERT gerado automaticamente
        ├─ Título: "Acesso não autorizado"
        ├─ Descrição: Contexto do incidente
        ├─ Nível: LOW / MEDIUM / HIGH
        └─ Admin notificado
```

#### Exemplos de Anomalias
- 🔴 **HIGH**: Tentativa de acesso não autorizado a dispositivo crítico
- 🟠 **MEDIUM**: Múltiplas falhas de login do mesmo IP
- 🟡 **LOW**: Acesso de IP incomum (informativo)

#### Ações do Admin
```
Admin → Menu Alertas
  ├─ Lista alertas não resolvidos
  ├─ Filtra por nível
  ├─ Clica em alerta para ver detalhes
  ├─ Visualiza log associado
  └─ Marca como "Resolvido"
```

---

### 📊 **6. Dashboard**

#### Widgets KPI
```
┌─────────────────────────────────────┐
│  Total de Usuários: 12              │
│  Total de Dispositivos: 8           │
│  Alertas Ativos: 3                  │
│  Status da Sessão: admin (online)   │
└─────────────────────────────────────┘
```

#### Últimos Acessos
```
┌────────────────────────────────────────────┐
│ João  → Servidor Web → success  → 14:30    │
│ Maria → Câmera 1     → failed   → 14:25    │ [SUSPEITO]
│ Pedro → Switch        → success → 14:20    │
└────────────────────────────────────────────┘
```

---

## 🏗️ Arquitetura do Sistema

### Padrão: MVC + Blueprints

```
┌────────────────────────────────────────┐
│         FLASK APPLICATION               │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  BLUEPRINTS (Modularização)      │ │
│  │  ├─ auth.py (login/logout)       │ │
│  │  ├─ main.py (dashboard)          │ │
│  │  ├─ users.py (gestão usuários)   │ │
│  │  ├─ devices.py (gestão disposi)  │ │
│  │  ├─ logs.py (auditoria)          │ │
│  │  └─ alerts.py (alertas)          │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  TEMPLATES (Jinja2/Bootstrap)    │ │
│  │  ├─ login.html                   │ │
│  │  ├─ dashboard.html               │ │
│  │  ├─ users.html / add_user.html   │ │
│  │  ├─ devices.html / add_device.html
│  │  ├─ logs.html                    │ │
│  │  └─ alerts.html                  │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  MODELS (SQLAlchemy ORM)         │ │
│  │  ├─ User                         │ │
│  │  ├─ Device                       │ │
│  │  ├─ UserPermission               │ │
│  │  ├─ AccessLog                    │ │
│  │  └─ Alert                        │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  DATABASE (SQLite)               │ │
│  │  └─ instance/app.db              │ │
│  └──────────────────────────────────┘ │
│                                        │
└────────────────────────────────────────┘
```

### Fluxo de uma Requisição

```
1. Usuário acessa /devices
              ↓
2. Blueprint devices.py:devices() é acionado
              ↓
3. Verifica @login_required (Flask-Login)
              ↓
4. Consulta: Device.query.all()
              ↓
5. Consulta: UserPermission.query.filter_by(user_id=current_user.id)
              ↓
6. Renderiza: render_template('devices.html', ...)
              ↓
7. Jinja2 processa e retorna HTML
              ↓
8. Bootstrap CSS + JavaScript carregam
              ↓
9. Página exibida no navegador
```

---

## 📦 Modelo de Dados

### 5 Tabelas Principais

```
┌──────────────┐      ┌──────────────┐
│     USER     │      │    DEVICE    │
├──────────────┤      ├──────────────┤
│ id (PK)      │      │ id (PK)      │
│ username     │      │ name         │
│ email        │      │ ip_address   │
│ password     │      │ device_type  │
│ role         │      │ location     │
│ is_active    │      │ created_at   │
└──────────────┘      └──────────────┘
       │ (1)                │ (1)
       │                    │
       │ (N)                │ (N)
       │                    │
   ┌───┴────────────────────┴───┐
   │                            │
   ▼                            ▼
┌──────────────────────────────────┐
│    USER_PERMISSION               │
├──────────────────────────────────┤
│ id (PK)                          │
│ user_id (FK) → USER              │
│ device_id (FK) → DEVICE          │
│ granted_by (FK) → USER (admin)   │
│ can_read, can_write, can_execute │
│ granted_at                       │
└──────────────────────────────────┘
   │
   │ (1)
   │
   └─────┬──────────────────┬────────────┐
         │                  │            │
         ▼                  ▼            ▼
    ┌──────────────┐  ┌──────────────┐
    │  ACCESS_LOG  │  │    ALERT     │
    ├──────────────┤  ├──────────────┤
    │ id (PK)      │  │ id (PK)      │
    │ user_id (FK) │  │ title        │
    │ device_id    │  │ description  │
    │ action       │  │ alert_level  │
    │ status       │  │ created_at   │
    │ ip_address   │  │ is_resolved  │
    │ is_suspicious├──→ [gerado auto]│
    │ access_time  │  └──────────────┘
    └──────────────┘
```

---

## 🔒 Recursos de Segurança

### 1. **Autenticação**
- ✅ Login com username/password
- ✅ Senha armazenada com hash bcrypt (Werkzeug)
- ✅ Sessão segura com Flask-Login
- ✅ Redirect automático para /login se não autenticado

### 2. **Autorização (RBAC)**
```
ADMIN
  ├─ Acesso total ao sistema
  ├─ Gerenciar usuários (CRUD)
  ├─ Gerenciar dispositivos (CRUD)
  ├─ Gerenciar permissões
  ├─ Visualizar todos os logs
  └─ Visualizar e resolver alertas

USER
  ├─ Visualizar dashboard
  ├─ Acessar dispositivos com permissão
  ├─ Visualizar apenas seus logs
  └─ Sem acesso a gestão
```

### 3. **Proteção de Dados**
- ✅ Senha hasheada (não armazenada em texto plano)
- ✅ Cascade delete: deletar user/device remove dados relacionados
- ✅ Unique constraints: username, email não duplicados
- ✅ NOT NULL constraints: campos críticos obrigatórios

### 4. **Auditoria de Segurança**
- ✅ Log de todas ações de acesso
- ✅ Rastreamento de IP e User-Agent
- ✅ Flag is_suspicious para anomalias
- ✅ Histórico de permissões concedidas (granted_by, granted_at)

### 5. **Proteção contra Erros**
- ✅ Não permite deletar último admin
- ✅ Não permite deletar seu próprio usuário
- ✅ Validação de campos obrigatórios no formulário
- ✅ Tratamento de exceções no banco de dados

---

## 🔄 Fluxo de Uso

### Cenário 1: Admin Criando Usuário e Dispositivo

```
┌─ Admin faz login (admin / admin123)
│
├─ Clica: Menu → Usuários → Novo
│  ├─ Preenche: João, joao@email.com, senha123
│  ├─ Marca: "Usuário Comum"
│  └─ Clica: Criar → [Sucesso!]
│
├─ Clica: Menu → Dispositivos → Novo
│  ├─ Preenche: "Servidor Web", 192.168.1.10, SERVER
│  └─ Clica: Criar → [Sucesso!]
│
├─ Clica: Menu → Usuários → João → Permissões
│  ├─ Marca: "Acesso" para "Servidor Web"
│  └─ Clica: Salvar → [Sucesso!]
│
└─ Log criado:
   ├─ user_id: 1 (admin)
   ├─ action: "user_created", "device_created", etc
   └─ status: "success"
```

### Cenário 2: Usuário Comum Acessando Dispositivo

```
┌─ João faz login (joao / senha123)
│
├─ Clica: Menu → Dispositivos
│  └─ Vê "Servidor Web" (permitido) e "Câmera 1" (negado)
│
├─ Clica: "Acessar" em "Servidor Web"
│  ├─ Sistema verifica USER_PERMISSION
│  ├─ ✅ Encontra: can_read=True
│  ├─ Renderiza: device_access.html
│  └─ Log criado: action="device_access", status="success"
│
└─ Dashboard mostra: "Servidor Web" acessado às 14:30 por João

[Se fosse negado]
├─ Clica: "Acessar" em "Câmera 1" (negada)
├─ ❌ Sem permissão
├─ Log criado: action="unauthorized_access", is_suspicious=True
└─ ALERT automático gerado: "Acesso não autorizado"
```

### Cenário 3: Admin Detectando Anomalia

```
┌─ Admin vê Dashboard
│  └─ Alerta "3 alertas ativos"
│
├─ Clica: Menu → Alertas
│  ├─ Vê: "Acesso não autorizado - HIGH"
│  ├─ Origem: Tentativa de Maria em Câmera 1
│  └─ IP: 203.0.113.45 (incomum!)
│
├─ Clica: Visualizar Log Associado
│  ├─ Vê: Timestamp, IP, User-Agent
│  └─ Confirma: Atividade suspeita
│
├─ Ações possíveis:
│  ├─ Marca alerta como "Resolvido"
│  ├─ Desativa o usuário Maria
│  └─ Verifica outros logs de Maria
│
└─ Sistema: Análise completa e resposta rápida
```

---

## 💻 Stack Tecnológico

### **Backend**
```
┌─────────────────────────────────┐
│   Framework: Flask 2.3.3        │
│   ORM: SQLAlchemy 3.0.5         │
│   Autenticação: Flask-Login     │
│   Migrations: Flask-Migrate     │
│   Segurança: Werkzeug (bcrypt)  │
│   Banco: SQLite                 │
└─────────────────────────────────┘
```

### **Frontend**
```
┌─────────────────────────────────┐
│   Template: Jinja2              │
│   CSS: Bootstrap 5.1.3          │
│   Icons: Bootstrap Icons        │
│   JS: Vanilla JavaScript        │
│   Funcionalidades:              │
│   - Tooltips                    │
│   - Confirmações               │
│   - Filtros de dados            │
│   - CSV export                  │
│   - Date masks                  │
│   - Table sorting               │
└─────────────────────────────────┘
```

### **Infraestrutura**
```
┌─────────────────────────────────┐
│   Python 3.11+                  │
│   Virtual Environment           │
│   Git (controle de versão)      │
│   VS Code (desenvolvimento)     │
└─────────────────────────────────┘
```

---

## ⭐ Diferenciais

### 1. **Auditoria Automática**
- Cada ação registrada automaticamente
- Sem necessidade de configuração manual
- Histórico completo preservado

### 2. **Alertas Inteligentes**
- Detecta anomalias automaticamente
- Gera alertas com níveis de severidade
- Admin informado em tempo real

### 3. **Interface Intuitiva**
- Design moderno com Bootstrap
- Responsivo (funciona em mobile)
- Botões intuitivos (lápis=editar, lixeira=deletar)

### 4. **Controle de Acesso Granular**
- RBAC simples mas eficaz
- Permissões por dispositivo
- Rastreamento de quem concedeu

### 5. **Proteção de Dados**
- Cascade delete automático
- Validações em múltiplas camadas
- Sem data loss acidental

### 6. **Modularização**
- Código organizado em blueprints
- Fácil manutenção e escalabilidade
- Separação clara de responsabilidades

### 7. **Dashboard Executivo**
- KPIs em tempo real
- Últimos acessos visíveis
- Status do sistema centralizado

---

## 🚀 Como Usar

### Instalação
```bash
# 1. Clonar repositório
git clone https://github.com/jtz04/Projetos-Flask.git
cd Projetos-Flask

# 2. Criar virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

# 3. Instalar dependências
pip install -r sistema_logs/requirements.txt

# 4. Executar aplicação
cd sistema_logs
python app.py
```

### Acesso Inicial
```
URL: http://127.0.0.1:5000
Usuário: admin
Senha: admin123
```

---

## 📈 Próximas Melhorias (Roadmap)

- [ ] Painel de controle com gráficos (Chart.js)
- [ ] Exportação de relatórios em PDF
- [ ] Notificações por email de alertas
- [ ] Integração com LDAP/Active Directory
- [ ] API REST para integrações
- [ ] Dashboard mobile-first
- [ ] Autenticação 2FA
- [ ] Backup automático do banco

---

## 📞 Suporte e Documentação

- **Documentação Técnica**: `/DER_DIAGRAM.md`
- **Código comentado**: Todas classes e funções
- **Exemplo de uso**: Credenciais padrão (admin/admin123)

---

## ✅ Conclusão

Um sistema **robusto, seguro e escalável** de monitoramento e auditoria que fornece:

1. ✅ **Visibilidade** completa sobre acessos aos dispositivos
2. ✅ **Segurança** com detecção automática de anomalias
3. ✅ **Conformidade** com logs e auditoria
4. ✅ **Facilidade** de uso intuitivo
5. ✅ **Escalabilidade** para crescer com a organização

---

**Desenvolvido em**: 2025-11-20  
**Versão**: 1.0  
**Status**: Funcional e pronto para produção  
**Autor**: jtz04 (GitHub)

---

## 📊 Quick Stats

| Métrica | Valor |
|---------|-------|
| **Tabelas do Banco** | 5 |
| **Blueprints** | 6 |
| **Templates** | 10+ |
| **Modelos** | 5 |
| **Rotas** | 20+ |
| **Funcionalidades** | 50+ |
| **Linhas de Código** | ~2000+ |

