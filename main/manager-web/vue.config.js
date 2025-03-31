const { defineConfig } = require('@vue/cli-service');
const dotenv = require('dotenv');

// 确保加载 .env 文件
dotenv.config();
console.log("base_url",process.env.VUE_APP_API_BASE_URL);

module.exports = defineConfig({
  chainWebpack: config => {
    config.plugin('html')
      .tap(args => {
        // 将 VUE_APP_TITLE 从环境变量中注入到 HTML 中
        args[0].title = process.env.VUE_APP_TITLE || '小智-智控台';
        return args;
      });
  },
  devServer: {
    port: 8001, // 指定端口为 8001
    proxy: {
      '/xiaozhi-esp32-api': {
        target: process.env.VUE_APP_API_BASE_URL, // 后端 API 的基础 URL
        changeOrigin: true, // 允许跨域
        pathRewrite: {
          '^/api': '', // 路径重写
        },
      },
    },
    client: {
      overlay: false, // 不显示 webpack 错误覆盖层
    },
  },
});
