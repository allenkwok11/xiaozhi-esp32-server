import RequestService from '../httpRequest'
import {getServiceUrl} from '../api'


export default {
    // 登录
    login(loginForm, callback) {
        RequestService.sendRequest().url(`${getServiceUrl()}/user/login`)
            .method('POST')
            .data(loginForm)
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('登录失败:', err);
                // RequestService.reAjaxFun(() => {
                //     this.login(loginForm, callback)
                // })
            }).send()
    },    // 获取验证码
    getCaptcha(uuid, callback) {

        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/captcha?uuid=${uuid}`)
            .method('GET')
            .type('blob')
            .header({
                  'Content-Type': 'image/gif',
                  'Pragma': 'No-cache',
                  'Cache-Control': 'no-cache'
            })
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {  // 添加错误参数
                console.error('获取验证码失败:', err);
            }).send()
    },
    // 注册账号
    register(registerForm, callback) {
        RequestService.sendRequest().url(`${getServiceUrl()}/user/register`).method('POST')
            .data(registerForm)
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('注册账号失败:', err);
            }).send()
    },

    // 获取所有模型名称
    getModelNames(callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/models/names`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail(() => {
                // RequestService.reAjaxFun(() => {
                //     this.getModelNames(callback);
                // });
            }).send();
    },

    // 获取模型音色
    getModelVoices(modelName, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/models/${modelName}/voices`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail(() => {
                // RequestService.reAjaxFun(() => {
                //     this.getModelVoices(modelName, callback);
                // });
            }).send();
    },
    // 获取用户信息
    getUserInfo(callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/info`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('接口请求失败:', err)
                // RequestService.reAjaxFun(() => {
                //     this.getUserInfo(callback)
                // })
            }).send()
    },
}
