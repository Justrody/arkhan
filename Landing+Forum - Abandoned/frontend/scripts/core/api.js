import { state } from './state.js';

const API_BASE = '/api';

export async function api(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    if (state.token)
        headers['Authorization'] = `Bearer ${state.token}`;
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `request failed: ${response.status}`);
        }
        
        if (response.status === 204) return null;
        return response.json();
    } catch (error) {
        console.error('api error:', error);
        throw error;
    }
}

export const auth = {
    login: (username, password) => {
        const form_data = new URLSearchParams();
        form_data.append('username', username);
        form_data.append('password', password);
        
        return fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: form_data,
        }).then(r => r.ok ? r.json() : r.json().then(e => Promise.reject(e)));
    },
    
    register: (data) => api('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    
    me: () => api('/auth/me'),
};

export const users = {
    profile: (username) => api(`/users/${username}`),
    me: () => api('/users/me'),
    update: (data) => api('/users/me', { method: 'PUT', body: JSON.stringify(data) }),
};

export const papers = {
    list: (params) => api(`/papers/?${new URLSearchParams(params)}`),
    get: (slug) => api(`/papers/${slug}`),
    create: (data) => api('/papers/', { method: 'POST', body: JSON.stringify(data) }),
    update: (slug, data) => api(`/papers/${slug}`, { method: 'PUT', body: JSON.stringify(data) }),
    preview: (content) => api('/papers/preview', { method: 'POST', body: JSON.stringify({ content }) }),
    featured: () => api('/papers/featured'),
    trending_tags: () => api('/papers/trending-tags'),
    user_papers: (username) => api(`/papers/user/${username}`),
};

export const votes = {
    status: (slug) => api(`/papers/${slug}/vote/`),
    upvote: (slug) => api(`/papers/${slug}/vote/`, { method: 'POST' }),
    remove: (slug) => api(`/papers/${slug}/vote/`, { method: 'DELETE' }),
};
