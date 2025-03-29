import RequestService from '../httpRequest'
import {getServiceUrl} from '../api'


export default {
    //设备列表
    getDeviceList(agent_id, page, callback) {
        RequestService.sendRequest().url(`${getServiceUrl()}/user/agent/device/bind/${agent_id}`)
            .method('GET')
            .data(page)
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('获取设备列表失败:', err);
            }).send()
    },
    //绑定设备
    bindDevice(agentId, deviceCode, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/agent/device/bind/${agentId}`)
            .method('POST')
            .data({deviceCode})
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('绑定设备失败:', err);
                // RequestService.reAjaxFun(() => {
                //     this.addDevice(agentId, deviceCode, callback);
                // });
            }).send();
    },
    // 解绑设备
    unbindDevice(deviceId, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/agent/device/unbind/${deviceId}`)
            .method('PUT')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('解绑设备失败:', err);
                // RequestService.reAjaxFun(() => {
                //   this.unbindDevice(deviceId, callback);
                // });
              }).send()
    },
    // 切换设备OTA升级状态
    toggleAutoUpdate(deviceId, autoUpdate, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/agent/device/autoUpdate/${deviceId}`)
            .method('POST')
            .data({autoUpdate})
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('切换设备OTA升级状态失败:', err);
              }).send()
    },
    // 设置设备别名
    setAlias(deviceId, alias, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/agent/device/alias/${deviceId}`)
            .method('POST')
            .data({alias})
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('设置设备别名失败:', err);
              }).send()
    },

}
