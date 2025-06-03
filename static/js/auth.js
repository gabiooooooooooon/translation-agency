// auth.js - единый модуль аутентификации
document.addEventListener('DOMContentLoaded', function() {
    // Общие функции
    function getCookie(name) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [cookieName, cookieValue] = cookie.trim().split('=');
            if (cookieName === name) return decodeURIComponent(cookieValue);
        }
        return null;
    }

    function showError(element, message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        errorElement.style.color = 'red';
        element.after(errorElement);
        setTimeout(() => errorElement.remove(), 3000);
    }

    // 1. Обработка входа
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/auth/token/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        email: loginForm.email.value,
                        password: loginForm.password.value
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('access_token', data.auth_token);
                    window.location.href = '/';
                } else {
                    showError(loginForm, data.non_field_errors?.[0] || 'Ошибка входа');
                }
            } catch (error) {
                console.error('Login error:', error);
                showError(loginForm, 'Ошибка соединения');
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    // 2. Обработка регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            if (registerForm.password.value !== registerForm.confirmPassword.value) {
                showError(registerForm, 'Пароли не совпадают');
                return;
            }

            const submitBtn = registerForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/auth/users/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        email: registerForm.email.value,
                        password: registerForm.password.value,
                        role: 'client'
                    })
                });

                if (response.ok) {
                    alert('Регистрация успешна! Войдите в систему.');
                    window.location.href = '/login/';
                } else {
                    const errors = await response.json();
                    const errorMessage = Object.values(errors).flat().join(', ');
                    showError(registerForm, errorMessage || 'Ошибка регистрации');
                }
            } catch (error) {
                console.error('Register error:', error);
                showError(registerForm, 'Ошибка соединения');
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    // 3. Восстановление пароля
    const recoveryForm = document.getElementById('recoveryForm');
    if (recoveryForm) {
        recoveryForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = recoveryForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/auth/users/reset_password/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        email: recoveryForm.email.value
                    })
                });

                if (response.ok) {
                    alert('Инструкции отправлены на ваш email!');
                } else {
                    showError(recoveryForm, 'Email не найден');
                }
            } catch (error) {
                console.error('Recovery error:', error);
                showError(recoveryForm, 'Ошибка соединения');
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    // 4. Выход из системы
    document.querySelectorAll('.logout-link').forEach(link => {
        link.addEventListener('click', async function(e) {
            e.preventDefault();

            try {
                const response = await fetch('/auth/token/logout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Authorization': `Token ${localStorage.getItem('access_token')}`
                    }
                });

                // Всегда очищаем данные, даже если сервер не ответил
                localStorage.removeItem('access_token');
                document.cookie.split(';').forEach(cookie => {
                    const [name] = cookie.trim().split('=');
                    document.cookie = `${name}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
                });

                window.location.href = '/?logout=' + Date.now();
            } catch (error) {
                console.error('Logout error:', error);
                window.location.reload();
            }
        });
    });

    // Проверка аутентификации при загрузке
    if (localStorage.getItem('access_token')) {
        console.log('User is authenticated');
    }
});