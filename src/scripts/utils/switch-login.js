const switchRegisterBtn = document.querySelector("#register-show");
const switchLoginBtn = document.querySelector("#login-show")
const registerForm = document.querySelector("#register");
const loginForm  = document.querySelector("#login");

switchRegisterBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    registerForm.classList.toggle("hidden");
    loginForm.classList.add("hidden")
})
switchLoginBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    loginForm.classList.toggle("hidden");
    registerForm.classList.add("hidden")
})
