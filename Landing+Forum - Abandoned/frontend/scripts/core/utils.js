export function escape_html(text) {
    if (!text) return '';

    const div = document.createElement('div');
    div.textContent = text;

    return div.innerHTML;
}

export function format_date(date_str) {
    if (!date_str) return '';
    
    const date = new Date(date_str);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

export function toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);
    
    setTimeout(() => {
        el.style.opacity = '0';
        el.style.transform = 'translateX(100%)';
        setTimeout(() => el.remove(), 300);
    }, 4000);
}

export function $(id) {
    return document.getElementById(id);
}

export function $$(selector) {
    return document.querySelectorAll(selector);
}

export function show_view(view_id) {
    $$('.view').forEach(v => v.classList.add('hidden'));

    const view = $(view_id);
    if (view) view.classList.remove('hidden');
}

export function toggle(element, show) {
    if (typeof element === 'string') element = $(element);
    if (element) element.classList.toggle('hidden', !show);
}

export function set_html(element, html) {
    if (typeof element === 'string') element = $(element);
    if (element) element.innerHTML = html;
}

export function on(element, event, handler) {
    if (typeof element === 'string') element = $(element);
    if (element) element.addEventListener(event, handler);
}

export function on_all(selector, event, handler) {
    $$(selector).forEach(el => el.addEventListener(event, handler));
}

