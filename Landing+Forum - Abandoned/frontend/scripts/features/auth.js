import { auth } from '../core/api.js';
import { navigate, build_url } from '../core/router.js';
import { state, set_user, set_token } from '../core/state.js';
import { toast, $, toggle } from '../core/utils.js';

const STORAGE_TOKEN = 's_token';
const STORAGE_USER = 's_user';

export function load_auth_state() {
    const token = localStorage.getItem(STORAGE_TOKEN);
    const user = localStorage.getItem(STORAGE_USER);

    if (token && user) {
        set_token(token);
        set_user(JSON.parse(user));
    }

    update_auth_ui();
    update_nav_ui(); // UI do Rody
}

function save_auth_state() {
    if (state.token && state.user) {
        localStorage.setItem(STORAGE_TOKEN, state.token);
        localStorage.setItem(STORAGE_USER, JSON.stringify(state.user));
    }
}

function clear_auth_state() {
    set_token(null);
    set_user(null);

    localStorage.removeItem(STORAGE_TOKEN);
    localStorage.removeItem(STORAGE_USER);

    update_auth_ui();
    update_nav_ui();
}

export function update_auth_ui() {
    const auth_container = $('nav-auth');
    const write_link = $('nav-write');

    if (state.user) {
        const profile_url = build_url('profile', { username: state.user.username });

        auth_container.innerHTML = `
            <a href="${profile_url}" class="nav-user" data-profile="${state.user.username}">
                ${state.user.username}
            </a>
            <button class="btn-secondary" data-logout>logout</button>
        `;

        auth_container.querySelector('[data-profile]')?.addEventListener('click', (e) => {
            e.preventDefault();
            navigate(`/user/${state.user.username}`);
        });

        auth_container.querySelector('[data-logout]')?.addEventListener('click', logout);

        if (write_link) write_link.style.display = '';
    } else {
        auth_container.innerHTML = `
            <button class="btn-secondary" data-auth>access</button>
        `;

        auth_container.querySelector('[data-auth]')?.addEventListener('click', () => show_auth_modal('login'));

        if (write_link) write_link.style.display = 'none';
    }
}

export async function login(username, password) {
    try {
        const data = await auth.login(username, password);

        set_token(data.access_token);
        set_user(data.user);
        save_auth_state();

        update_auth_ui();
        update_nav_ui();
        close_auth_modal();

        toast('welcome back', 'success');
    } catch (error) {
        toast(error.message || error.detail || 'login failed', 'error');
    }
}

export async function register(user_data) {
    try {
        await auth.register(user_data);
        await login(user_data.username, user_data.password);
        toast('welcome aboard', 'success');
    } catch (error) {
        toast(error.message || 'registration failed', 'error');
    }
}

export function logout() {
    clear_auth_state();
    navigate('/');
    toast('disconnected', 'success');
}

export function show_auth_modal(tab = 'login') {
    const modal = $('auth-modal');
    modal?.classList.remove('hidden');

    document.querySelectorAll('.auth-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
    });

    toggle('login-form', tab === 'login');
    toggle('register-form', tab === 'register');
}

export function close_auth_modal() {
    $('auth-modal')?.classList.add('hidden');
}

export function init_auth() {
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tab_name = tab.dataset.tab;

            document.querySelectorAll('.auth-tab').forEach(t => {
                t.classList.toggle('active', t.dataset.tab === tab_name);
            });

            toggle('login-form', tab_name === 'login');
            toggle('register-form', tab_name === 'register');
        });
    });

    $('login-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await login(
            $('login-username').value.trim(),
            $('login-password').value
        );
    });

    $('register-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await register({
            username: $('register-username').value.trim(),
            email: $('register-email').value.trim(),
            password: $('register-password').value,
        });
    });

    $('auth-modal')?.addEventListener('click', (e) => {
        if (e.target.id === 'auth-modal') close_auth_modal();
    });

    $('auth-modal')?.querySelector('.modal-close')?.addEventListener('click', close_auth_modal);
}

//codigo do rody
export function update_nav_ui() {
    const loginBtn = document.getElementById('login-open-btn');
    const accountBtn = document.getElementById('open-modal');

    if (!loginBtn || !accountBtn) return;

    if (state.user) {
        loginBtn.classList.add('hidden');
        accountBtn.textContent = state.user.username;
        accountBtn.classList.remove('hidden');
    } else {
        loginBtn.classList.remove('hidden');
        accountBtn.textContent = "";
        accountBtn.classList.add('hidden');
    }
}
