import { state } from '../core/state.js';
import { navigate, build_url } from '../core/router.js';
import { users, papers } from '../core/api.js';
import { escape_html, format_date, toast, show_view, $, set_html } from '../core/utils.js';

export async function show_profile(username) {
    show_view('profile-view');
    
    const header_container = $('profile-header');
    const papers_container = $('profile-papers');
    
    set_html(header_container, '<div class="loading">loading</div>');
    
    try {
        const profile = await users.profile(username);

        document.title = `${profile.username} - arkhan`;
        
        const is_own_profile = state.user?.username === username;
        
        set_html(header_container, `
            <div class="profile-info">
                <h1>
                    ${escape_html(profile.username)}
                </h1>

                <div class="profile-stats">
                    <div class="stat">
                        <div class="stat-value">${profile.paper_count || 0}</div>
                        <div class="stat-label">papers</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${profile.votes_received || 0}</div>
                        <div class="stat-label">upvotes</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${profile.reputation_points || 0}</div>
                        <div class="stat-label">reputation</div>
                    </div>
                </div>
            </div>
        `);
                
        await load_user_papers(username, papers_container);
        
    } catch (error) {
        set_html(header_container, `<div style="padding: 2rem; color: var(--red);">error: ${error.message}</div>`);
    }
}

async function load_user_papers(username, container) {
    try {
        const data = await papers.user_papers(username);
        
        if (data.papers.length === 0) {
            set_html(container, '<div style="padding: 2rem; text-align: center; color: var(--text-dim);">no papers published yet</div>');
            return;
        }
        
        set_html(container, `
            <h3 style="margin-bottom: 1rem; color: var(--text-bright); font-weight: normal;">
                publications
            </h3>
            <div class="papers-list">
                ${data.papers.map(paper => render_paper_card(paper)).join('')}
            </div>
        `);
        
        container.querySelectorAll('[data-paper]').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                navigate(`/paper/${el.dataset.paper}`);
            });
        });
        
    } catch (error) {
        set_html(container, '<div style="padding: 2rem; color: var(--dark);">error loading papers</div>');
    }
}

function render_paper_card(paper) {
    const paper_url = build_url('paper', { slug: paper.slug });

    return `
        <div class="paper-item">
            <h2>
                <a href="${paper_url}" data-paper="${paper.slug}">
                    ${escape_html(paper.title)}
                </a>
            </h2>
            <div class="paper-meta">
                <span>${format_date(paper.published_at || paper.created_at)}</span>
            </div>

            <div class="paper-stats">
                <span>^ ${paper.vote_count}</span>
            </div>
        </div>
    `;
}