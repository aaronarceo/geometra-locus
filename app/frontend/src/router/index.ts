import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

declare module 'vue-router' {
  interface RouteMeta {
    titulo?: string
    /** Oculta el footer global (el recomendador ocupa toda la altura). */
    ocultarFooter?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { titulo: 'Locus | Geometra' } },
    {
      path: '/recomendador',
      name: 'recomendador',
      component: () => import('../views/RecomendadorView.vue'),
      meta: { titulo: 'Recomendador | Locus', ocultarFooter: true },
    },
    {
      path: '/negocios',
      name: 'negocios',
      component: () => import('../views/NegociosView.vue'),
      meta: { titulo: 'Negocios | Locus' },
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  document.title = to.meta.titulo ?? 'Locus | Geometra'
})

export default router
