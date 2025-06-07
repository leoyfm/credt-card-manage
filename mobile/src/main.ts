import '@/style/index.scss'

// 在开发环境下引入 Mock 数据
// #ifdef H5
if (import.meta.env.MODE === 'development') {
  console.log('🔧 开发环境，正在加载 Mock 数据...')
  import('@/mock/index').then(() => {
    console.log('✅ Mock 数据加载完成')
  }).catch((error) => {
    console.error('❌ Mock 数据加载失败:', error)
  })
}
// #endif

import { VueQueryPlugin } from '@tanstack/vue-query'
import 'uno.css'
import { createSSRApp } from 'vue'

import App from './App.vue'
import { prototypeInterceptor, requestInterceptor, routeInterceptor } from './interceptors'
import store from './store'

export function createApp() {
  const app = createSSRApp(App)
  app.use(store)
  app.use(routeInterceptor)
  app.use(requestInterceptor)
  app.use(prototypeInterceptor)
  app.use(VueQueryPlugin)

  return {
    app,
  }
}
