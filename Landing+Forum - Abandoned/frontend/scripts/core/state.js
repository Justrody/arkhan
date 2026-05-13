export const state = {
    user: null,
    token: null,

    current_paper: null,
    current_sort: 'recent',

    page_size: 10,
    feed: {
        papers: [],
        page: 1,
        
        has_more: true,
        is_loading: false,

        total: 0,
    },
};

export function set_user(user) {
    state.user = user;
}

export function set_token(token) {
    state.token = token;
}

export function set_current_paper(paper) {
    state.current_paper = paper;
}

export function set_sort(sort) {
    state.current_sort = sort;
}

export function reset_feed() {
    state.feed = {
        papers: [],
        page: 1,
        has_more: true,
        is_loading: false,
        total: 0,
    };
}

export function set_feed_loading(is_loading) {
    state.feed.is_loading = is_loading;
}

export function append_papers(papers, total, totalPages) {
    state.feed.papers.push(...papers);

    state.feed.total = total;
    state.feed.has_more = state.feed.page < totalPages;
    state.feed.page++;
}

export function set_pagination(page, sort = null) {
    state.current_page = page;
    if (sort) state.current_sort = sort;
}

export function is_logged_in() {
    return !!state.user && !!state.token;
}

export function is_admin() {
    return state.user?.role === 'admin';
}

export function is_owner(author_id) {
    return state.user?.id === author_id;
}

