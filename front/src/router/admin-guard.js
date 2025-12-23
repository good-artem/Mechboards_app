// admin-guard.js
export async function checkAdminAccess() {
  try {
    // Получаем Telegram пользователя
    const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
    const initData = window.Telegram?.WebApp?.initData || '';
    
    console.log('🔍 Проверка администратора:', {
      hasTelegram: !!window.Telegram,
      hasWebApp: !!window.Telegram?.WebApp,
      hasInitData: !!initData,
      user: tgUser
    });
    
    let telegramId;
    
    if (tgUser) {
      telegramId = tgUser.id;
      console.log(`🔍 Telegram ID: ${telegramId}`);
    } else {
      // Для разработки без Telegram
      console.warn('⚠️ Telegram user not found, using test ID');
      telegramId = 391622124;
    }
    
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'https://psychic-adventure-wrpj64gv4jx7h5pwp-8000.app.github.dev';
    
    // Пробуем сначала простую проверку (без проверки хэша)
    try {
      const simpleResponse = await fetch(`${baseUrl}/api/admin/check_simple/${telegramId}`);
      
      if (simpleResponse.ok) {
        const adminData = await simpleResponse.json();
        console.log('✅ Простая проверка администратора:', adminData);
        
        if (adminData.is_admin) {
          return true;
        }
      }
    } catch (simpleError) {
      console.warn('⚠️ Простая проверка не удалась:', simpleError);
    }
    
    // Если есть initData, пробуем полную проверку
    if (initData && tgUser) {
      try {
        const response = await fetch(`${baseUrl}/api/admin/check/${telegramId}`, {
          headers: {
            'X-Telegram-Init-Data': initData
          }
        });
        
        if (response.ok) {
          const adminData = await response.json();
          console.log('✅ Полная проверка администратора:', adminData);
          return adminData.is_admin === true;
        } else {
          console.warn('⚠️ Полная проверка не удалась, статус:', response.status);
        }
      } catch (fullError) {
        console.error('❌ Ошибка полной проверки:', fullError);
      }
    }
    
    // Fallback: проверяем, является ли это тестовым ID администратора
    if (telegramId === 391622124) {
      console.log('🔍 Используем fallback для тестового администратора');
      return true;
    }
    
    return false;
    
  } catch (error) {
    console.error('❌ Ошибка проверки администратора:', error);
    return false;
  }
}