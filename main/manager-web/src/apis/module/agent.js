import RequestService from '../httpRequest'
import {getServiceUrl} from '../api'


export default {
    //智能体列表
    getAgentList(callback) {
        RequestService.sendRequest().url(`${getServiceUrl()}/user/agent`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail((err) => {
                console.error('获取智能体列表失败:', err);
            }).send()
    },
    //添加智能体
    addAgent(agentName, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/agent`)
            .method('POST')
            .data({agentName})
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('添加智能体失败:', err);
            }).send();
    },
    //获取智能体配置
    getAgentConfig(agentId, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/agent/${agentId}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('获取智能体配置失败:', err);
                // RequestService.reAjaxFun(() => {
                //     this.getAgentConfig(agent_id, callback);
                // });
            }).send();
    },
    //配置智能体
    saveAgentConfig(agentId, configData, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/agent/${agentId}`)
            .method('PUT')
            .data(configData)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('保存智能体配置失败:', err);
                // RequestService.reAjaxFun(() => {
                //     this.saveAgentConfig(device_id, configData, callback);
                // });
            }).send();
    },
    //删除智能体
    delAgent(agentId, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/user/agent/${agentId}`)
            .method('DELETE')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((err) => {
                console.error('删除智能体失败:', err);
                // RequestService.reAjaxFun(() => {
                //     this.deleteAgent(agent_id, callback);
                // });
            }).send();
    },
}
