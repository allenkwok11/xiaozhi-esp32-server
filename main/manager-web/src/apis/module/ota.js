import RequestService from '../httpRequest'
import {getServiceUrl} from '../api'


export default {
    //设备OTA列表
    getOtaList(page, callback) {
        RequestService.sendRequest().url(`${getServiceUrl()}/ota/sys/getOtalist`)
            .method('GET')
            .data(page)
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('获取设备OTA列表失败:', err);
            }).send()
    },
    //添加设备OTA
    saveOta(ota, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/ota/sys/save`)
            .method('POST')
            .data(ota)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('添加设备OTA失败:', err);
            }).send();
    },    
    //配置设备OTA
    updateOta(ota, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/ota/sys/update`)
            .method('POST')
            .data(ota)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('保存设备OTA配置失败:', err);
                // RequestService.reAjaxFun(() => {
                //     this.saveAgentConfig(device_id, configData, callback);
                // });
            }).send();
    },
    //切换设备OTA可用状态失败
    toggleEnabled(ota, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/ota/sys/toggleEnabled`)
            .method('POST')
            .data(ota)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('切换设备OTA可用状态失败:', err);
                // RequestService.reAjaxFun(() => {
                //     this.deleteAgent(agent_id, callback);
                // });
            }).send();
    },
}
