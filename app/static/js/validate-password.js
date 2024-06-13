const passwordInput = document.getElementById('password');

document.addEventListener('DOMContentLoaded', function () {
    passwordInput.addEventListener('input', function () {
        var password = passwordInput.value;
        if (password.length >= 8) {
            passwordInput.classList.remove('is-invalid');
            passwordInput.classList.add('is-valid');
        } else {
            passwordInput.classList.remove('is-valid');
            passwordInput.classList.add('is-invalid');
        }
    });
});