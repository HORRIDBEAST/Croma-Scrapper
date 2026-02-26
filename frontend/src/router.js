import { createRouter, createWebHistory } from 'vue-router'
import CromaApp from './App.vue'
import PharmaApp from './PharmaApp.vue'

const routes = [
  { path: '/',       component: CromaApp  },
  { path: '/pharma', component: PharmaApp }
]

export default createRouter({
  history: createWebHistory(),
  routes
})