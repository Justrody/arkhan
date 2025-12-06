
export function $(id) {
    return document.getElementById(id);
}

export function $$(selector) {
    return document.querySelectorAll(selector);
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

