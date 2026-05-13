import { is_logged_in } from '../core/state.js';
import { navigate } from '../core/router.js';
import { papers } from '../core/api.js';
import { toast, show_view, $, set_html } from '../core/utils.js';
import { show_auth_modal } from './auth.js';
import { show_paper } from './paper.js';

export function show_editor(existing_paper = null) {
    if (!is_logged_in()) {
        show_auth_modal('login');
        navigate('/');
        return;
    }
    
    show_view('editor-view');

    document.title = existing_paper ? `editing: ${existingPaper.title} - arkhan` : 'publishing - arkhan';
    
    const form = $('paper-form');
    
    form?.reset();
    const editor = $('paper-editor');
    if (editor) editor.value = '';
    
    if (existing_paper) {
        $('paper-title').value = existing_paper.title || '';
        $('paper-tags').value = (existing_paper.tags || []).join(', ');

        if (editor) editor.value = existing_paper.content || '';
        
        const publish_checkbox = $('paper-publish');
        if (publish_checkbox) publish_checkbox.checked = existing_paper.is_published;
        
        form.dataset.edit_slug = existing_paper.slug;
    } else {
        delete form?.dataset.edit_slug;
    }
    
    show_editor_tab('write');
}

export async function edit_paper(slug) {
    try {
        const paper = await papers.get(slug);
        show_editor(paper);
    } catch (error) {
        toast(error.message, 'error');
        navigate('/');
    }
}

export function show_editor_tab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
    
    $('write-pane')?.classList.toggle('hidden', tab !== 'write');
    $('preview-pane')?.classList.toggle('hidden', tab !== 'preview');
    
    if (tab === 'preview') {
        preview_markdown();
    }
}

async function preview_markdown() {
    const content = $('paper-editor')?.value;
    const preview = $('markdown-preview');
    
    if (!content?.trim()) {
        set_html(preview, '<p style="color: var(--text-dim);">nothing to preview</p>');
        return;
    }
    
    try {
        const result = await papers.preview(content);
        set_html(preview, result.html);
    } catch (error) {
        set_html(preview, `<p style="color: var(--red);">preview error: ${error.message}</p>`);
    }
}

async function submit_paper(e) {
    e.preventDefault();
    
    const form = e.target;
    const edit_slug = form.dataset.edit_slug;
    
    const paperData = {
        title: $('paper-title')?.value.trim(),
        content: $('paper-editor')?.value,
        tags: $('paper-tags')?.value
            .split(',')
            .map(t => t.trim())
            .filter(Boolean),
        is_published: $('paper-publish')?.checked ?? true,
    };
    
    try {
        let result;
        
        if (edit_slug) {
            result = await papers.update(edit_slug, paperData);
            toast('paper updated', 'success');
        } else {
            result = await papers.create(paperData);
            toast('paper published', 'success');
        }
        
        navigate(`/paper/${result.slug}`);
    } catch (error) {
        toast(error.message, 'error');
    }
}

export function init_editor() {
    $('paper-form')?.addEventListener('submit', submit_paper);
    
    document.querySelectorAll('.editor-container .tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            show_editor_tab(btn.dataset.tab);
        });
    });
}
