import './assets/main.css';

import { createPinia } from 'pinia';
import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import 'vfonts/Lato.css';
import 'vfonts/FiraCode.css';

import App from './App.vue';
import router from './router';
import './styles/main.css';
import './styles/tailwind.css';

const app = createApp(App);

app.config.globalProperties.window = window;

app.use(createPinia());
app.use(router);
app.use(ElementPlus);

app.mount('#app');
