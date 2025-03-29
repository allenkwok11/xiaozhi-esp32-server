import RequestService from '../httpRequest'
import {getServiceUrl} from '../api'


export default {
    // 用户列表
    getUserList(callback) {
        RequestService.sendRequest().url(`${getServiceUrl()}/admin/users`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime()
                callback(res)
            })
            .fail(() => {
                // RequestService.reAjaxFun(() => {
                //     this.getUserList()
                // })
            }).send()
    },
}
