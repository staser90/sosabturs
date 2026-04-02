// Funções de autenticação compartilhadas

async function checkAuth() {
  try {
    const response = await fetch('/api/auth/me', {
      credentials: 'include'
    });

    if (response.ok) {
      const data = await response.json();
      showUserMenu(data.user);
      return true;
    } else {
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
        await fetch('/api/auth/logout', {
          method: 'POST',
          credentials: 'include'
        });
        window.location.href = '/';
      } catch (error) {
        console.error('Erro ao fazer logout:', error);
        window.location.href = '/';
      }
    });
  }
});
