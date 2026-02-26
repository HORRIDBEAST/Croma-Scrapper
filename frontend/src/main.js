import { createApp } from 'vue'
import { defineComponent, h } from 'vue'
import { RouterView } from 'vue-router'
import router from './router.js'
import App from './App.vue'
import './main.css'

// Root wrapper — must pass the RouterView component, NOT the string 'router-view'
const Root = defineComponent({ render: () => h(RouterView) })

createApp(Root).use(router).mount('#app')