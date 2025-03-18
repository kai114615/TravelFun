<script setup lang="ts">
import {
  NConfigProvider,
  NDialogProvider,
  NLoadingBarProvider,
  NMessageProvider,
} from 'naive-ui';
import { computed, onMounted, ref } from 'vue';
import { RouterView, useRoute, useRouter } from 'vue-router';
import Header from '@/components/Header/src/index.vue';
import GlobalAiChat from '@/components/AiChat/GlobalAiChat.vue';

const route = useRoute();
const router = useRouter();

const getThemeOverrides = computed(() => {
  const isAdmin = !!route.meta.requiresAuth;

  const adminCardOverrides = {
    borderRadius: '12px',
  };

  return {
    common: {
      primaryColor: '#0F4BB4',
      primaryColorHover: '#68A0E8',
      primaryColorPressed: '#072A81',
      primaryColorSuppl: '#CDE4FB',
      borderRadius: '5px',
      textColorBase: '#2f4050',
      textColor1: '#2f4050',
      textColor2: '#2f4050',
      textColor3: '#2f4050',
      fontFamily: "'Noto Serif TC', serif",
      fontFamilyMono: "'Noto Serif TC', serif",
    },
    Breadcrumb: {
      itemTextColor: '#0F4BB4',
      itemTextColorHover: '#0F4BB4',
      itemTextColorPressed: '#EE5220',
      itemColorHover: '#CDE4FB',
    },
    Rate: {
      itemColorActive: '#EE5220',
    },
    Card: isAdmin ? adminCardOverrides : {},
    Button: {
      textColor: '#2f4050',
      fontWeight: 500,
    },
    Input: {
      fontFamily: "'Noto Serif TC', serif",
    },
    Typography: {
      fontFamily: "'Noto Serif TC', serif",
    },
    Dialog: {
      titleFontSize: '20px',
      titleTextColor: '#2f4050',
      titleFontWeight: 600,
      fontFamily: "'Noto Serif TC', serif",
    },
    Form: {
      labelFontWeight: 500,
      labelTextColor: '#2f4050',
    }
  };
});

onMounted(() => {
  // 檢查是否需要重定向
  const redirectUrl = localStorage.getItem('redirectAfterLogin');
  if (redirectUrl) {
    localStorage.removeItem('redirectAfterLogin');
    router.replace(redirectUrl);
  }
});
</script>

<template>
  <NConfigProvider :theme-overrides="getThemeOverrides">
    <NLoadingBarProvider>
      <NMessageProvider>
        <NDialogProvider>
          <Header />
          <RouterView />
          <GlobalAiChat />
        </NDialogProvider>
      </NMessageProvider>
    </NLoadingBarProvider>
  </NConfigProvider>
</template>

<style>
/* 引入 Google Fonts - Noto Serif TC */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@200;300;400;500;600;700;900&display=swap');

:root {
  --main-font: 'Noto Serif TC', serif;
  --main-color: #2f4050;
  --main-bg-color: rgba(255, 255, 255, 0.85);
  --main-gradient: linear-gradient(135deg, #1c84c6 0%, #23c6c8 100%);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  font-family: var(--main-font);
  color: var(--main-color);
}

#app {
  width: 100%;
  height: 100vh;
  font-family: var(--main-font);
}

body {
  margin: 0;
  padding: 0;
}

h1, h2, h3, h4, h5, h6, p, span, div, button, input, textarea, select, option {
  font-family: var(--main-font);
}

/* Naive UI 組件全局覆蓋 */
.n-base-selection-input__content,
.n-input__input,
.n-button__content,
.n-form-item-label,
.n-alert-body,
.n-text,
.n-dialog-title,
.n-dialog-content {
  font-family: var(--main-font) !important;
}
</style>
