import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'welcome',
    component: function () {
      return import('../views/login.vue')
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: function () {
      return import('../views/register.vue')
    }
  },
  {
    path: '/login',
    name: 'login',
    component: function () {
      return import('../views/login.vue')
    }
  },
  {
    path: '/home',
    name: 'home',
    meta: {
      menuCode: 'agent',
    },
    component: function () {
      return import('../views/home.vue')
    }
  },
  {
    path: '/role-config',
    name: 'RoleConfig',
    meta: {
      menuCode: 'agent',
    },
    component: function () {
      return import('../views/roleConfig.vue')
    }
  },
  {
    path: '/device',
    name: 'Device',
    meta: {
      menuCode: 'agent',
    },
    component: function () {
      return import('../views/device.vue')
    }
  },
  {
    path: '/ota',
    name: 'Ota',
    meta: {
      menuCode: 'ota',
    },
    component: function () {
      return import('../views/ota.vue')
    }
  }
]

const router = new VueRouter({
  routes
})

export default router
