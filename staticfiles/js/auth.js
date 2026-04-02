// Funções de autenticação compartilhadas
const API_BASE = '/api';

function getAuthToken() {
  return localStorage.getItem('access_token');
}

async function checkAuth() {
  try {
    const token = getAuthToken();
    if (!token) {
      showAuthButtons();
      return false;
    }

    const response = await fetch(`${API_BASE}/auth/me/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      showUserMenu(data.user);
      return true;
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      showAuthButtons();
      return false;
    }
  } catch (error) {
    showAuthButtons();
    return false;
  }
}

function showUserMenu(user) {
  const authButtons = document.getElementById('auth-buttons');
  const userMenu = document.getElementById('user-menu');
  
  if (authButtons) authButtons.classList.add('hidden');
  if (userMenu) userMenu.classList.remove('hidden');
}

function showAuthButtons() {
  const authButtons = document.getElementById('auth-buttons');
  const userMenu = document.getElementById('user-menu');
  
  if (authButtons) authButtons.classList.remove('hidden');
  if (userMenu) userMenu.classList.add('hidden');
}

// Logout
document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          await fetch(`${API_BASE}/auth/logout/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
          });
        }
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
      } catch (error) {
        console.error('Erro ao fazer logout:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
      }
    });
  }
});
