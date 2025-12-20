// Middleware для проверки администратора
export async function checkAdminAccess() {
  try {
    // Получаем Telegram пользователя
    const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
    if (!tgUser) {
      throw new Error('Требуется авторизация Telegram');
    }
    
    const telegramId = tgUser.id;
    
    // Проверяем статус администратора через API
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'https://verbose-space-orbit-x45v4q7q6wwf6g94-8000.app.github.dev';
    const initData = window.Telegram?.WebApp?.initData || '';
    
    const response = await fetch(`${baseUrl}/api/user/${telegramId}`, {
      headers: {
        'X-Telegram-Init-Data': initData
      }
    });
    
    if (!response.ok) {
      throw new Error('Ошибка проверки прав доступа');
    }
    
    const userData = await response.json();
    return userData.is_admin === true;
    
  } catch (error) {
    console.error('Ошибка проверки администратора:', error);
    return false;
  }
}