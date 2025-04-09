// timbre.js
import { getServiceUrl } from '../api';
import RequestService from '../httpRequest';

export default {
  getVoiceList(params, callback) {
    const queryParams = new URLSearchParams({
      ttsModelId: params.ttsModelId,
      page: params.page || 1,
      limit: params.limit || 10,
      name: params.name || ''
    }).toString();

    RequestService.sendRequest()
      .url(`${getServiceUrl()}/ttsVoice?${queryParams}`)
      .method('GET')
      .success((res) => {
        RequestService.clearRequestTime();
        callback(res.data || []);
      })
      .fail((err) => {
        console.error('获取音色列表失败:', err);
        RequestService.reAjaxFun(() => {
          this.getVoiceList(params, callback);
        });
      }).send();
  },
}