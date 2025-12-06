const modal = document.getElementById("modal-nav-2");
const open_modal_btn = document.getElementById("open-modal");

open_modal_btn.addEventListener("click", (e) => {
    e.stopPropagation();
    modal.classList.toggle("hidden");
})
document.addEventListener("click", (e) => {
    if (!modal.contains(e.target) && !open_modal_btn.contains(e.target)) {
        modal.classList.add("hidden");
    }
});

const account = document.getElementById("account");
const open_account_btn = document.getElementById("settings-open-btn");
const close_account_modal_btn = document.getElementById("close-account-btn");

open_account_btn.addEventListener("click", (e) => {
    e.stopPropagation();
    account.classList.toggle("hidden");
})
 close_account_modal_btn .addEventListener("click", () => {
    account.classList.add("hidden");
}
);


const open_post_upload_modal = document.getElementById("post-content");
const post_modal = document.getElementById("upload-post-modal");
const close_upload_modal_btn = document.getElementById("close-upload-btn");

open_post_upload_modal.addEventListener("click", (e) => {
    e.stopPropagation();
    post_modal.classList.toggle("hidden");
})
close_upload_modal_btn.addEventListener("click", () => {
    post_modal.classList.add("hidden");
}
);

const open_markdown = document.querySelector(".paper");
const markdown_file = document.getElementById("markdown-body");
const close_markdown_btn = document.getElementById("close-paper");

open_markdown.addEventListener("click", (e) => {
    e.stopPropagation();
    markdown_file.classList.remove("hidden");
})
close_markdown_btn.addEventListener("click", () => {
    markdown_file.classList.add("hidden");
}
);

