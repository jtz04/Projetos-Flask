/**
 * ARQUIVO: script.js
 * DESCRIÇÃO: Funções JavaScript para o Sistema de Logs
 * 
 * Funcionalidades:
 * - Inicialização de tooltips e confirmações
 * - Filtros de data e auto-refresh
 * - Exportação de tabelas para CSV
 * - Fetch de dados via AJAX
 * - Sistema de notificações
 * - Validação de formulários
 * - Máscaras de input
 * - Ordenação de tabelas
 * - Utilidades de formatação
 */

/* ========== INICIALIZAÇÃO ========== */
/* Aguarda carregamento completo do DOM antes de executar */
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Inicializa todos os componentes da aplicação
 */
function initializeApp() {
    // Inicializar tooltips do Bootstrap
    initializeTooltips();
    
    // Inicializar confirmações para ações destrutivas
    initializeConfirmations();
    
    // Inicializar filtros de data nos formulários
    initializeDateFilters();
    
    // Inicializar auto-refresh (se a página tiver o atributo data-auto-refresh)
    initializeAutoRefresh();
}

/**
 * Inicializa tooltips do Bootstrap
 * Tooltips mostram informações adicionais ao passar o mouse
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Adiciona confirmação antes de ações destrutivas
 * Formulários que deletam, togglam ou resolvem alertas
 */
function initializeConfirmations() {
    // Buscar todos os formulários que executam ações destrutivas
    const destructiveForms = document.querySelectorAll('form[action*="toggle"], form[action*="delete"], form[action*="resolve"]');
    destructiveForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Tem certeza que deseja realizar esta ação?')) {
                e.preventDefault();  // Cancela submissão do formulário
            }
        });
    });
}

/**
 * Inicializa filtros de data com valores padrão
 * Define data até hoje e data de 7 dias atrás como padrão
 */
function initializeDateFilters() {
    // Campo "Data Até" recebe a data de hoje
    const dateTo = document.getElementById('date_to');
    const dateFrom = document.getElementById('date_from');
    
    if (dateTo && !dateTo.value) {
        const today = new Date().toISOString().split('T')[0];
        dateTo.value = today;
    }
    
    // Campo "Data De" recebe data de 7 dias atrás
    if (dateFrom && !dateFrom.value) {
        const lastWeek = new Date();
        lastWeek.setDate(lastWeek.getDate() - 7);
        dateFrom.value = lastWeek.toISOString().split('T')[0];
    }
}

/**
 * Auto-refresh de páginas que precisam de dados em tempo real
 * Usa atributo data-auto-refresh na página
 * Exemplo: <div data-auto-refresh data-refresh-interval="30000">
 */
function initializeAutoRefresh() {
    // Verifica se a página tem atributo de auto-refresh
    if (document.querySelector('[data-auto-refresh]')) {
        // Intervalo padrão: 30 segundos (30000ms)
        const refreshInterval = document.querySelector('[data-auto-refresh]').getAttribute('data-refresh-interval') || 30000;
        setInterval(() => {
            // Só atualiza se a aba está visível (não recarrega em background)
            if (!document.hidden) {
                window.location.reload();
            }
        }, refreshInterval);
    }
}

/* ========== EXPORTAÇÃO DE TABELAS ========== */

/**
 * Exporta tabela HTML para arquivo CSV
 * @param {string} filename - Nome do arquivo CSV a ser criado
 * @param {string} tableId - ID da tabela (opcional, usa primeira tabela se não informado)
 */
function exportTableToCSV(filename, tableId = null) {
    // Selecionar tabela
    let table;
    if (tableId) {
        table = document.getElementById(tableId);
    } else {
        table = document.querySelector('table');
    }
    
    if (!table) {
        alert('Nenhuma tabela encontrada para exportar.');
        return;
    }
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    // Iterar por cada linha da tabela
    for (let i = 0; i < rows.length; i++) {
        const row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            // Limpar texto removendo ícones e formatos visuais
            let text = cols[j].innerText
                .replace(/\n/g, ' ')
                .replace(/\s+/g, ' ')
                .trim();
            row.push('"' + text + '"');
        }
        
        csv.push(row.join(","));
    }

    // Download do arquivo
    downloadCSV(csv.join("\n"), filename);
}

/**
 * Cria e faz download de arquivo CSV
 * @param {string} csv - Conteúdo CSV
 * @param {string} filename - Nome do arquivo
 */
function downloadCSV(csv, filename) {
    // Criar blob com UTF-8 BOM (compatibilidade com Excel em Windows)
    const csvFile = new Blob(["\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' });
    const downloadLink = document.createElement("a");
    
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = "none";
    
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

/* ========== FETCH ASSÍNCRONO ========== */

/**
 * Busca dados via AJAX/Fetch API
 * @param {string} url - URL para buscar dados
 * @param {object} options - Opções adicionais (headers, método, etc)
 * @returns {Promise} JSON dos dados retornados
 */
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        // Verificar se resposta foi bem-sucedida
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar dados:', error);
        showNotification('Erro ao carregar dados', 'danger');
        throw error;
    }
}

/* ========== SISTEMA DE NOTIFICAÇÕES ========== */

/**
 * Exibe notificação flutuante no canto superior direito
 * @param {string} message - Mensagem a exibir
 * @param {string} type - Tipo de alerta (info, success, warning, danger)
 * @param {number} duration - Duração em ms antes de desaparecer (0 = permanente)
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    `;
    
    // HTML com mensagem e botão de fechar
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Adicionar ao corpo da página
    document.body.appendChild(notification);
    
    // Auto-remover após duração (se duration > 0)
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }
}

/* ========== VALIDAÇÃO DE FORMULÁRIOS ========== */

/**
 * Valida um formulário verificando campos obrigatórios
 * @param {HTMLFormElement} form - Formulário a validar
 * @returns {boolean} True se válido, false caso contrário
 */
function validateForm(form) {
    // Selecionar todos os campos obrigatórios
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    // Verificar cada campo
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/* ========== MÁSCARAS DE INPUT ========== */

/**
 * Aplica máscaras de formatação aos inputs
 * Suporta IP, data, etc
 */
function applyInputMasks() {
    // Máscara para IP (apenas números e pontos)
    const ipInputs = document.querySelectorAll('input[data-mask="ip"]');
    ipInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^0-9.]/g, '');
            e.target.value = value;
        });
    });
    
    // Máscara para data (remove classe inválida quando preenchido)
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            if (e.target.value) {
                e.target.classList.remove('is-invalid');
            }
        });
    });
}

/* ========== ORDENAÇÃO DE TABELAS ========== */

/**
 * Ordena uma tabela HTML por coluna
 * @param {HTMLTableElement} table - Tabela a ordenar
 * @param {number} column - Índice da coluna
 * @param {boolean} ascending - True para ascendente, false para descendente
 */
function sortTable(table, column, ascending = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Ordenar linhas
    rows.sort((a, b) => {
        const aText = a.cells[column].textContent.trim();
        const bText = b.cells[column].textContent.trim();
        
        // Tentar converter para número se possível (ordenação numérica)
        const aNum = parseFloat(aText.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bText.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return ascending ? aNum - bNum : bNum - aNum;
        }
        
        // Se não for número, ordenar como texto (alfabético)
        return ascending ? 
            aText.localeCompare(bText) : 
            bText.localeCompare(aText);
    });
    
    // Reordenar as linhas na tabela
    rows.forEach(row => tbody.appendChild(row));
    
    // Atualizar indicadores visuais de ordenação
    updateSortIndicators(table, column, ascending);
}

/**
 * Atualiza indicadores visuais de ordenação na tabela
 * @param {HTMLTableElement} table - Tabela
 * @param {number} column - Coluna ordenada
 * @param {boolean} ascending - Direção de ordenação
 */
function updateSortIndicators(table, column, ascending) {
    // Remover indicadores existentes
    const headers = table.querySelectorAll('th');
    headers.forEach(header => {
        header.classList.remove('sorting-asc', 'sorting-desc');
    });
    
    // Adicionar novo indicador na coluna ordenada
    const targetHeader = headers[column];
    targetHeader.classList.add(ascending ? 'sorting-asc' : 'sorting-desc');
}

/* ========== INICIALIZAR MÁSCARAS AO CARREGAR ========== */
document.addEventListener('DOMContentLoaded', applyInputMasks);

/* ========== UTILITÁRIOS DE FORMATAÇÃO ========== */

/**
 * Objeto com funções utilitárias de formatação de dados
 */
const Formatter = {
    /**
     * Formata data ISO para formato brasileiro
     * @param {string} dateString - Data em formato ISO
     * @returns {string} Data formatada (dd/mm/yyyy hh:mm:ss)
     */
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR');
    },
    
    /**
     * Converte bytes para formato legível (KB, MB, GB, etc)
     * @param {number} bytes - Número de bytes
     * @param {number} decimals - Casas decimais
     * @returns {string} Tamanho formatado
     */
    formatBytes: function(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },
    
    /**
     * Formata segundos para formato legível (h, m, s)
     * @param {number} seconds - Número de segundos
     * @returns {string} Duração formatada
     */
    formatDuration: function(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }
};

/* ========== EXPORTAR PARA ESCOPO GLOBAL ========== */
/* Expõe utilitários para uso em templates e scripts inline */

// Expõe objeto Formatter globalmente
window.Formatter = Formatter;

// Expõe funções principais como namespace "SistemaLogs"
window.SistemaLogs = {
    exportTableToCSV,
    showNotification,
    validateForm,
    sortTable,
    fetchData
};