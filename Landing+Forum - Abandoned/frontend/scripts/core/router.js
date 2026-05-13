const routes = {
    '': 'feed',
    '/': 'feed',
    '/feed': 'feed',
    '/feed/:sort': 'feed',
    '/paper/:slug': 'paper',
    '/user/:username': 'profile',
    '/publish': 'editor',
    '/edit/:slug': 'editor-edit',
};

const handlers = {};

export function register_route(name, handler) {
    handlers[name] = handler;
}

function parse_hash(hash) {
    let path = hash.replace(/^#/, '') || '/';
    if (!path.startsWith('/')) path = '/' + path;
    
    for (const [pattern, name] of Object.entries(routes)) {
        const params = match_route(pattern, path);
        if (params !== null) {
            return { name, params, path };
        }
    }
    
    return { name: 'feed', params: {}, path };
}

function match_route(pattern, path) {
    if (pattern === '') pattern = '/';
    
    const pattern_parts = pattern.split('/').filter(Boolean);
    const path_parts = path.split('/').filter(Boolean);
    
    if (pattern_parts.length === 0 && path_parts.length === 0) {
        return {};
    }
    
    if (pattern_parts.length !== path_parts.length) {
        return null;
    }
    
    const params = {};
    
    for (let i = 0; i < pattern_parts.length; i++) {
        const pattern_part = pattern_parts[i];
        const path_part = path_parts[i];
        
        if (pattern_part.startsWith(':')) {
            params[pattern_part.slice(1)] = decodeURIComponent(path_part);
        } else if (pattern_part !== path_part) {
            return null;
        }
    }
    
    return params;
}

export function navigate(path, replace = false) {
    const new_hash = '#' + (path.startsWith('/') ? path : '/' + path);
    
    if (replace) {
        window.history.replaceState(null, '', new_hash);
    } else {
        window.history.pushState(null, '', new_hash);
    }
    
    handle_route();
}

export function replace_route(path) {
    navigate(path, true);
}

export function handle_route() {
    const { name, params, path } = parse_hash(window.location.hash);
    
    const handler = handlers[name];
    if (handler) {
        handler(params);
    } else {
        console.warn(`no handler for route: ${name}`);
        if (handlers.feed) handlers.feed({});
    }
}

export function get_current_route() {
    return parse_hash(window.location.hash);
}

export function build_url(route, params = {}) {
    switch (route) {
        case 'feed':
            return params.sort && params.sort !== 'recent' ? `#/feed/${params.sort}` : '#/';
        case 'paper':
            return `#/paper/${encodeURIComponent(params.slug)}`;
        case 'profile':
            return `#/user/${encodeURIComponent(params.username)}`;
        case 'editor':
            return '#/publish';
        case 'editor-edit':
            return `#/edit/${encodeURIComponent(params.slug)}`;
        case 'leaderboard':
            return '#/rankings';
        default:
            return '#/';
    }
}

export function init_router() {
    window.addEventListener('hashchange', handle_route);
    handle_route();
}

export function is_route(name, params = {}) {
    const current = get_current_route();
    if (current.name !== name) return false;
    
    for (const [key, value] of Object.entries(params)) {
        if (current.params[key] !== value) return false;
    }
    
    return true;
}
