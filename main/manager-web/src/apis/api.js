// 引入各个模块的请求
import admin from './module/admin.js'
import agent from './module/agent.js'
import device from './module/device.js'
import model from './module/model.js'
import user from './module/user.js'
import timbre from "./module/timbre.js";

/**
 * 接口地址
 * 开发时自动读取使用.env.development文件
 * 编译时自动读取使用.env.production文件
 */
// const DEV_API_SERVICE = process.env.VUE_APP_API_BASE_URL
const DEV_API_SERVICE = 'https://2662r3426b.vicp.fun/xiaozhi'

/**
 * 根据开发环境返回接口url
 * @returns {string}
 */
export function getServiceUrl() {
    return DEV_API_SERVICE
}


/** request服务封装 */
export default {
    getServiceUrl,
    user,
    admin,
    agent,
    device,
    model,
    timbre,
}
