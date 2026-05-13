const modal = document.getElementById("modal-nav-2");
const open_modal_btn = document.getElementById("open-modal");

if (open_modal_btn && modal) {
    open_modal_btn.addEventListener("click", (e) => {
        e.stopPropagation();
        modal.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
        if (!modal.contains(e.target) && !open_modal_btn.contains(e.target)) {
            modal.classList.add("hidden");
        }
    });
}

const account = document.getElementById("account");
const open_account_btn = document.getElementById("settings-open-btn");
const close_account_modal_btn = document.getElementById("close-account-btn");

if (open_account_btn && account && close_account_modal_btn) {
    open_account_btn.addEventListener("click", (e) => {
        e.stopPropagation();
        account.classList.toggle("hidden");
    });

    close_account_modal_btn.addEventListener("click", () => {
        account.classList.add("hidden");
    });
}

const login_register_modal = document.getElementById("login-register-form");
const open_login_btn = document.getElementById("login-open-btn");
const close_login_modal_btn = document.getElementById("close-login-btn");

if (open_login_btn && login_register_modal && close_login_modal_btn) {
    open_login_btn.addEventListener("click", (e) => {
        e.stopPropagation();
        login_register_modal.classList.toggle("hidden");
    });

    close_login_modal_btn.addEventListener("click", () => {
        login_register_modal.classList.add("hidden");
    });
}

// Switching login/register
const switchRegisterBtn = document.querySelector("#register-show");
const switchLoginBtn = document.querySelector("#login-show");
const registerForm = document.querySelector("#register-form");
const loginForm = document.querySelector("#login-form");

if (switchRegisterBtn && registerForm && loginForm) {
    switchRegisterBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        registerForm.classList.toggle("hidden");
        loginForm.classList.add("hidden");
    });
}

if (switchLoginBtn && registerForm && loginForm) {
    switchLoginBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        loginForm.classList.toggle("hidden");
        registerForm.classList.add("hidden");
    });
}
