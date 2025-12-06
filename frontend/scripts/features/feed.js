import {
    state,
    set_sort,
    reset_feed,
    set_feed_loading,
    append_papers,
    is_logged_in
} from '../core/state.js';
import { navigate, build_url, replace_route } from '../core/router.js';
import { papers } from '../core/api.js';

import { escape_html, format_date, show_view, $, set_html } from '../core/utils.js';

let scroll_observer = null;

export async function show_feed(sort = null, page = 1) {
    const needs_reset = (sort && sort !== state.current_sort) || !state.feed.papers.length;

    if (sort && sort !== state.current_sort)
        set_sort(sort);

    if (needs_reset) reset_feed();
    
    show_view('feed-view');
    update_filter_buttons();

    if (needs_reset) {
        const container = $('papers-list');
        set_html(container, '<div class="loading">loading</div>');
    }

    await Promise.all([
        needs_reset ? load_more_papers() : render_current_papers()
    ]);

    setup_scroll_observer();
}

function setup_scroll_observer() {
    if (scroll_observer) scroll_observer.disconnect();
    
    const sentinel = $('feed-sentinel');
    if (!sentinel) return;
    
    scroll_observer = new IntersectionObserver(
        (entries) => {
            const entry = entries[0];
            if (entry.isIntersecting && state.feed.has_more && !state.feed.is_loading)
                load_more_papers();
        },
        {
            root: null,
            root_margin: '200px',
            threshold: 0
        }
    );
    
    scroll_observer.observe(sentinel);
}

function update_filter_buttons() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.sort === state.current_sort);
    });
}

async function load_more_papers() {
    if (state.feed.is_loading || !state.feed.has_more) return;
    
    set_feed_loading(true);
    update_loading_state();
    
    try {
        const params = {
            sort: state.current_sort,
            page: state.feed.page,
            page_size: state.page_size,
        };
        
        const search_input = $('search-input')?.value.trim();
        if (search_input) params.search = search_input;
        
        const data = await papers.list(params);

        append_papers(data.papers, data.total, data.total_pages);
        render_current_papers();
        
    } catch (error) {
        show_feed_error(error.message);
    } finally {
        set_feed_loading(false);
        update_loading_state();
    }
}

function render_current_papers() {
    const container = $('papers-list');
    
    if (state.feed.papers.length === 0) {
        set_html(container, `
            <div class="feed-empty">
                <p>no papers found</p>
                ${is_logged_in() ? '<p><a href="#" data-action="editor">be the first to publish</a></p>' : ''}
            </div>
        `);
        
        container?.querySelector('[data-action="editor"]')?.addEventListener('click', (e) => {
            e.preventDefault();
            import('./editor.js').then(m => m.show_editor());
        });
        
        update_sentinel_visibility(false);
        return;
    }
    
    set_html(container, state.feed.papers.map(render_paper_card).join(''));
    attach_paper_listeners(container);
    update_sentinel_visibility(state.feed.has_more);
}

function render_paper_card(paper) {
    const paper_url = build_url('paper', { slug: paper.slug });
    const profile_url = build_url('profile', { username: paper.author.username });

    return `
        <div class="paper-item">
            <div class="paper-row-top">
                <h2>
                    <a href="${paper_url}" data-paper="${paper.slug}">
                        ${escape_html(paper.title)}
                    </a>
                </h2>
                <div class="paper-meta">
                    <span>
                        by <a href="${profile_url}" data-profile="${paper.author.username}">${paper.author.username}</a>
                    </span>
                    <span>${format_date(paper.published_at || paper.created_at)}</span>
                </div>
            </div>

            <div class="paper-row-bottom">
                <div class="paper-tags">
                    ${(paper.tags || []).map(tag => `
                        <span class="tag" data-tag="${escape_html(tag)}">${escape_html(tag)}</span>
                    `).join('')}
                </div>

                <div class="paper-stats">
                    <span>^ ${paper.vote_count}</span>
                </div>
            </div>
        </div>
    `;
}

function attach_paper_listeners(container) {
    container?.querySelectorAll('[data-paper]').forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            navigate(`/paper/${el.dataset.paper}`);
        });
    });
    
    container?.querySelectorAll('[data-profile]').forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            navigate(`/user/${el.dataset.profile}`);
        });
    });
}

function update_loading_state() {
    const loader = $('feed-loader');
    if (loader) {
        loader.classList.toggle('visible', state.feed.is_loading);
    }
}

function update_sentinel_visibility(visible) {
    const sentinel = $('feed-sentinel');
    if (sentinel) {
        sentinel.classList.toggle('hidden', !visible);
    }
    
    const end_message = $('feed-end');
    if (end_message) {
        end_message.classList.toggle('visible', !visible && state.feed.papers.length > 0);
    }
}


function show_feed_error(message) {
    const container = $('papers-list');
    if (state.feed.papers.length === 0) {
        set_html(container, `<div class="feed-error">error: ${message}</div>`);
    }
}

export function search_papers() {
    reset_feed();
    load_more_papers().then(() => setup_scroll_observer());
}

export function search_by_tag(tag) {
    const search_input = $('search-input');
    if (search_input) search_input.value = tag;

    search_papers();
}

export function init_feed() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            e.preventDefault();
            
            const sort = btn.dataset.sort;
            reset_feed();

            if (sort === 'recent') {
                navigate('/');
            } else {
                navigate(`/feed/${sort}`);
            }
        });
    });
    
    $('search-input')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') search_papers();
    });

    document.querySelector('.search-box button')?.addEventListener('click', search_papers);
    
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('tag') && e.target.dataset.tag) {
            search_by_tag(e.target.dataset.tag);
        }
    });
}

export function cleanup_feed() {
    if (scroll_observer) {
        scroll_observer.disconnect();
        scroll_observer = null;
    }
}
