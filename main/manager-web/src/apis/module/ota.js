import RequestService from '../httpRequest'
import {getServiceUrl} from '../api'

export default {
    /**
     * 设备激活接口
     * @param {string} code 激活码
     * @param {function} callback 回调函数
     */
    activateDevice(code, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/api/v1/ota/activation`)
            .method('GET')
            .query({code})
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('设备激活失败:', err)
                RequestService.reAjaxFun(() => {
                    this.activateDevice(code, callback)
                })
            }).send()
    },

    /**
     * 检查OTA版本和设备激活状态
     * @param {object} deviceInfo 设备信息对象
     * @param {string} deviceId 设备唯一标识
     * @param {string} clientId 客户端标识
     * @param {function} callback 回调函数
     */
    checkOtaVersion(deviceInfo, deviceId, clientId, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/api/v1/ota`)
            .method('POST')
            .header({
                'Device-Id': deviceId,
                'Client-Id': clientId
            })
            .data(deviceInfo)
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('检查OTA版本失败:', err)
                RequestService.reAjaxFun(() => {
                    this.checkOtaVersion(deviceInfo, deviceId, clientId, callback)
                })
            }).send()
    }
}