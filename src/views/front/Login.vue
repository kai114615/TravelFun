<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
      <!-- 標題區域 -->
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">
          歡迎回來
        </h2>
        <p class="text-gray-600">
          登入您的帳號以繼續
        </p>
      </div>

      <!-- 登入表單 -->
      <NForm
        ref="formRef"
        :model="formValue"
        :rules="rules"
        class="space-y-6"
      >
        <!-- 帳號輸入 -->
        <NFormItem path="username" label="帳號">
          <NInput
            v-model:value="formValue.username"
            placeholder="請輸入帳號"
            size="large"
            :maxlength="30"
            class="rounded-lg"
          />
        </NFormItem>

        <!-- 密碼輸入 -->
        <NFormItem path="password" label="密碼">
          <NInput
            v-model:value="formValue.password"
            type="password"
            placeholder="請輸入密碼"
            size="large"
            :maxlength="30"
            show-password-on="click"
            class="rounded-lg"
          />
        </NFormItem>

        <!-- 驗證碼區域 -->
        <NFormItem path="captcha" label="驗證碼">
          <div class="flex items-center gap-4">
            <NInput
              v-model:value="formValue.captcha"
              placeholder="請輸入驗證碼"
              size="large"
              :maxlength="6"
              class="rounded-lg flex-1"
            />
            <!-- 放大驗證碼圖片 -->
            <div class="captcha-container cursor-pointer" @click="refreshCaptcha">
              <img
                :src="captchaUrl"
                alt="驗證碼"
                class="h-12 rounded-lg shadow-sm hover:shadow-md transition-shadow"
                style="min-width: 150px; height: 48px;"
              >
            </div>
          </div>
        </NFormItem>

        <!-- 記住我選項 -->
        <div class="flex items-center justify-between">
          <NCheckbox v-model:checked="rememberMe">
            記住我
          </NCheckbox>
          <a href="#" class="text-primary hover:text-primary-dark text-sm">
            忘記密碼？
          </a>
        </div>

        <!-- 登入按鈕 -->
        <div class="pt-4">
          <NButton
            type="primary"
            size="large"
            block
            :loading="isLoading"
            :disabled="isLoading"
            class="rounded-lg h-12 text-lg"
            @click="handleSubmit"
          >
            {{ isLoading ? '登入中...' : '登入' }}
          </NButton>
        </div>

        <!-- 註冊連結 -->
        <div class="text-center text-gray-600 mt-6">
          還沒有帳號？
          <router-link
            to="/register"
            class="text-primary hover:text-primary-dark font-medium"
          >
            立即註冊
          </router-link>
        </div>
      </NForm>
    </div>
  </div>
</template>

<style scoped>
.captcha-container {
  position: relative;
  overflow: hidden;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
}

.captcha-container:hover {
  transform: scale(1.02);
}

.captcha-container img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 自定義輸入框樣式 */
:deep(.n-input) {
  border-radius: 0.5rem;
}

:deep(.n-input:hover),
:deep(.n-input:focus) {
  border-color: var(--primary-color);
}

:deep(.n-button) {
  font-weight: 500;
  letter-spacing: 0.025em;
}

:deep(.n-form-item-label) {
  font-weight: 500;
  color: #374151;
}

/* 添加漸變背景 */
.bg-gradient-to-b {
  background-image: linear-gradient(to bottom, var(--primary-color-light), white);
}
</style>
