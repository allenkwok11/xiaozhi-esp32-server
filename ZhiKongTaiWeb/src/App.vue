<template>
  <div id="app">
    <div class="app-content">
      <router-view></router-view>
    </div>
    <Footer />
  </div>
</template>

<script>
import Footer from './components/Footer.vue';

export default {
  name: 'App',
  components: { 
    Footer 
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
}

/* 登录注册页面的布局 */
.auth-layout {
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* 主要页面的布局 */
.main-layout {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>