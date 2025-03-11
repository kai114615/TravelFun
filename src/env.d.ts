/// <reference types="vite/client" />

// 為所有 .vue 檔案宣告型別
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}