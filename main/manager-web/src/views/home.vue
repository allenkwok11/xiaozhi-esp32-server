<template>
  <div class="welcome">
      <!-- 公共头部 -->
      <HeaderBar :devices="agents" @search-result="handleSearchResult" />
      <el-main style="padding: 20px;display: flex;flex-direction: column;">
        <div>
          <!-- 首页内容 -->
          <div class="add-agent">
            <div class="add-agent-bg">
              <div class="hellow-text" style="margin-top: 30px;">
                您好，小智
              </div>
              <div class="hellow-text">
                让我们度过
                <div style="display: inline-block;color: #5778FF;">
                  美好的一天！
                </div>
              </div>
              <div class="hi-hint">
                Hello, Let's have a wonderful day!
              </div>
              <div class="add-agent-btn" @click="showAddDialog">
                <div class="left-add">
                  添加智能体
                </div>
                <div style="width: 23px;height: 13px;background: #5778ff;margin-left: -10px;" />
                <div class="right-add">
                  <i class="el-icon-right" style="font-size: 20px;color: #fff;" />
                </div>
              </div>
            </div>
          </div>
          <!-- 面包屑-->
          <div class="breadcrumbs">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>控制台</el-breadcrumb-item>
              <el-breadcrumb-item>智能体</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <!-- 智能体列表-->
          <div style="display: flex;flex-wrap: wrap;margin-top: 20px;gap: 20px;justify-content: flex-start;box-sizing: border-box;">
            <AgentItem v-for="(item,index) in agents" :key="index" :agent="item" @configure="goToRoleConfig" @device="goToDevice" @del="handleAgentDel" />
          </div>
        </div>
        <!-- 底部 -->
        <Footer :visible="true" />
        <!-- 添加设备对话框 -->
        <AddAgentDialog :visible.sync="addAgentDialogVisible" @confirm="handleAgentAdded" />
      </el-main>
  </div>

</template>

<script>
import {getUUID, goToPage, showDanger, showSuccess} from '@/utils'
import Api from '@/apis/api';
import AgentItem from '@/components/AgentItem.vue'
import AddAgentDialog from '@/components/AddAgentDialog.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import Footer from '@/components/Footer.vue'
export default {
  name: 'HomePage',
  components: { AgentItem, AddAgentDialog, HeaderBar, Footer },
  data() {
    return {
      addAgentDialogVisible: false,
      agents: [],
    }
  },

  mounted() {
    // 获取智能体列表
    this.fetchAgentList();
  },

  methods: {
    fetchAgentList() {
      // 获取智能体列表
      Api.agent.getAgentList(({data}) => {
        if (data.code === 0) {
          this.agents = data.data
        } else {
          showDanger(data.msg)
        }
      })
    },
    showAddDialog() {
      this.addAgentDialogVisible = true
    },
    goToRoleConfig(agentId) {
      // 点击配置角色后跳转到角色配置页
      this.$router.push({path:'/role-config', query: {agentId: agentId}})
    },

    goToDevice(agentId) {
      // 点击设备后跳转到设备页
      this.$router.push({path:'/device', query: {agentId: agentId}})
    },
    handleAgentAdded(agentName) {
      // 添加智能体
      Api.agent.addAgent(agentName, ({data}) => {
        if (data.code === 0) {
          showSuccess('添加成功')
          this.fetchAgentList();
        } else {
          showDanger(data.msg)
        }
      })
    },
    handleAgentDel(agetnId){
      // 删除智能体
      Api.agent.delAgent(agetnId, (data) => {
        if (data.status === 200) {
          showSuccess('删除成功')
          this.fetchAgentList();
        } else {
          showDanger(data.msg)
        }
      })
    },
    // 搜索更新智能体列表
    handleSearchResult(filteredList) {
      this.agents = filteredList; // 更新设备列表
    }
  }
}
</script>

<style scoped>
.breadcrumbs{
  padding: 10px 0 0 5px;
}

.welcome {
  min-width: 900px;
  min-height: 506px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-image: url("@/assets/home/background.png");
  background-size: cover;
  /* 确保背景图像覆盖整个元素 */
  background-position: center;
  /* 从顶部中心对齐 */
  -webkit-background-size: cover;
  /* 兼容老版本WebKit浏览器 */
  -o-background-size: cover;
  /* 兼容老版本Opera浏览器 */
}
.add-agent {
  height: 195px;
  border-radius: 15px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(
      269.62deg,
      #e0e6fd 0%,
      #cce7ff 49.69%,
      #d3d3fe 100%
  );
}
.add-agent-bg {
  width: 100%;
  height: 100%;
  text-align: left;
  background-image: url("@/assets/home/main-top-bg.png");
  overflow: hidden;
  background-size: cover;
  /* 确保背景图像覆盖整个元素 */
  background-position: center;
  /* 从顶部中心对齐 */
  -webkit-background-size: cover;
  /* 兼容老版本WebKit浏览器 */
  -o-background-size: cover;
  box-sizing: border-box;
  /* 兼容老版本Opera浏览器 */
  .hellow-text {
    margin-left: 75px;
    color: #3d4566;
    font-size: 33px;
    font-weight: 700;
    letter-spacing: 0;
  }

  .hi-hint {
    font-weight: 400;
    font-size: 10px;
    text-align: left;
    color: #818cae;
    margin-left: 75px;
    margin-top: 5px;
  }
}

.add-agent-btn {
  display: flex;
  align-items: center;
  margin-left: 75px;
  margin-top: 15px;
  cursor: pointer;
  width: fit-content;

  .left-add {
    width: 105px;
    height: 34px;
    border-radius: 17px;
    background: #5778ff;
    color: #fff;
    font-size: 12px;
    font-weight: 500;
    text-align: center;
    line-height: 34px;
  }

  .right-add {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #5778ff;
    margin-left: -6px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
</style>