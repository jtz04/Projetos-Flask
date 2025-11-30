# DER - Diagrama de Entidade-Relacionamento
## Sistema de Logs e Monitoramento de Dispositivos

---

## 📊 Visão Geral do Banco de Dados

O sistema possui **5 tabelas principais** que trabalham juntas para:
- ✅ Gerenciar usuários e autenticação
- ✅ Monitorar dispositivos de rede
- ✅ Controlar permissões de acesso (RBAC)
- ✅ Registrar todos os acessos em logs
- ✅ Gerar alertas automáticos para atividades suspeitas

---

## 🗂️ Estrutura das Tabelas

### 1️⃣ **USER** (Usuários do Sistema)
```
┌─────────────────────────────────────┐
│           USER                      │
├─────────────────────────────────────┤
│ PK  id                INT            │
│     username          STRING(80)     │ ← Único
│     email             STRING(120)    │ ← Único
│     password_hash     STRING(255)    │
│     role              ENUM           │ ← ADMIN / USER
│     created_at        DATETIME       │
│     is_active         BOOLEAN        │
└─────────────────────────────────────┘
        ▲                    ▲
        │                    │
        │ (1)                │ (1)
        │                    │
        └────────┬───────────┘
                 │
        ┌────────┴────────┐
        │                 │
    [Permissões]      [Logs de Acesso]
    [Dados Concedidos] [Tentativas Login]
```

**Função:**
- Armazena todos os usuários do sistema
- **role**: Define se é ADMIN (acesso total) ou USER (acesso restrito)
- **is_active**: Permite bloquear usuários sem deletá-los
- Cada usuário tem:
  - ✓ Múltiplas **permissões** em dispositivos
  - ✓ Múltiplos **logs de acesso**
  - ✓ Permissões **concedidas por ele** (se for admin)

---

### 2️⃣ **DEVICE** (Dispositivos a Monitorar)
```
┌─────────────────────────────────────┐
│          DEVICE                     │
├─────────────────────────────────────┤
│ PK  id                INT            │
│     name              STRING(100)    │
│     ip_address        STRING(45)     │
│     device_type       ENUM           │ ← COMPUTER/SERVER/CAMERA/SWITCH/ROUTER
│     description       TEXT           │
│     location          STRING(200)    │
│     is_active         BOOLEAN        │
│     created_at        DATETIME       │
└─────────────────────────────────────┘
        ▲                    ▲
        │                    │
        │ (1)                │ (1)
        │                    │
        └────────┬───────────┘
                 │
        ┌────────┴────────┐
        │                 │
    [Permissões]      [Logs de Acesso]
    [Quem tem acesso]  [Acessos realizados]
```

**Função:**
- Armazena os dispositivos que serão monitorados
- Pode ser: computador, servidor, câmera, switch, roteador, etc.
- Cada dispositivo tem:
  - ✓ Múltiplas **permissões** de usuários
  - ✓ Múltiplos **logs de acesso**

---

### 3️⃣ **USER_PERMISSION** (Controle de Acesso)
```
┌──────────────────────────────────────────┐
│       USER_PERMISSION                    │
│  (Tabela de Junção / Relacionamento)    │
├──────────────────────────────────────────┤
│ PK  id                INT                │
│ FK  user_id           INT ──────┐        │
│ FK  device_id         INT       │        │
│ FK  granted_by        INT       │        │
│     can_read          BOOLEAN   │        │
│     can_write         BOOLEAN   │        │
│     can_execute       BOOLEAN   │        │
│     granted_at        DATETIME  │        │
└──────────────────────────────────────────┘
             │                    │
             ▼                    ▼
        USER (quem)         DEVICE (o quê)
        
        USER (admin)
             ▲
             │ granted_by
             │
      Quem concedeu a permissão
```

**Função - RBAC (Role-Based Access Control):**
- Define **qual usuário tem acesso a qual dispositivo**
- Armazena **3 tipos de permissão**:
  - `can_read` = usuário pode acessar/visualizar o dispositivo
  - `can_write` = usuário pode modificar o dispositivo
  - `can_execute` = usuário pode executar ações no dispositivo
- `granted_by` rastreia **qual admin** concedeu a permissão
- `granted_at` registra **quando** foi concedida

**Relacionamentos:**
- ✓ 1 usuário → N permissões em N dispositivos
- ✓ 1 dispositivo → N permissões de N usuários
- ✓ Muitos-para-muitos com **atributos** (can_read/write/execute)

---

### 4️⃣ **ACCESS_LOG** (Auditoria e Rastreamento)
```
┌─────────────────────────────────────────┐
│        ACCESS_LOG                       │
│  (Histórico de Acessos/Tentativas)     │
├─────────────────────────────────────────┤
│ PK  id                INT                │
│ FK  user_id           INT ──────┐        │
│ FK  device_id         INT       │        │
│     access_time       DATETIME  │        │
│     action            STRING    │        │
│     status            STRING    │        │
│     ip_address        STRING    │        │
│     user_agent        TEXT      │        │
│     details           TEXT      │        │
│     is_suspicious     BOOLEAN ──┤──┐    │
└─────────────────────────────────────┬──┘
             │                        │
             ▼                        ▼
        USER (quem acessou)   DEVICE (qual)
        
        is_suspicious = True
             │
             ▼
        Gera ALERT automaticamente
```

**Função - Auditoria Completa:**
- Registra **cada tentativa de acesso** (sucesso ou falha)
- Tipos de ação: `system_login`, `device_access`, `unauthorized_access_attempt`, etc.
- Captura informações técnicas:
  - `ip_address`: IP do usuário que tentou acessar
  - `user_agent`: Browser/cliente usado
  - `details`: Contexto adicional
- **is_suspicious**: Flag que marca acessos anormais
  - Tentativa de acesso não autorizado
  - Múltiplas falhas de login
  - Acesso fora de padrão

**Relacionamentos:**
- 1 usuário → N logs de acesso
- 1 dispositivo → N logs de acesso
- Muitos-para-um (N:1) em ambas as direções

---

### 5️⃣ **ALERT** (Alertas de Segurança)
```
┌─────────────────────────────────────┐
│          ALERT                      │
│  (Alertas de Segurança)            │
├─────────────────────────────────────┤
│ PK  id                INT            │
│     title             STRING(200)    │
│     description       TEXT           │
│     alert_level       ENUM           │ ← LOW / MEDIUM / HIGH
│     created_at        DATETIME       │
│     resolved_at       DATETIME       │
│     is_resolved       BOOLEAN        │
└─────────────────────────────────────┘
        ▲
        │ (1)
        │ (originado por)
        │
   ACCESS_LOG
   (is_suspicious = True)
```

**Função - Alertas Automáticos:**
- Gerado **automaticamente** quando `access_log.is_suspicious = True`
- **Níveis de severidade**:
  - `LOW`: Informativo, risco mínimo
  - `MEDIUM`: Aviso, requer atenção
  - `HIGH`: Crítico, ação imediata necessária
- Admins podem **marcar como resolvido**
- Rastreia quando foi criado e resolvido

---

## 🔗 Relacionamentos (Mapa Completo)

```
                     ┌──────────────┐
                     │     USER     │
                     │  (Usuários)  │
                     └──────────────┘
                      ▲      ▲       ▲
                      │      │       │
         ┌────────────┘      │       └──────────────┐
         │                   │                      │
         │              (1:N)│(1:N)                 │
         │                   │                      │
         ▼                   ▼                      ▼
    ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐
    │ USER_PERM   │  │ ACCESS_LOG   │  │ USER_PERMISSION │
    │ (Concede)   │  │ (Auditoria)  │  │ (Acesso)        │
    └─────────────┘  └──────────────┘  └─────────────────┘
                      │       │                  │
                      │       │ (N:1)            │ (N:1)
                      │       │                  │
                      ▼       ▼                  ▼
                    ┌──────────────────┐   ┌────────────┐
                    │     DEVICE       │   │   DEVICE   │
                    │ (Dispositivos)   │   │            │
                    └──────────────────┘   └────────────┘
                      │
                      │ (1:N)
                      │
                      ▼
                   ┌──────────┐
                   │  ALERT   │
                   │ (Alertas)│
                   └──────────┘
```

---

## 📋 Fluxos de Dados Principais

### ✅ Fluxo 1: Criação de Permissão
```
Admin cria permissão para usuário
              │
              ▼
        USER_PERMISSION
   (user_id=5, device_id=3)
              │
         Salvo no DB
              │
              ▼
    Usuário 5 agora pode acessar dispositivo 3
```

### ✅ Fluxo 2: Acesso a Dispositivo
```
Usuário tenta acessar dispositivo
              │
              ▼
    Verifica USER_PERMISSION
              │
      ┌───────┴───────┐
      │               │
   PERMITIDO      NEGADO
      │               │
      ▼               ▼
  ACCESS_LOG     ACCESS_LOG
  (status: success) (status: failed)
  (is_suspicious: False) (is_suspicious: True)
      │               │
      ▼               ▼
  [Dispositivo Acessado] [ALERT Gerado]
```

### ✅ Fluxo 3: Detecção de Anomalia
```
Múltiplas tentativas de login com erro
              │
              ▼
      ACCESS_LOG
  (is_suspicious: True)
              │
              ▼
        ALERT Criado
    (alert_level: HIGH)
              │
              ▼
  Admin visualiza em /alerts
  e marca como resolvido
```

---

## 🔐 Segurança e Integridade

### **Cascata de Exclusão (CASCADE)**
- ✓ Se deletar um **USER**: automaticamente deleta suas PERMISSÕES e LOGS
- ✓ Se deletar um **DEVICE**: automaticamente deleta suas PERMISSÕES e LOGS
- Garante **integridade referencial**

### **Validações**
- ✓ `is_active = False`: Bloqueia login sem deletar usuário
- ✓ `device_id` pode ser NULL em ACCESS_LOG: Permite logs de ação geral (login do sistema)
- ✓ `granted_by` rastreia quem criou permissões
- ✓ Timestamps (`created_at`, `granted_at`, `access_time`) em todas as tabelas

### **RBAC (Control de Acesso Baseado em Papéis)**
```
USER (role = ADMIN)
  └─ Pode: criar/editar/deletar usuários
  └─ Pode: criar/editar/deletar dispositivos
  └─ Pode: granter permissões a usuários
  └─ Pode: visualizar TODOS os logs e alertas

USER (role = USER)
  └─ Pode: acessar apenas dispositivos com permissão
  └─ Pode: visualizar apenas seus próprios logs
  └─ Não pode: gerenciar usuários
```

---

## 📊 Exemplo de Dados (Casos de Uso)

### Caso 1: Usuário comum acessando um dispositivo
```
USER
├─ id: 2
├─ username: "joao"
└─ role: USER

DEVICE
├─ id: 1
├─ name: "Servidor Web"
└─ ip_address: "192.168.1.10"

USER_PERMISSION
├─ user_id: 2
├─ device_id: 1
├─ can_read: True
└─ can_write: False

ACCESS_LOG
├─ user_id: 2
├─ device_id: 1
├─ action: "device_access"
├─ status: "success"
├─ access_time: "2025-11-20 14:30:00"
└─ is_suspicious: False
```

### Caso 2: Tentativa não autorizada
```
USER
├─ id: 3
├─ username: "maria"
└─ role: USER

DEVICE
├─ id: 2
├─ name: "Câmera Segurança"
└─ ip_address: "192.168.1.20"

[Nenhuma USER_PERMISSION entre usuário 3 e dispositivo 2]

ACCESS_LOG
├─ user_id: 3
├─ device_id: 2
├─ action: "unauthorized_access_attempt"
├─ status: "failed"
├─ access_time: "2025-11-20 14:35:00"
└─ is_suspicious: True ◄─── Ativa!

ALERT (auto-gerado)
├─ title: "Acesso não autorizado detectado"
├─ description: "Usuário 3 tentou acessar dispositivo 2"
├─ alert_level: "HIGH"
└─ is_resolved: False
```

---

## 🎯 Resumo de Relacionamentos

| De | Para | Tipo | Descrição |
|---|---|---|---|
| USER | USER_PERMISSION | 1:N | Um usuário tem múltiplas permissões |
| DEVICE | USER_PERMISSION | 1:N | Um dispositivo tem múltiplas permissões |
| USER | ACCESS_LOG | 1:N | Um usuário tem múltiplos acessos registrados |
| DEVICE | ACCESS_LOG | 1:N | Um dispositivo tem múltiplos acessos registrados |
| ACCESS_LOG | ALERT | 1:N | Um log suspeito gera múltiplos alertas |
| USER | USER (self) | 1:N | Um admin pode conceder permissões (granted_by) |

---

## 💾 Conclusão

Este DER implementa um **sistema robusto de auditoria e controle de acesso**:

1. **USER**: Autenticação e autorização básica
2. **DEVICE**: Inventário de recursos
3. **USER_PERMISSION**: RBAC (quem pode acessar o quê)
4. **ACCESS_LOG**: Auditoria completa de todas ações
5. **ALERT**: Detecção e resposta a anomalias

Tudo funciona em **cascata automática**: um acesso suspeito → gera log → gera alerta → admin resolve.

---

**Criado em**: 2025-11-20  
**Sistema**: Sistema de Logs e Monitoramento de Dispositivos (Flask + SQLAlchemy)
