<template>
  <v-container class="admin-container" fluid>
    <v-row>
      <v-col cols="12">
        <v-card class="admin-header pa-4" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon size="28" color="primary" class="mr-2">mdi-shield-account</v-icon>
            <span class="text-h5 font-weight-bold">Админ панель</span>
            <v-spacer></v-spacer>
            <v-avatar size="40" class="ml-3">
              <v-img :src="adminAvatar" alt="Admin avatar" />
            </v-avatar>
          </v-card-title>
          <v-card-subtitle>
            Добро пожаловать, {{ adminName }}! Здесь вы можете управлять магазином и заказами.
          </v-card-subtitle>
        </v-card>
        
        <!-- Быстрые действия -->
        <v-row class="mt-4">
          <v-col cols="6" sm="3" v-for="(action, index) in quickActions" :key="index">
            <v-card 
              class="quick-action-card d-flex align-center justify-center" 
              elevation="1"
              @click="navigateTo(action.route)"
              hover
            >
              <div class="text-center pa-2">
                <v-icon :color="action.color" size="36">{{ action.icon }}</v-icon>
                <div class="text-subtitle-2 mt-1 font-weight-medium">{{ action.title }}</div>
              </div>
            </v-card>
          </v-col>
        </v-row>
        
        <!-- Основной контент -->
        <v-tabs v-model="activeTab" class="mt-4" color="primary">
          <v-tab value="orders">Заказы</v-tab>
          <v-tab value="products">Товары</v-tab>
          <v-tab value="services">Услуги</v-tab>
          <v-tab value="stats">Статистика</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <!-- Вкладка Заказов -->
          <v-window-item value="orders">
            <div class="orders-section">
              <v-card class="admin-card pa-3" elevation="1">
                <v-card-title class="d-flex justify-space-between align-center">
                  <span class="font-weight-medium">Активные заказы</span>
                  <v-btn size="small" variant="tonal" @click="refreshOrders">
                    <v-icon size="18" class="mr-1">mdi-refresh</v-icon>
                    Обновить
                  </v-btn>
                </v-card-title>
                <v-card-text>
                  <v-data-table
                    :items="orders"
                    :headers="orderHeaders"
                    :loading="loadingOrders"
                    loading-text="Загрузка заказов..."
                    no-data-text="Нет активных заказов"
                    class="admin-table"
                    hide-default-footer
                  >
                    <template v-slot:item.status="{ item }">
                      <v-chip 
                        :color="getStatusColor(item.status)" 
                        size="small"
                        variant="tonal"
                      >
                        {{ getStatusText(item.status) }}
                      </v-chip>
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-btn 
                        size="small" 
                        variant="tonal" 
                        color="primary" 
                        @click="viewOrderDetails(item)"
                      >
                        Детали
                      </v-btn>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </div>
          </v-window-item>
          
          <!-- Вкладка Товаров -->
          <v-window-item value="products">
            <div class="products-section">
              <v-card class="admin-card pa-3" elevation="1">
                <v-card-title class="d-flex justify-space-between align-center">
                  <span class="font-weight-medium">Каталог товаров</span>
                  <v-btn size="small" color="primary" @click="openAddProductDialog">
                    <v-icon size="18" class="mr-1">mdi-plus</v-icon>
                    Добавить товар
                  </v-btn>
                </v-card-title>
                <v-card-text>
                  <v-data-table
                    :items="products"
                    :headers="productHeaders"
                    :loading="loadingProducts"
                    loading-text="Загрузка товаров..."
                    no-data-text="Нет товаров в каталоге"
                    class="admin-table"
                    :items-per-page="10"
                  >
                    <template v-slot:item.images="{ item }">
                      <v-avatar size="40" class="mr-2">
                        <v-img 
                          :src="getProductImage(item)" 
                          alt="Product image"
                          cover
                        ></v-img>
                      </v-avatar>
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-btn size="small" variant="tonal" color="primary" class="mr-1">
                        <v-icon size="18">mdi-pencil</v-icon>
                      </v-btn>
                      <v-btn size="small" variant="tonal" color="error">
                        <v-icon size="18">mdi-delete</v-icon>
                      </v-btn>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </div>
          </v-window-item>
          
          <!-- Вкладка Услуг -->
          <v-window-item value="services">
            <div class="services-section">
              <v-card class="admin-card pa-3" elevation="1">
                <v-card-title class="d-flex justify-space-between align-center">
                  <span class="font-weight-medium">Услуги</span>
                  <v-btn size="small" color="primary" @click="openAddServiceDialog">
                    <v-icon size="18" class="mr-1">mdi-plus</v-icon>
                    Добавить услугу
                  </v-btn>
                </v-card-title>
                <v-card-text>
                  <v-list lines="two" class="admin-list">
                    <v-list-item
                      v-for="service in services"
                      :key="service.service_id"
                      class="service-item mb-1"
                    >
                      <template v-slot:prepend>
                        <v-avatar rounded="lg" size="40" class="service-icon mr-3">
                          <v-icon size="20" color="white">mdi-wrench</v-icon>
                        </v-avatar>
                      </template>
                      
                      <div class="service-content">
                        <div class="service-name font-weight-medium">{{ service.name }}</div>
                        <div class="service-description text-caption text-grey">{{ service.description }}</div>
                        <div class="service-price text-body-2 font-weight-medium primary--text">
                          {{ formatPrice(service.price) }}
                        </div>
                      </div>
                      
                      <template v-slot:append>
                        <div class="d-flex">
                          <v-btn size="small" variant="tonal" color="primary" class="mr-1">
                            <v-icon size="18">mdi-pencil</v-icon>
                          </v-btn>
                          <v-btn size="small" variant="tonal" color="error">
                            <v-icon size="18">mdi-delete</v-icon>
                          </v-btn>
                        </div>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </div>
          </v-window-item>
          
          <!-- Вкладка Статистики -->
          <v-window-item value="stats">
            <div class="stats-section">
              <v-row>
                <v-col cols="12" md="6" lg="3" v-for="(stat, index) in stats" :key="index">
                  <v-card class="stat-card pa-3" elevation="1">
                    <div class="d-flex align-center">
                      <v-avatar size="40" class="mr-3" :color="stat.color" variant="tonal">
                        <v-icon size="24" dark>{{ stat.icon }}</v-icon>
                      </v-avatar>
                      <div>
                        <div class="text-body-2 text-grey">{{ stat.label }}</div>
                        <div class="text-h6 font-weight-bold mt-1">{{ stat.value }}</div>
                      </div>
                    </div>
                  </v-card>
                </v-col>
              </v-row>
              
              <v-card class="mt-4 admin-card pa-3" elevation="1">
                <v-card-title class="font-weight-medium">Последние заказы</v-card-title>
                <v-card-text>
                  <v-timeline density="compact" side="end">
                    <v-timeline-item
                      v-for="order in recentOrders"
                      :key="order.order_id"
                      size="small"
                      :dot-color="getStatusColor(order.status)"
                    >
                      <div>
                        <div class="font-weight-medium">Заказ #{{ order.order_number }}</div>
                        <div class="text-caption text-grey mt-1">
                          {{ new Date(order.created_at).toLocaleDateString('ru-RU') }} • {{ formatPrice(order.total_amount) }}
                        </div>
                        <v-chip 
                          :color="getStatusColor(order.status)" 
                          size="small"
                          class="mt-2"
                          variant="tonal"
                        >
                          {{ getStatusText(order.status) }}
                        </v-chip>
                      </div>
                    </v-timeline-item>
                  </v-timeline>
                </v-card-text>
              </v-card>
            </div>
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <!-- Диалог деталей заказа -->
    <v-dialog v-model="orderDetailsDialog" max-width="600">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Детали заказа #{{ selectedOrder?.order_number }}</span>
          <v-btn icon @click="orderDetailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text v-if="selectedOrder">
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Статус:</div>
            <v-select
              v-model="selectedOrder.status"
              :items="statusOptions"
              item-title="text"
              item-value="value"
              variant="outlined"
              density="compact"
            ></v-select>
          </div>
          
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Клиент:</div>
            <div>{{ selectedOrder.user?.name || 'Не указано' }}</div>
            <div class="text-caption">{{ selectedOrder.user?.phone || 'Нет телефона' }}</div>
          </div>
          
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Товары:</div>
            <v-list density="compact">
              <v-list-item
                v-for="(item, index) in selectedOrder.order_items"
                :key="index"
              >
                <v-list-item-title>{{ item.product?.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ item.quantity }} × {{ formatPrice(item.unit_price) }} = {{ formatPrice(item.total_price) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </div>
          
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Итого:</div>
            <div class="text-h6 primary--text font-weight-bold">{{ formatPrice(selectedOrder.total_amount) }}</div>
          </div>
          
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Доставка:</div>
            <div>{{ selectedOrder.shipping_method || 'Не указана' }}</div>
            <div class="text-caption">{{ selectedOrder.shipping_address || 'Нет адреса' }}</div>
          </div>
          
          <div v-if="selectedOrder.customer_notes">
            <div class="text-subtitle-1 font-weight-medium mb-1">Комментарий:</div>
            <div class="text-body-2">{{ selectedOrder.customer_notes }}</div>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="orderDetailsDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveOrderStatus">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Диалог добавления товара -->
    <v-dialog v-model="addProductDialog" max-width="500">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Добавить новый товар</span>
          <v-btn icon @click="addProductDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newProduct.name"
            label="Название товара"
            variant="outlined"
            density="compact"
            required
          ></v-text-field>
          <v-textarea
            v-model="newProduct.description"
            label="Описание"
            variant="outlined"
            density="compact"
            rows="2"
          ></v-textarea>
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="newProduct.price"
                label="Цена (BYN)"
                type="number"
                variant="outlined"
                density="compact"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="newProduct.stock_quantity"
                label="Количество на складе"
                type="number"
                variant="outlined"
                density="compact"
                required
              ></v-text-field>
            </v-col>
          </v-row>
          <v-select
            v-model="newProduct.category_id"
            :items="categories"
            item-title="name"
            item-value="category_id"
            label="Категория"
            variant="outlined"
            density="compact"
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="addProductDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="addProduct">Добавить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Диалог добавления услуги -->
    <v-dialog v-model="addServiceDialog" max-width="500">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Добавить новую услугу</span>
          <v-btn icon @click="addServiceDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newService.name"
            label="Название услуги"
            variant="outlined"
            density="compact"
            required
          ></v-text-field>
          <v-textarea
            v-model="newService.description"
            label="Описание"
            variant="outlined"
            density="compact"
            rows="2"
            required
          ></v-textarea>
          <v-text-field
            v-model="newService.price"
            label="Цена (BYN)"
            type="number"
            variant="outlined"
            density="compact"
            required
          ></v-text-field>
          <v-text-field
            v-model="newService.duration"
            label="Время выполнения"
            placeholder="Например: 1-3 дня"
            variant="outlined"
            density="compact"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="addServiceDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="addService">Добавить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { useApi } from '@/composables/useApi'
import '@/assets/styles/components/admin-view.css'

export default {
  name: 'AdminView',
  data() {
    return {
      activeTab: 'orders',
      loadingOrders: false,
      loadingProducts: false,
      orderDetailsDialog: false,
      addProductDialog: false,
      addServiceDialog: false,
      orders: [],
      products: [],
      services: [],
      categories: [],
      selectedOrder: null,
      newProduct: {
        name: '',
        description: '',
        price: 0,
        stock_quantity: 0,
        category_id: null,
        is_available: true
      },
      newService: {
        name: '',
        description: '',
        price: 0,
        duration: '',
        is_active: true
      },
      stats: [
        { label: 'Всего заказов', value: '0', icon: 'mdi-package-variant', color: 'primary' },
        { label: 'Активных заказов', value: '0', icon: 'mdi-clock-outline', color: 'warning' },
        { label: 'Товаров в каталоге', value: '0', icon: 'mdi-view-grid', color: 'success' },
        { label: 'Доступных услуг', value: '0', icon: 'mdi-tools', color: 'info' }
      ],
      recentOrders: [],
      quickActions: [
        { title: 'Новые заказы', icon: 'mdi-bell-ring', color: 'primary', route: 'orders' },
        { title: 'Каталог', icon: 'mdi-view-grid', color: 'success', route: 'products' },
        { title: 'Услуги', icon: 'mdi-tools', color: 'info', route: 'services' },
        { title: 'Статистика', icon: 'mdi-chart-bar', color: 'warning', route: 'stats' }
      ],
      orderHeaders: [
        { title: '№', value: 'order_number', width: '100' },
        { title: 'Клиент', value: 'user.name', width: '150' },
        { title: 'Сумма', value: 'total_amount', width: '100' },
        { title: 'Статус', value: 'status', width: '120' },
        { title: 'Дата', value: 'created_at', width: '150' },
        { title: 'Действия', value: 'actions', width: '100' }
      ],
      productHeaders: [
        { title: 'Изображение', value: 'images', width: '80' },
        { title: 'Название', value: 'name' },
        { title: 'Цена', value: 'price', width: '100' },
        { title: 'В наличии', value: 'stock_quantity', width: '100' },
        { title: 'Категория', value: 'category.name', width: '120' },
        { title: 'Действия', value: 'actions', width: '120' }
      ],
      statusOptions: [
        { text: 'Создан', value: 'Создан' },
        { text: 'Оплачен', value: 'Оплачен' },
        { text: 'Подтвержден', value: 'Подтвержден' },
        { text: 'Отправлен', value: 'Отправлен' },
        { text: 'Доставлен', value: 'Доставлен' },
        { text: 'Отменен', value: 'Отменен' }
      ]
    }
  },
  computed: {
    adminName() {
      return window.Telegram?.WebApp?.initDataUnsafe?.user?.first_name || 'Администратор';
    },
    adminAvatar() {
      const user = window.Telegram?.WebApp?.initDataUnsafe?.user;
      return user?.photo_url || 'https://via.placeholder.com/40x40/667eea/ffffff?text=A';
    }
  },
  async mounted() {
    await this.fetchAllData();
  },
  methods: {
    formatPrice(price) {
      return new Intl.NumberFormat('ru-BY', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(price) + ' р.';
    },
    
    getProductImage(product) {
      if (product.images && product.images.length > 0) {
        try {
          const images = Array.isArray(product.images) ? product.images : JSON.parse(product.images);
          return images[0];
        } catch (e) {
          return product.images;
        }
      }
      return 'https://via.placeholder.com/40x40/667eea/ffffff?text=No+Image';
    },
    
    getStatusColor(status) {
      const colors = {
        'Создан': 'grey',
        'Оплачен': 'warning',
        'Подтвержден': 'info',
        'Отправлен': 'success',
        'Доставлен': 'primary',
        'Отменен': 'error'
      };
      return colors[status] || 'grey';
    },
    
    getStatusText(status) {
      return status;
    },
    
    async fetchAllData() {
      await Promise.all([
        this.fetchOrders(),
        this.fetchProducts(),
        this.fetchServices(),
        this.fetchCategories(),
        this.fetchStats()
      ]);
    },
    
    async fetchOrders() {
      this.loadingOrders = true;
      try {
        const { get } = useApi();
        const response = await get('/api/orders');
        this.orders = response.orders || [];
        this.recentOrders = response.recent_orders || [];
        
        // Обновляем статистику
        this.stats[1].value = this.orders.length.toString();
      } catch (error) {
        console.error('❌ Ошибка загрузки заказов:', error);
        this.orders = [];
        this.recentOrders = [];
      } finally {
        this.loadingOrders = false;
      }
    },
    
    async fetchProducts() {
      this.loadingProducts = true;
      try {
        const { get } = useApi();
        const response = await get('/api/products');
        this.products = response || [];
        
        // Обновляем статистику
        this.stats[2].value = this.products.length.toString();
      } catch (error) {
        console.error('❌ Ошибка загрузки товаров:', error);
        this.products = [];
      } finally {
        this.loadingProducts = false;
      }
    },
    
    async fetchServices() {
      try {
        const { get } = useApi();
        const response = await get('/api/services');
        this.services = response || [];
        
        // Обновляем статистику
        this.stats[3].value = this.services.length.toString();
      } catch (error) {
        console.error('❌ Ошибка загрузки услуг:', error);
        this.services = [];
      }
    },
    
    async fetchCategories() {
      try {
        const { get } = useApi();
        const response = await get('/api/categories');
        this.categories = response || [];
      } catch (error) {
        console.error('❌ Ошибка загрузки категорий:', error);
        this.categories = [];
      }
    },
    
    async fetchStats() {
      try {
        const { get } = useApi();
        const response = await get('/api/admin/stats');
        if (response) {
          this.stats[0].value = response.total_orders.toString();
        }
      } catch (error) {
        console.error('❌ Ошибка загрузки статистики:', error);
      }
    },
    
    async refreshOrders() {
      await this.fetchOrders();
    },
    
    viewOrderDetails(order) {
      this.selectedOrder = { ...order };
      this.orderDetailsDialog = true;
    },
    
    async saveOrderStatus() {
      try {
        const { put } = useApi();
        await put(`/api/orders/${this.selectedOrder.order_id}`, {
          status: this.selectedOrder.status
        });
        this.$root.$emit('show-message', 'Статус заказа обновлен', 'success');
        this.orderDetailsDialog = false;
        await this.fetchOrders();
      } catch (error) {
        console.error('❌ Ошибка обновления статуса:', error);
        this.$root.$emit('show-message', 'Ошибка обновления статуса', 'error');
      }
    },
    
    openAddProductDialog() {
      this.newProduct = {
        name: '',
        description: '',
        price: 0,
        stock_quantity: 0,
        category_id: this.categories[0]?.category_id || null,
        is_available: true
      };
      this.addProductDialog = true;
    },
    
    async addProduct() {
      try {
        const { post } = useApi();
        await post('/api/admin/products', this.newProduct);
        this.$root.$emit('show-message', 'Товар добавлен', 'success');
        this.addProductDialog = false;
        await this.fetchProducts();
      } catch (error) {
        console.error('❌ Ошибка добавления товара:', error);
        this.$root.$emit('show-message', 'Ошибка добавления товара', 'error');
      }
    },
    
    openAddServiceDialog() {
      this.newService = {
        name: '',
        description: '',
        price: 0,
        duration: '',
        is_active: true
      };
      this.addServiceDialog = true;
    },
    
    async addService() {
      try {
        const { post } = useApi();
        await post('/api/admin/services', this.newService);
        this.$root.$emit('show-message', 'Услуга добавлена', 'success');
        this.addServiceDialog = false;
        await this.fetchServices();
      } catch (error) {
        console.error('❌ Ошибка добавления услуги:', error);
        this.$root.$emit('show-message', 'Ошибка добавления услуги', 'error');
      }
    },
    
    navigateTo(route) {
      this.activeTab = route;
    }
  }
}
</script>

<style scoped>
.admin-container {
  padding: 0 8px;
}

.admin-header {
  border-radius: 16px;
}

.quick-action-card {
  border-radius: 12px;
  height: 100px;
  cursor: pointer;
  transition: transform 0.2s ease;
  background-color: var(--tg-theme-bg-color, #ffffff);
  border: 1px solid var(--tg-theme-divider-color, rgba(0,0,0,0.12));
}

.quick-action-card:hover {
  transform: translateY(-2px);
}

.admin-card {
  border-radius: 12px;
}

.admin-table :deep(th), .admin-table :deep(td) {
  padding: 8px 4px;
}

.stat-card {
  border-radius: 12px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.service-item {
  border-radius: 12px;
  background-color: var(--tg-theme-bg-color, #ffffff);
  border: 1px solid var(--tg-theme-divider-color, rgba(0,0,0,0.12));
}

.service-icon {
  background-color: var(--tg-theme-button-color, #2481cc);
}

.service-content {
  color: var(--tg-theme-text-color, #212121);
}

.service-name {
  line-height: 1.3;
}

.service-description {
  line-height: 1.4;
}
</style>