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
        
        <!-- Вкладки -->
        <v-tabs v-model="activeTab" class="mt-4" color="primary">
          <v-tab value="orders">Заказы товаров</v-tab>
          <v-tab value="service_orders">Заказы услуг</v-tab>
          <v-tab value="products">Товары</v-tab>
          <v-tab value="services">Услуги</v-tab>
          <v-tab value="users">Пользователи</v-tab>
          <v-tab value="support">Поддержка</v-tab>
          <v-tab value="stats">Статистика</v-tab>
        </v-tabs>
        
        <!-- Окно вкладок -->
        <v-window v-model="activeTab" class="mt-4" :touch="false">
          <!-- Вкладка Заказов товаров -->
          <v-window-item value="orders">
            <v-card class="admin-card pa-3" elevation="1">
              <v-card-title class="d-flex justify-space-between align-center">
                <span class="font-weight-medium">Заказы товаров</span>
                <div>
                  <v-select
                    v-model="orderFilter"
                    :items="statusOptions"
                    label="Фильтр по статусу"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="filter-select mr-2"
                    style="max-width: 200px;"
                    @update:model-value="fetchOrders"
                  >
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props">
                        <v-list-item-title>
                          {{ item === null ? 'Все статусы' : item }}
                        </v-list-item-title>
                      </v-list-item>
                    </template>
                    <template v-slot:selection="{ item }">
                      {{ item === null ? 'Все статусы' : item }}
                    </template>
                  </v-select>
                  <v-btn size="small" variant="tonal" @click="fetchOrders">
                    <v-icon size="18" class="mr-1">mdi-refresh</v-icon>
                    Обновить
                  </v-btn>
                </div>
              </v-card-title>
              <v-card-text>
                <v-data-table
                  :items="orders"
                  :headers="orderHeaders"
                  :loading="loadingOrders"
                  loading-text="Загрузка заказов..."
                  no-data-text="Нет заказов"
                  class="admin-table"
                  hide-default-footer
                >
                  <template v-slot:item.status="{ item }">
                    <v-chip 
                      :color="getStatusColor(item.status)" 
                      size="small"
                      variant="tonal"
                    >
                      {{ item.status }}
                    </v-chip>
                  </template>
                  <template v-slot:item.total_amount="{ item }">
                    {{ formatPrice(item.total_amount) }}
                  </template>
                  <template v-slot:item.user="{ item }">
                    <div v-if="item.user">
                      <div>{{ item.user.name || 'Без имени' }}</div>
                      <div class="text-caption">@{{ item.user.username || 'без username' }}</div>
                      <div class="text-caption">ID: {{ item.user.telegram_id }}</div>
                    </div>
                    <div v-else>Пользователь не найден</div>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn 
                      size="small" 
                      variant="tonal" 
                      color="primary" 
                      @click="viewOrderDetails(item)"
                      class="mr-1"
                    >
                      <v-icon size="18">mdi-eye</v-icon>
                    </v-btn>
                    <v-btn 
                      size="small" 
                      variant="tonal" 
                      color="success" 
                      @click="updateOrderStatus(item, 'Доставлен')"
                      v-if="item.status !== 'Доставлен' && item.status !== 'Отменен'"
                    >
                      <v-icon size="18">mdi-check</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <!-- Вкладка Заказов услуг -->
          <v-window-item value="service_orders">
            <v-card class="admin-card pa-3" elevation="1">
              <v-card-title class="d-flex justify-space-between align-center">
                <span class="font-weight-medium">Заказы услуг</span>
                <div>
                  <v-select
                    v-model="serviceOrderFilter"
                    :items="statusOptions"
                    label="Фильтр по статусу"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="filter-select mr-2"
                    style="max-width: 200px;"
                    @update:model-value="fetchServiceOrders"
                  ></v-select>
                  <v-btn size="small" variant="tonal" @click="fetchServiceOrders">
                    <v-icon size="18" class="mr-1">mdi-refresh</v-icon>
                    Обновить
                  </v-btn>
                </div>
              </v-card-title>
              <v-card-text>
                <v-data-table
                  :items="serviceOrders"
                  :headers="serviceOrderHeaders"
                  :loading="loadingServiceOrders"
                  loading-text="Загрузка заказов услуг..."
                  no-data-text="Нет заказов на услуги"
                  class="admin-table"
                  hide-default-footer
                >
                  <template v-slot:item.status="{ item }">
                    <v-chip 
                      :color="getStatusColor(item.status)" 
                      size="small"
                      variant="tonal"
                    >
                      {{ item.status }}
                    </v-chip>
                  </template>
                  <template v-slot:item.price="{ item }">
                    {{ formatPrice(item.price) }}
                  </template>
                  <template v-slot:item.user="{ item }">
                    <div v-if="item.user">
                      <div>{{ item.user.name || 'Без имени' }}</div>
                      <div class="text-caption">ID: {{ item.user.telegram_id }}</div>
                    </div>
                    <div v-else>Пользователь не найден</div>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn 
                      size="small" 
                      variant="tonal" 
                      color="success" 
                      @click="updateServiceOrderStatus(item, 'Доставлен')"
                      v-if="item.status !== 'Доставлен' && item.status !== 'Отменен'"
                    >
                      <v-icon size="18">mdi-check</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <!-- Вкладка Товаров -->
          <v-window-item value="products">
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
                  <template v-slot:item.price="{ item }">
                    {{ formatPrice(item.price) }}
                  </template>
                  <template v-slot:item.stock_quantity="{ item }">
                    <v-chip 
                      :color="item.stock_quantity > 0 ? 'success' : 'error'" 
                      size="small"
                      variant="tonal"
                    >
                      {{ item.stock_quantity }} шт.
                    </v-chip>
                  </template>
                  <template v-slot:item.is_available="{ item }">
                    <v-switch
                      v-model="item.is_available"
                      inset
                      hide-details
                      color="success"
                      @change="updateProductAvailability(item)"
                    ></v-switch>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn size="small" variant="tonal" color="primary" class="mr-1" @click="editProduct(item)">
                      <v-icon size="18">mdi-pencil</v-icon>
                    </v-btn>
                    <v-btn size="small" variant="tonal" color="error" @click="deleteProduct(item)">
                      <v-icon size="18">mdi-delete</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <!-- Вкладка Услуг -->
          <v-window-item value="services">
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
                      <div class="d-flex align-center mt-1">
                        <div class="service-price text-body-2 font-weight-medium primary--text mr-3">
                          {{ formatPrice(service.price) }}
                        </div>
                        <v-chip v-if="service.duration" size="small" variant="tonal">
                          {{ service.duration }}
                        </v-chip>
                      </div>
                    </div>
                    
                    <template v-slot:append>
                      <div class="d-flex">
                        <v-switch
                          v-model="service.is_active"
                          inset
                          hide-details
                          color="success"
                          @change="updateServiceActivity(service)"
                        ></v-switch>
                        <v-btn size="small" variant="tonal" color="primary" class="mr-1" @click="editService(service)">
                          <v-icon size="18">mdi-pencil</v-icon>
                        </v-btn>
                        <v-btn size="small" variant="tonal" color="error" @click="deleteService(service)">
                          <v-icon size="18">mdi-delete</v-icon>
                        </v-btn>
                      </div>
                    </template>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <!-- Вкладка Пользователей -->
          <v-window-item value="users">
            <v-card class="admin-card pa-3" elevation="1">
              <v-card-title class="d-flex justify-space-between align-center">
                <span class="font-weight-medium">Пользователи</span>
                <div>
                  <v-text-field
                    v-model="userSearch"
                    placeholder="Поиск пользователей..."
                    variant="outlined"
                    density="compact"
                    hide-details
                    prepend-inner-icon="mdi-magnify"
                    clearable
                    @input="fetchUsers"
                    @click:clear="fetchUsers"
                    style="max-width: 300px;"
                    class="mr-2"
                  ></v-text-field>
                  <v-btn size="small" variant="tonal" @click="fetchUsers">
                    <v-icon size="18" class="mr-1">mdi-refresh</v-icon>
                    Обновить
                  </v-btn>
                </div>
              </v-card-title>
              <v-card-text>
                <v-data-table
                  :items="users"
                  :headers="userHeaders"
                  :loading="loadingUsers"
                  loading-text="Загрузка пользователей..."
                  no-data-text="Нет пользователей"
                  class="admin-table"
                  :items-per-page="10"
                >
                  <template v-slot:item.is_active="{ item }">
                    <v-switch
                      v-model="item.is_active"
                      inset
                      hide-details
                      color="success"
                      @change="updateUserActivity(item)"
                    ></v-switch>
                  </template>
                  <template v-slot:item.is_admin="{ item }">
                    <v-switch
                      v-model="item.is_admin"
                      inset
                      hide-details
                      color="primary"
                      @change="updateUserAdminStatus(item)"
                    ></v-switch>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn 
                      size="small" 
                      variant="tonal" 
                      color="primary" 
                      @click="sendMessageToUser(item)"
                      class="mr-1"
                    >
                      <v-icon size="18">mdi-message</v-icon>
                    </v-btn>
                    <v-btn 
                      size="small" 
                      variant="tonal" 
                      color="info" 
                      @click="viewUserOrders(item)"
                    >
                      <v-icon size="18">mdi-shopping</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <!-- Вкладка Поддержки -->
          <v-window-item value="support">
            <v-card class="admin-card pa-3" elevation="1">
              <v-card-title class="d-flex justify-space-between align-center">
                <span class="font-weight-medium">Поддержка</span>
                <div>
                  <v-select
                    v-model="supportFilter"
                    :items="supportStatuses"
                    label="Фильтр по статусу"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="filter-select mr-2"
                    style="max-width: 200px;"
                    @update:model-value="fetchSupportTickets"
                  ></v-select>
                  <v-btn size="small" variant="tonal" @click="fetchSupportTickets">
                    <v-icon size="18" class="mr-1">mdi-refresh</v-icon>
                    Обновить
                  </v-btn>
                </div>
              </v-card-title>
              <v-card-text>
                <v-data-table
                  :items="supportTickets"
                  :headers="supportHeaders"
                  :loading="loadingSupport"
                  loading-text="Загрузка тикетов..."
                  no-data-text="Нет тикетов поддержки"
                  class="admin-table"
                  hide-default-footer
                >
                  <template v-slot:item.status="{ item }">
                    <v-chip 
                      :color="getSupportStatusColor(item.status)" 
                      size="small"
                      variant="tonal"
                    >
                      {{ getSupportStatusText(item.status) }}
                    </v-chip>
                  </template>
                  <template v-slot:item.user="{ item }">
                    <div v-if="item.user">
                      <div>{{ item.user.name || 'Без имени' }}</div>
                      <div class="text-caption">@{{ item.user.username || 'без username' }}</div>
                      <div class="text-caption">ID: {{ item.user.telegram_id }}</div>
                    </div>
                    <div v-else>Пользователь не найден</div>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn 
                      size="small" 
                      variant="tonal" 
                      color="primary" 
                      @click="openTelegramChat(item.user.telegram_id)"
                      class="mr-1"
                    >
                      <v-icon size="18">mdi-telegram</v-icon>
                    </v-btn>
                    <v-btn 
                      size="small" 
                      variant="tonal" 
                      color="success" 
                      @click="closeSupportTicket(item)"
                      v-if="item.status !== 'closed'"
                    >
                      <v-icon size="18">mdi-check</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <!-- Вкладка Статистики -->
          <v-window-item value="stats">
            <v-row>
              <v-col cols="12" md="6" lg="3" v-for="(stat, index) in statsCards" :key="index">
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
            
            <!-- Статистика заказов по статусам -->
            <v-row class="mt-4">
              <v-col cols="12" md="6">
                <v-card class="admin-card pa-3 mt-4" elevation="1">
                  <v-card-title class="font-weight-medium">Заказы по статусам</v-card-title>
                  <v-card-text>
                    <v-list>
                      <v-list-item
                        v-for="(count, status) in statsData.orders?.by_status || {}"
                        :key="status"
                        class="px-0"
                      >
                        <template v-slot:prepend>
                          <v-chip :color="getStatusColor(status)" size="small" class="mr-3">
                            {{ status }}
                          </v-chip>
                        </template>
                        <v-list-item-title class="text-right">{{ count }} заказов</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="6">
                <v-card class="admin-card pa-3 mt-4" elevation="1">
                  <v-card-title class="font-weight-medium">Последние заказы</v-card-title>
                  <v-card-text>
                    <v-timeline density="compact" side="end">
                      <v-timeline-item
                        v-for="order in statsData.recent_orders || []"
                        :key="order.order_id"
                        size="small"
                        :dot-color="getStatusColor(order.status)"
                      >
                        <div>
                          <div class="font-weight-medium">Заказ #{{ order.order_number }}</div>
                          <div class="text-caption text-grey mt-1">
                            {{ new Date(order.created_at).toLocaleDateString('ru-RU') }} • {{ formatPrice(order.total_amount) }}
                          </div>
                          <div class="text-caption">
                            {{ order.user?.name || 'Без имени' }}
                          </div>
                          <v-chip 
                            :color="getStatusColor(order.status)" 
                            size="small"
                            class="mt-2"
                            variant="tonal"
                          >
                            {{ order.status }}
                          </v-chip>
                        </div>
                      </v-timeline-item>
                    </v-timeline>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <!-- Диалоги -->
    <!-- Диалог деталей заказа -->
    <v-dialog v-model="orderDetailsDialog" max-width="600">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Заказ #{{ selectedOrder?.order_number }}</span>
          <v-btn icon @click="orderDetailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text v-if="selectedOrder">
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Статус:</div>
            <v-select
              v-model="selectedOrder.status"
              :items="statusOptions.filter(s => s !== null)"
              variant="outlined"
              density="compact"
              @update:model-value="saveOrderStatus"
            ></v-select>
          </div>
          
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Клиент:</div>
            <div v-if="selectedOrder.user">
              <div>{{ selectedOrder.user.name || 'Не указано' }}</div>
              <div class="text-caption">Username: @{{ selectedOrder.user.username || 'нет' }}</div>
              <div class="text-caption">Telegram ID: {{ selectedOrder.user.telegram_id }}</div>
              <div class="text-caption">{{ selectedOrder.user.phone || 'Нет телефона' }}</div>
              <v-btn 
                size="small" 
                color="primary" 
                variant="tonal" 
                class="mt-1"
                @click="openTelegramChat(selectedOrder.user.telegram_id)"
              >
                <v-icon size="16" class="mr-1">mdi-telegram</v-icon>
                Написать в Telegram
              </v-btn>
            </div>
            <div v-else>Пользователь не найден</div>
          </div>
          
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Товары:</div>
            <v-list density="compact">
              <v-list-item
                v-for="(item, index) in selectedOrder.items"
                :key="index"
              >
                <v-list-item-title>{{ item.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ item.quantity }} × {{ formatPrice(item.price) }} = {{ formatPrice(item.subtotal) }}
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
          
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Дата создания:</div>
            <div>{{ new Date(selectedOrder.created_at).toLocaleString('ru-RU') }}</div>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="orderDetailsDialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Диалог отправки сообщения в Telegram -->
    <v-dialog v-model="messageDialog" max-width="500">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Отправить сообщение через Telegram</span>
          <v-btn icon @click="messageDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text v-if="selectedUser">
          <div class="mb-4">
            <div class="text-subtitle-1 font-weight-medium mb-1">Пользователь:</div>
            <div>{{ selectedUser.name || selectedUser.username || 'Без имени' }}</div>
            <div class="text-caption">Telegram ID: {{ selectedUser.telegram_id }}</div>
            <div class="text-caption">
              <v-btn 
                color="primary" 
                size="small" 
                variant="tonal"
                @click="openTelegramChat(selectedUser.telegram_id)"
                class="mt-1"
              >
                <v-icon size="16" class="mr-1">mdi-open-in-new</v-icon>
                Открыть чат в Telegram
              </v-btn>
            </div>
          </div>
          
          <v-textarea
            v-model="messageText"
            label="Текст сообщения (будет отправлено через Telegram бота)"
            variant="outlined"
            density="comfortable"
            rows="4"
            placeholder="Введите текст сообщения..."
            required
            :rules="[v => !!v || 'Текст сообщения обязателен']"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="messageDialog = false" :disabled="sendingMessage">
            Отмена
          </v-btn>
          <v-btn 
            color="primary" 
            @click="sendTelegramMessage"
            :loading="sendingMessage"
            :disabled="!messageText.trim()"
          >
            Отправить через бота
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Диалог добавления/редактирования товара -->
    <v-dialog v-model="productDialog" max-width="500">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>{{ editingProduct ? 'Редактировать товар' : 'Добавить товар' }}</span>
          <v-btn icon @click="productDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-text-field
            v-model="currentProduct.name"
            label="Название товара"
            variant="outlined"
            density="compact"
            required
          ></v-text-field>
          <v-textarea
            v-model="currentProduct.description"
            label="Описание"
            variant="outlined"
            density="compact"
            rows="2"
          ></v-textarea>
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="currentProduct.price"
                label="Цена (руб.)"
                type="number"
                variant="outlined"
                density="compact"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="currentProduct.stock_quantity"
                label="Количество на складе"
                type="number"
                variant="outlined"
                density="compact"
                required
              ></v-text-field>
            </v-col>
          </v-row>
          <v-select
            v-model="currentProduct.category_id"
            :items="categories"
            item-title="name"
            item-value="category_id"
            label="Категория"
            variant="outlined"
            density="compact"
          ></v-select>
          <v-switch
            v-model="currentProduct.is_available"
            label="Доступен для покупки"
            color="success"
          ></v-switch>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="productDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveProduct" :loading="savingProduct">
            {{ editingProduct ? 'Сохранить' : 'Добавить' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Диалог добавления/редактирования услуги -->
    <v-dialog v-model="serviceDialog" max-width="500">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>{{ editingService ? 'Редактировать услугу' : 'Добавить услугу' }}</span>
          <v-btn icon @click="serviceDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-text-field
            v-model="currentService.name"
            label="Название услуги"
            variant="outlined"
            density="compact"
            required
          ></v-text-field>
          <v-textarea
            v-model="currentService.description"
            label="Описание"
            variant="outlined"
            density="compact"
            rows="2"
            required
          ></v-textarea>
          <v-text-field
            v-model="currentService.price"
            label="Цена (руб.)"
            type="number"
            variant="outlined"
            density="compact"
            required
          ></v-text-field>
          <v-text-field
            v-model="currentService.duration"
            label="Время выполнения"
            placeholder="Например: 1-3 дня"
            variant="outlined"
            density="compact"
          ></v-text-field>
          <v-text-field
            v-model="currentService.category"
            label="Категория"
            placeholder="Например: Ремонт"
            variant="outlined"
            density="compact"
          ></v-text-field>
          <v-switch
            v-model="currentService.is_active"
            label="Активна"
            color="success"
          ></v-switch>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="serviceDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveService" :loading="savingService">
            {{ editingService ? 'Сохранить' : 'Добавить' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Уведомления -->
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarMessage }}
    </v-snackbar>
  </v-container>
</template>

<script>
import { useApi } from '@/composables/useApi'

export default {
  name: 'AdminView',
  data() {
    return {
      activeTab: 'orders',
      
      // Данные администратора
      adminName: 'Администратор',
      adminAvatar: '',
      
      // Быстрые действия
      quickActions: [
        { title: 'Новый заказ', icon: 'mdi-cart-plus', color: 'primary', route: '/orders' },
        { title: 'Добавить товар', icon: 'mdi-package-variant-plus', color: 'success', route: '/admin?tab=products' },
        { title: 'Статистика', icon: 'mdi-chart-bar', color: 'info', route: '/admin?tab=stats' },
        { title: 'Поддержка', icon: 'mdi-headset', color: 'warning', route: '/admin?tab=support' }
      ],
      
      // Данные заказов
      orders: [],
      loadingOrders: false,
      orderFilter: null,
      orderHeaders: [
        { title: '№', value: 'order_number', width: '100' },
        { title: 'Дата', value: 'created_at', width: '120' },
        { title: 'Клиент', value: 'user', width: '150' },
        { title: 'Сумма', value: 'total_amount', width: '100' },
        { title: 'Статус', value: 'status', width: '120' },
        { title: 'Действия', value: 'actions', width: '150' }
      ],
      
      // Данные заказов услуг
      serviceOrders: [],
      loadingServiceOrders: false,
      serviceOrderFilter: null,
      serviceOrderHeaders: [
        { title: 'ID', value: 'service_order_id', width: '80' },
        { title: 'Дата', value: 'created_at', width: '120' },
        { title: 'Клиент', value: 'user', width: '150' },
        { title: 'Услуга', value: 'service.name', width: '150' },
        { title: 'Цена', value: 'price', width: '100' },
        { title: 'Статус', value: 'status', width: '120' },
        { title: 'Действия', value: 'actions', width: '120' }
      ],
      
      // Данные товаров
      products: [],
      loadingProducts: false,
      productHeaders: [
        { title: 'Изображение', value: 'images', width: '80' },
        { title: 'Название', value: 'name' },
        { title: 'Цена', value: 'price', width: '100' },
        { title: 'Остаток', value: 'stock_quantity', width: '100' },
        { title: 'Доступен', value: 'is_available', width: '100' },
        { title: 'Действия', value: 'actions', width: '120' }
      ],
      
      // Данные услуг
      services: [],
      loadingServices: false,
      
      // Данные пользователей
      users: [],
      loadingUsers: false,
      userSearch: '',
      userHeaders: [
        { title: 'Telegram ID', value: 'telegram_id', width: '120' },
        { title: 'Имя', value: 'name' },
        { title: 'Username', value: 'username', width: '120' },
        { title: 'Заказов', value: 'orders_count', width: '80' },
        { title: 'Активен', value: 'is_active', width: '100' },
        { title: 'Админ', value: 'is_admin', width: '100' },
        { title: 'Действия', value: 'actions', width: '120' }
      ],
      
      // Данные поддержки
      supportTickets: [],
      loadingSupport: false,
      supportFilter: null,
      supportStatuses: [null, 'open', 'pending', 'closed'],
      supportHeaders: [
        { title: 'ID', value: 'ticket_id', width: '80' },
        { title: 'Тема', value: 'subject' },
        { title: 'Пользователь', value: 'user', width: '150' },
        { title: 'Статус', value: 'status', width: '120' },
        { title: 'Создан', value: 'created_at', width: '150' },
        { title: 'Действия', value: 'actions', width: '150' }
      ],
      
      // Статистика
      statsData: {},
      statsCards: [],
      
      // Статусы
      statusOptions: [null, 'Создан', 'Оплачен', 'Подтвержден', 'Отправлен', 'Доставлен', 'Отменен'],
      
      // Категории
      categories: [],
      
      // Диалоги
      orderDetailsDialog: false,
      selectedOrder: null,
      
      messageDialog: false,
      selectedUser: null,
      messageText: '',
      sendingMessage: false,
      
      productDialog: false,
      currentProduct: {
        name: '',
        description: '',
        price: 0,
        stock_quantity: 0,
        category_id: null,
        is_available: true
      },
      editingProduct: false,
      savingProduct: false,
      
      serviceDialog: false,
      currentService: {
        name: '',
        description: '',
        price: 0,
        duration: '',
        category: '',
        is_active: true
      },
      editingService: false,
      savingService: false,
      
      // Уведомления
      showSnackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success'
    }
  },
  async mounted() {
    await this.loadAdminData();
    await this.fetchInitialData();
    
    // Проверяем параметр таба из URL
    const tab = this.$route.query.tab;
    if (tab && ['orders', 'service_orders', 'products', 'services', 'users', 'support', 'stats'].includes(tab)) {
      this.activeTab = tab;
    }
  },
  watch: {
    activeTab(newTab) {
      switch (newTab) {
        case 'products':
          this.fetchProducts();
          break;
        case 'services':
          this.fetchServices();
          break;
        case 'users':
          this.fetchUsers();
          break;
        case 'support':
          this.fetchSupportTickets();
          break;
        case 'stats':
          this.fetchStats();
          break;
      }
    }
  },
  methods: {
    async loadAdminData() {
      try {
        const { get } = useApi();
        const tg_user = window.Telegram?.WebApp?.initDataUnsafe?.user;
        const telegramId = tg_user?.id || 391622124;
        
        // Проверяем права администратора
        const adminData = await get(`/api/admin/check_simple/${telegramId}`);
        if (!adminData.is_admin) {
          this.$router.push('/profile');
          return;
        }
        
        this.adminName = adminData.name || 'Администратор';
      } catch (error) {
        console.error('❌ Ошибка загрузки данных администратора:', error);
        this.$router.push('/profile');
      }
    },
    
    async fetchInitialData() {
      await this.fetchOrders();
      await this.fetchCategories();
      // Остальные данные будут загружаться по мере переключения вкладок
    },
    
    formatPrice(price) {
      return new Intl.NumberFormat('ru-BY', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(price) + ' p.';
    },
    
    getStatusColor(status) {
      const colors = {
        'Создан': 'blue',
        'Оплачен': 'green',
        'Подтвержден': 'teal',
        'Отправлен': 'orange',
        'Доставлен': 'success',
        'Отменен': 'error'
      };
      return colors[status] || 'grey';
    },
    
    getProductImage(product) {
      if (!product || !product.images) return 'https://via.placeholder.com/100x100/667eea/ffffff?text=No+Image';
      
      try {
        let imagePath = product.images;
        if (typeof product.images === 'string') {
          try {
            const images = JSON.parse(product.images);
            imagePath = images[0];
          } catch (e) {
            imagePath = product.images;
          }
        } else if (Array.isArray(product.images)) {
          imagePath = product.images[0];
        }
        
        if (imagePath && imagePath.startsWith('http')) {
          return imagePath;
        }
        
        if (imagePath && imagePath.startsWith('/')) {
          return `https://psychic-adventure-wrpj64gv4jx7h5pwp-8000.app.github.dev${imagePath}`;
        }
        
        return imagePath || 'https://via.placeholder.com/100x100/667eea/ffffff?text=No+Image';
      } catch (e) {
        return 'https://via.placeholder.com/100x100/667eea/ffffff?text=No+Image';
      }
    },
    
    navigateTo(route) {
      this.$router.push(route);
    },
    
    // Методы для заказов
    async fetchOrders() {
      this.loadingOrders = true;
      try {
        const { get } = useApi();
        let url = '/api/admin/orders';
        if (this.orderFilter) {
          url += `?status=${this.orderFilter}`;
        }
        const response = await get(url);
        this.orders = response.orders || [];
      } catch (error) {
        console.error('❌ Ошибка загрузки заказов:', error);
        this.showMessage('Ошибка загрузки заказов', 'error');
      } finally {
        this.loadingOrders = false;
      }
    },
    
    async fetchServiceOrders() {
      this.loadingServiceOrders = true;
      try {
        const { get } = useApi();
        let url = '/api/admin/service_orders';
        if (this.serviceOrderFilter) {
          url += `?status=${this.serviceOrderFilter}`;
        }
        const response = await get(url);
        this.serviceOrders = response.service_orders || [];
      } catch (error) {
        console.error('❌ Ошибка загрузки заказов услуг:', error);
        this.showMessage('Ошибка загрузки заказов услуг', 'error');
      } finally {
        this.loadingServiceOrders = false;
      }
    },
    
    async fetchCategories() {
      try {
        const { get } = useApi();
        this.categories = await get('/api/categories');
      } catch (error) {
        console.error('❌ Ошибка загрузки категорий:', error);
      }
    },
    
    viewOrderDetails(order) {
      this.selectedOrder = order;
      this.orderDetailsDialog = true;
    },
    
    async saveOrderStatus() {
      if (!this.selectedOrder || !this.selectedOrder.status) return;
      
      try {
        const { put } = useApi();
        await put(`/api/admin/orders/${this.selectedOrder.order_id}`, {
          status: this.selectedOrder.status
        });
        
        this.showMessage('Статус заказа обновлен', 'success');
        await this.fetchOrders();
        this.orderDetailsDialog = false;
      } catch (error) {
        console.error('❌ Ошибка обновления статуса:', error);
        this.showMessage('Ошибка обновления статуса', 'error');
      }
    },
    
    async updateOrderStatus(item, status) {
      try {
        const { put } = useApi();
        await put(`/api/admin/orders/${item.order_id}`, { status });
        
        this.showMessage(`Статус заказа #${item.order_number} обновлен на "${status}"`, 'success');
        await this.fetchOrders();
      } catch (error) {
        console.error('❌ Ошибка обновления статуса заказа:', error);
        this.showMessage('Ошибка обновления статуса заказа', 'error');
      }
    },
    
    async updateServiceOrderStatus(item, status) {
      try {
        const { put } = useApi();
        await put(`/api/admin/service_orders/${item.service_order_id}`, { status });
        
        this.showMessage(`Статус заказа услуги обновлен на "${status}"`, 'success');
        await this.fetchServiceOrders();
      } catch (error) {
        console.error('❌ Ошибка обновления статуса заказа услуги:', error);
        this.showMessage('Ошибка обновления статуса заказа услуги', 'error');
      }
    },
    
    async fetchProducts() {
        this.loadingProducts = true;
        try {
            const { get } = useApi();
            this.products = await get('/api/admin/products');
        } catch (error) {
            console.error('❌ Ошибка загрузки товаров:', error);
            this.showMessage('Ошибка загрузки товаров', 'error');
        } finally {
            this.loadingProducts = false;
        }
    },

    // Методы для услуг
    async fetchServices() {
        this.loadingServices = true;
        try {
            const { get } = useApi();
            this.services = await get('/api/admin/services');
        } catch (error) {
            console.error('❌ Ошибка загрузки услуг:', error);
            this.showMessage('Ошибка загрузки услуг', 'error');
        } finally {
            this.loadingServices = false;
        }
    },
    
    openAddProductDialog() {
      this.editingProduct = false;
      this.currentProduct = {
        name: '',
        description: '',
        price: 0,
        stock_quantity: 0,
        category_id: null,
        is_available: true
      };
      this.productDialog = true;
    },
    
    editProduct(product) {
      this.editingProduct = true;
      this.currentProduct = { ...product };
      this.productDialog = true;
    },
    
    async saveProduct() {
      this.savingProduct = true;
      try {
        const { post, put } = useApi();
        
        if (this.editingProduct) {
          await put(`/api/admin/products/${this.currentProduct.product_id}`, this.currentProduct);
          this.showMessage('Товар обновлен', 'success');
        } else {
          await post('/api/admin/products', this.currentProduct);
          this.showMessage('Товар добавлен', 'success');
        }
        
        this.productDialog = false;
        await this.fetchProducts();
      } catch (error) {
        console.error('❌ Ошибка сохранения товара:', error);
        this.showMessage('Ошибка сохранения товара', 'error');
      } finally {
        this.savingProduct = false;
      }
    },
    
    async updateProductAvailability(product) {
      try {
        const { put } = useApi();
        await put(`/api/admin/products/${product.product_id}`, {
          is_available: product.is_available
        });
        this.showMessage('Доступность товара обновлена', 'success');
      } catch (error) {
        console.error('❌ Ошибка обновления доступности товара:', error);
        product.is_available = !product.is_available; // Откатываем изменение
        this.showMessage('Ошибка обновления доступности товара', 'error');
      }
    },
    
    async deleteProduct(product) {
      if (!confirm(`Удалить товар "${product.name}"?`)) return;
      
      try {
        const { del } = useApi();
        await del(`/api/admin/products/${product.product_id}`);
        
        this.showMessage('Товар удален', 'success');
        await this.fetchProducts();
      } catch (error) {
        console.error('❌ Ошибка удаления товара:', error);
        this.showMessage('Ошибка удаления товара', 'error');
      }
    },
    
    openAddServiceDialog() {
      this.editingService = false;
      this.currentService = {
        name: '',
        description: '',
        price: 0,
        duration: '',
        category: '',
        is_active: true
      };
      this.serviceDialog = true;
    },
    
    editService(service) {
      this.editingService = true;
      this.currentService = { ...service };
      this.serviceDialog = true;
    },
    
    async saveService() {
      this.savingService = true;
      try {
        const { post, put } = useApi();
        
        if (this.editingService) {
          await put(`/api/admin/services/${this.currentService.service_id}`, this.currentService);
          this.showMessage('Услуга обновлена', 'success');
        } else {
          await post('/api/admin/services', this.currentService);
          this.showMessage('Услуга добавлена', 'success');
        }
        
        this.serviceDialog = false;
        await this.fetchServices();
      } catch (error) {
        console.error('❌ Ошибка сохранения услуги:', error);
        this.showMessage('Ошибка сохранения услуги', 'error');
      } finally {
        this.savingService = false;
      }
    },
    
    async updateServiceActivity(service) {
      try {
        const { put } = useApi();
        await put(`/api/admin/services/${service.service_id}`, {
          is_active: service.is_active
        });
        this.showMessage('Статус услуги обновлен', 'success');
      } catch (error) {
        console.error('❌ Ошибка обновления статуса услуги:', error);
        service.is_active = !service.is_active; // Откатываем изменение
        this.showMessage('Ошибка обновления статуса услуги', 'error');
      }
    },
    
    async deleteService(service) {
      if (!confirm(`Удалить услугу "${service.name}"?`)) return;
      
      try {
        const { del } = useApi();
        await del(`/api/admin/services/${service.service_id}`);
        
        this.showMessage('Услуга удалена', 'success');
        await this.fetchServices();
      } catch (error) {
        console.error('❌ Ошибка удаления услуги:', error);
        this.showMessage('Ошибка удаления услуги', 'error');
      }
    },
    
    // Методы для пользователей
    async fetchUsers() {
      this.loadingUsers = true;
      try {
        const { get } = useApi();
        let url = '/api/admin/users';
        if (this.userSearch) {
          url += `?search=${encodeURIComponent(this.userSearch)}`;
        }
        this.users = await get(url);
      } catch (error) {
        console.error('❌ Ошибка загрузки пользователей:', error);
        this.showMessage('Ошибка загрузки пользователей', 'error');
      } finally {
        this.loadingUsers = false;
      }
    },
    
    async updateUserActivity(user) {
      try {
        // В реальном приложении здесь должен быть API вызов
        this.showMessage('Статус пользователя обновлен', 'success');
      } catch (error) {
        console.error('❌ Ошибка обновления статуса пользователя:', error);
        user.is_active = !user.is_active; // Откатываем изменение
        this.showMessage('Ошибка обновления статуса пользователя', 'error');
      }
    },
    
    async updateUserAdminStatus(user) {
      try {
        // В реальном приложении здесь должен быть API вызов
        this.showMessage('Статус администратора обновлен', 'success');
      } catch (error) {
        console.error('❌ Ошибка обновления статуса администратора:', error);
        user.is_admin = !user.is_admin; // Откатываем изменение
        this.showMessage('Ошибка обновления статуса администратора', 'error');
      }
    },
    
    sendMessageToUser(user) {
      this.selectedUser = user;
      this.messageText = '';
      this.messageDialog = true;
    },
    
    async sendTelegramMessage() {
      if (!this.selectedUser || !this.messageText.trim()) return;
      
      this.sendingMessage = true;
      try {
        const { post } = useApi();
        await post('/api/admin/send_message', {
          telegram_id: this.selectedUser.telegram_id,
          message: this.messageText
        });
        
        this.showMessage('Сообщение отправлено через Telegram бота', 'success');
        this.messageDialog = false;
      } catch (error) {
        console.error('❌ Ошибка отправки сообщения:', error);
        this.showMessage('Ошибка отправки сообщения', 'error');
      } finally {
        this.sendingMessage = false;
      }
    },
    
    openTelegramChat(telegramId) {
      // Открывает чат с пользователем в Telegram
      const telegramUrl = `https://t.me/${telegramId}`;
      window.open(telegramUrl, '_blank');
    },
    
    viewUserOrders(user) {
      this.showMessage(`Просмотр заказов пользователя ${user.name}`, 'info');
      // В реальном приложении можно открыть список заказов пользователя
    },
    
    // Методы для поддержки
    getSupportStatusColor(status) {
      const colors = {
        'open': 'warning',
        'pending': 'info',
        'closed': 'success'
      };
      return colors[status] || 'grey';
    },
    
    getSupportStatusText(status) {
      const texts = {
        'open': 'Открыт',
        'pending': 'В обработке',
        'closed': 'Закрыт'
      };
      return texts[status] || status;
    },
    
    async fetchSupportTickets() {
      this.loadingSupport = true;
      try {
        const { get } = useApi();
        let url = '/api/admin/support/tickets';
        if (this.supportFilter) {
          url += `?status=${this.supportFilter}`;
        }
        const response = await get(url);
        this.supportTickets = response.tickets || [];
      } catch (error) {
        console.error('❌ Ошибка загрузки тикетов поддержки:', error);
        this.showMessage('Ошибка загрузки тикетов поддержки', 'error');
      } finally {
        this.loadingSupport = false;
      }
    },
    
    async closeSupportTicket(ticket) {
      if (!confirm(`Закрыть тикет "${ticket.subject}"?`)) return;
      
      try {
        const { put } = useApi();
        await put(`/api/admin/support/tickets/${ticket.ticket_id}/close`);
        this.showMessage('Тикет закрыт', 'success');
        await this.fetchSupportTickets();
      } catch (error) {
        console.error('❌ Ошибка закрытия тикета:', error);
        this.showMessage('Ошибка закрытия тикета', 'error');
      }
    },
    
    // Методы для статистики
    async fetchStats() {
      try {
        const { get } = useApi();
        this.statsData = await get('/api/admin/stats');
        
        // Формируем карточки статистики
        this.statsCards = [
          { label: 'Всего пользователей', value: this.statsData.users?.total || 0, icon: 'mdi-account-group', color: 'primary' },
          { label: 'Всего заказов', value: this.statsData.orders?.total || 0, icon: 'mdi-cart', color: 'success' },
          { label: 'Доступных товаров', value: this.statsData.products?.available || 0, icon: 'mdi-package', color: 'info' },
          { label: 'Общая выручка', value: this.formatPrice(this.statsData.revenue?.total || 0), icon: 'mdi-cash', color: 'warning' }
        ];
      } catch (error) {
        console.error('❌ Ошибка загрузки статистики:', error);
      }
    },
    
    // Наблюдатель за активной вкладкой
    
    showMessage(message, type = 'success') {
      this.snackbarMessage = message;
      this.snackbarColor = type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'success';
      this.showSnackbar = true;
      
      setTimeout(() => {
        this.showSnackbar = false;
      }, 3000);
    }
  }
}
</script>
