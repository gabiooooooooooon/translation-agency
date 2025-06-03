// Функция для работы с API
export async function apiRequest(endpoint, method = 'GET', data = null) {
  const url = `/api/${endpoint}`;
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    }
  };

  if (localStorage.getItem('access_token')) {
    options.headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
  }

  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}

// Функция для получения CSRF-токена
export function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}