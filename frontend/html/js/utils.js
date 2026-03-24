const API = 'https://v-meal.onrender.com';

function showToast(message, type = 'info') {
    const existing = document.querySelector('.vmeal-toast');
    if (existing) existing.remove();

    const colors = { success: '#60B246', error: '#D83C3C', info: '#FC8019' };
    const toast = document.createElement('div');
    toast.className = 'vmeal-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed; bottom: 24px; right: 24px;
        background: ${colors[type] || colors.info}; color: white;
        padding: 12px 20px; border-radius: 10px;
        font-size: 14px; font-weight: 600;
        z-index: 99999; opacity: 1;
        transition: opacity 0.4s ease;
        max-width: 320px; box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        font-family: 'Inter', sans-serif;
    `;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; }, 2600);
    setTimeout(() => { toast.remove(); }, 3000);
}

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

function requireRole(...roles) {
    const role = localStorage.getItem('user_role');
    if (!role || !roles.includes(role)) {
        window.location.href = 'login.html';
    }
}
