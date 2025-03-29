<template>
  <div class="agent-item">
    <div style="display: flex;justify-content: space-between;">
      <div style="font-weight: 700;font-size: 18px;text-align: left;color: #3d4566;">
         {{ agent.agentName }}
      </div>
      <div>
        <img src="@/assets/home/delete.png" alt=""
             style="width: 18px;height: 18px;" @click="$emit('del', agent.id)" />
        <!-- <img src="@/assets/home/info.png" alt="" style="width: 18px;height: 18px;" /> -->
      </div>
    </div>
    <div class="agent-name">
      角色音色：{{ agent.ttsModelName }}
    </div>
    <div class="agent-name">
      语言模型：{{ agent.llmModelName }}
    </div>
    <div class="agent-name">
      最近对话：{{ agent.lastConnectedAt }}
    </div>
    <div style="display: flex;justify-content: space-between;align-items: center;gap: 10px;">
      <div class="settings-btn" @click="$emit('configure', agent.id)">
        配置角色
      </div>
      <div class="settings-btn" @click="$emit('asr', agent.id)">
        声纹识别
      </div>
      <div class="settings-btn" @click="$emit('chat', agent.id)">
        历史对话
      </div>
      <div class="settings-btn" @click="$emit('device', agent.id)">
        设备数量({{agent.deviceCount}})
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AgentItem',
  props: {
    agent: { type: Object, required: true }
  },
  data() {
    return { }
  }
}
</script>
<style scoped>
.agent-item {
  width: 342px;
  border-radius: 20px;
  background: #fafcfe;
  padding: 22px 22px 11px 22px;
  box-sizing: border-box;
}
.agent-name {
  margin: 7px 0 10px;
  font-weight: 400;
  font-size: 11px;
  color: #3d4566;
  text-align: left;
}

.settings-btn {
  font-weight: 500;
  font-size: 10px;
  color: #5778ff;
  background: #e6ebff;
  padding: 2px 10px;
  line-height: 21px;
  cursor: pointer;
  border-radius: 14px;
}

</style>