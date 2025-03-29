import RequestService from '../httpRequest'
import {getServiceUrl} from '../api'


export default {
    //模型配置列表
    getModelList(callback) {
        RequestService.sendRequest().url(`${getServiceUrl()}/model/list`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('获取模型配置列表失败:', err);
            }).send()
    },
    
    //音色列表
    getTtsVoiceList(ttsModelId, callback) {
        RequestService.sendRequest().url(`${getServiceUrl()}/tts/voice`)
            .method('GET')
            .data({ttsModelId})
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('获取音色列表失败:', err);
            }).send()
    },
}
