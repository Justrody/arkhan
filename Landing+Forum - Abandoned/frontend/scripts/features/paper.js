import { state, is_logged_in, set_current_paper, is_owner } from '../core/state.js';
import { navigate, build_url } from '../core/router.js';
import { papers, votes } from '../core/api.js';
import { toast, escape_html, format_date, show_view, $, set_html } from '../core/utils.js';

export async function show_paper(slug) {
    show_view('paper-view');
    
    const container = $('paper-detail');
    set_html(container, '<div class="loading">loading</div>');
    
    try {
        const paper = await papers.get(slug);
        set_current_paper(paper);

        document.title = `${paper.title} - arkhan`;
        
        const is_author = is_owner(paper.author.id);

        const edit_url = build_url('editor-edit', { slug: paper.slug });
        const profile_url = build_url('profile', { username: paper.author.username });
        
        set_html(container, `
            <div class="paper-header">
                <div class="paper-meta">
                    <span>
                        by <a href="${profile_url}" data-profile="${paper.author.username}">@${paper.author.username}</a>
                    </span>
                    ${format_date(paper.published_at || paper.created_at)}
                </div>

                <h1>${escape_html(paper.title)}</h1>
                
                <div class="paper-tags">
                    ${(paper.tags || []).map(tag => `<span class="tag">${escape_html(tag)}</span>`).join('')}
                </div>

                <div class="paper-actions">
                    <button class="vote-btn ${paper.user_has_voted ? 'voted' : ''}" data-vote="${paper.slug}" ${!is_logged_in() ? 'disabled' : ''}>
                        ^ <span id="vote-count">${paper.vote_count}</span>
                    </button>

                    ${is_author ? `
                        <a href="${edit_url}" class="btn-secondary" data-edit="${paper.slug}">edit</a>
                    ` : ''}
                </div>
            </div>
            <div class="paper-body markdown-body">
                ${paper.content_html}
            </div>
        `);
        
        container.querySelector('[data-vote]')?.addEventListener('click', () => toggle_vote(slug));

        container.querySelector('[data-edit]')?.addEventListener('click', () => {
            e.preventDefault();
            navigate(`/edit/${slug}`);
        });
        
        container.querySelector('[data-profile]')?.addEventListener('click', (e) => {
            e.preventDefault();
            navigate(`/user/${paper.author.username}`);
        });
        
    } catch (error) {
        set_html(container, `<div style="padding: 2rem; color: var(--red);">error: ${error.message}</div>`);
    }
}

async function toggle_vote(slug) {
    if (!is_logged_in()) {
        show_auth_modal('login');
        return;
    }
    
    try {
        const paper = state.current_paper;
        
        if (paper.user_has_voted) {
            await votes.remove(slug);

            paper.user_has_voted = false;
            paper.vote_count--;
        } else {
            await votes.upvote(slug);

            paper.user_has_voted = true;
            paper.vote_count++;
        }

        const vote_btn = document.querySelector('.vote-btn');
        vote_btn?.classList.toggle('voted', paper.user_has_voted);
        set_html('vote-count', paper.vote_count.toString());

    } catch (error) {
        toast(error.message, 'error');
    }
}

