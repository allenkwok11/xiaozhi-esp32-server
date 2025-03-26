<template>
  <el-header class="header">
    <div style="display: flex;justify-content: space-between;margin-top: 6px;">
      <div style="display: flex;align-items: center;gap: 10px;">
        <img alt="" src="@/assets/xiaozhi-logo.png" style="width: 42px;height: 42px;"/>
        <img alt="" src="@/assets/xiaozhi-ai.png" style="width: 58px;height: 12px;"/>
        <div ref="menu-code_agent" class="ml-20 menu-btn" @click="goToPage('/home')">
          <!-- <img alt="" src="@/assets/home/equipment.png" style="width: 12px;height: 10px;"/> -->
          <i class="el-icon-cpu"></i>
          智能体
        </div>
        <div ref="menu-code_console" class="menu-btn">
          <i class="el-icon-s-grid" style="font-size: 10px;color: #979db1;"/>
          控制台
        </div>
        <div ref="menu-code_user" class="menu-btn" @click="goToPage('/user-management')">
          用户管理
        </div>
        <div ref="menu-code_model" class="menu-btn" @click="goToPage('/model-config')">
          模型配置
        </div>
        <div ref="menu-code_ota" class="menu-btn" @click="goToPage('/ota')">
          <i class="el-icon-lightning"></i>
          OTA管理
        </div>
      </div>
      <div style="display: flex;align-items: center;gap: 7px; margin-top: 2px;">
        <div class="serach-box">
          <el-input v-model="serach" placeholder="输入名称搜索.." style="border: none; background: transparent;"
                    @keyup.enter.native="handleSearch"/>
          <img alt="" src="@/assets/home/search.png"
               style="width: 14px;height: 14px;margin-right: 11px;cursor: pointer;" @click="handleSearch"/>
        </div>
        <img alt="" src="@/assets/home/avatar.png" style="width: 21px;height: 21px;"/>
        <el-dropdown trigger="click">
          <span class="el-dropdown-link">
             {{ userInfo.mobile || '加载中...' }}<i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item icon="el-icon-user" @click.native="">个人中心</el-dropdown-item>
            <el-dropdown-item icon="el-icon-key" @click.native="">修改密码</el-dropdown-item>
            <el-dropdown-item icon="el-icon-connection" @click.native="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <ChangePasswordDialog :visible.sync="isChangePasswordDialogVisible" />
  </el-header>
</template>

<script>
import userApi from '@/apis/module/user';
import ChangePasswordDialog from './ChangePasswordDialog.vue'; // 引入修改密码弹窗组件

export default {
  name: 'HeaderBar',
  components: {
    ChangePasswordDialog
  },
  props: ['devices'],  // 接收父组件设备列表
  data() {
    return {
      serach: '',
      userInfo: {
        username: '',
        mobile: ''
      },
      isChangePasswordDialogVisible: false // 控制修改密码弹窗的显示
    }
  },
  watch: {
    '$route.meta.menuCode': {
      handler(to, from) {
        const meta = this.$route.meta;
        if(meta && meta.menuCode){
          this.$nextTick(() => {
            const menu = this.$refs[`menu-code_`+ meta.menuCode]
            menu && menu.classList.add('active')
          })
        }
      },
      immediate: true,
      deep: true
    }
  },
  mounted() {
    this.fetchUserInfo()
  },
  methods: {
    handleLogout() {
      // 退出登录
        this.$store.commit('setToken','')
        this.$router.push('/login')
    },
    goToPage(path) {
      // 跳转到首页
      this.$router.replace(path)
    },
    // 获取用户信息
    fetchUserInfo() {
      userApi.getUserInfo(({data}) => {
        this.userInfo = data.data
      })
    },

    // 处理搜索
    handleSearch() {
      const searchValue = this.serach.trim();
      let filteredDevices;

      if (!searchValue) {
        // 当搜索内容为空时，显示原始完整列表
        filteredDevices = this.$parent.originalDevices;
      } else {
        // 过滤逻辑
        filteredDevices = this.devices.filter(device => {
          return device.agentName.includes(searchValue) ||
              device.ttsModelName.includes(searchValue) ||
              device.ttsVoiceName.includes(searchValue);
        });
      }

      this.$emit('search-result', filteredDevices);
    },

    // 显示修改密码弹窗
    showChangePasswordDialog() {
      this.isChangePasswordDialogVisible = true;
    }
  }
}
</script>

<style scoped>
.ml-20 {
  margin-left: 20px;
}

.menu-btn {
  padding: 8px 14px;
  border-radius: 8px;
  background: #fff;
  color: #979db1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
}
.menu-btn.active {
  background: #5778ff;
  color: #fff;
}

.header {
  background: #f6fcfe66;
  border: 1px solid #fff;
  height: 53px !important;
}

.serach-box {
  display: flex;
  width: 220px;
  height: 30px;
  border-radius: 15px;
  background-color: #f6fcfe66;
  border: 1px solid #e4e6ef;
  align-items: center;
  padding: 0 7px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-right: 15px;
}

.serach-box /deep/ .el-input__inner {
  border-radius: 15px;
  height: 100%;
  width: 100%;
  border: 0;
  background: transparent;
  padding-left: 12px;
}

.user-info {
  font-weight: 600;
  font-size: 12px;
  letter-spacing: -0.02px;
  text-align: left;
  color: #3d4566;
}

.el-dropdown-link {
  cursor: pointer;
  color: #5778ff;
}

.el-icon-arrow-down {
  font-size: 12px;
}

</style>