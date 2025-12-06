import { load_auth_state, init_auth } from './features/auth.js';
import { init_router, register_route, navigate, build_url } from './core/router.js';

import { show_paper } from './features/paper.js';
import { show_profile } from './features/profile.js';
import { show_feed, init_feed } from './features/feed.js';
import { show_editor, init_editor } from './features/editor.js';

window.navigate_to = navigate;
window.build_url = build_url;

window.show_feed = show_feed;
window.show_editor = show_editor;

function register_routes() {
    register_route('feed', (params) => {
        show_feed(params.sort || 'recent');
    });
    
    register_route('paper', (params) => {
        show_paper(params.slug);
    });
    
    register_route('profile', (params) => {
        show_profile(params.username);
    });
    
    register_route('editor', () => {
        show_editor();
    });
    
    register_route('editor-edit', (params) => {
        edit_paper(params.slug);
    });
}

function init()
{
    load_auth_state();

    init_auth();
    init_feed();
    init_editor();

    register_routes();
    init_router();

    console.log("initialized")
}

document.addEventListener('DOMContentLoaded', init);