<template>
  <div class="welcome">
    <!-- 公共头部 -->
    <HeaderBar />
    <!-- 首页内容 -->
    <el-main style="padding: 20px; display: flex; flex-direction: column;">
      <!-- 面包屑-->
      <div class="breadcrumbs">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>控制台</el-breadcrumb-item>
          <el-breadcrumb-item><router-link to="/home">智能体</router-link></el-breadcrumb-item>
          <el-breadcrumb-item>设备管理</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="table-container">
         <h3 class="device-list-title">设备列表</h3>
        <el-button type="primary" class="add-device-btn" @click="handleAddDevice">
          + 添加设备
        </el-button>
        <el-table :data="devices" style="width: 100%; margin-top: 20px" border>
          <el-table-column label="设备型号" prop="device_type" flex></el-table-column>
          <el-table-column label="固件版本" prop="app_version" width="140"></el-table-column>
          <el-table-column label="MAC地址" prop="mac_address" width="220"></el-table-column>
          <el-table-column label="绑定时间" prop="bind_time" width="260"></el-table-column>
          <el-table-column label="最近对话" prop="recent_chat_time" width="100"></el-table-column>
          <el-table-column label="备注" width="220">
            <template slot-scope="scope">
              <el-input v-if="scope.row.isEdit" v-model="scope.row.remark" size="small" @blur="stopEditRemark(scope.$index)"></el-input>
              <span v-else>
                {{ scope.row.remark }}
              </span>
              <i  v-if="!scope.row.isEdit" class="el-icon-edit" @click="startEditRemark(scope.$index, scope.row)"></i>
            </template>
          </el-table-column>
          <el-table-column label="OTA升级" width="100" align="center">
            <template slot-scope="scope">
              <el-switch v-model="scope.row.ota_upgrade" size="mini" :active-value="1" :inactive-value="0" active-color="#13ce66" inactive-color="#ff4949"></el-switch>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template slot-scope="scope">
              <el-button size="mini" type="text" @click="handleUnbind(scope.row)" style="color: #ff4949">
                解绑
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <!-- 分页 -->
        <el-pagination background :page-size="10" :pager-count="5" layout="prev, pager, next" :total="150" style="margin-top: 4px;text-align: right;"></el-pagination>
      </div>
      <!-- 底部 -->
      <Footer :visible="true" />
      <!-- 添加设备对话框 -->
      <AddDeviceDialog :visible.sync="addDeviceDialogVisible" @added="handleDeviceAdded" />
    </el-main>
  </div>
</template>

<script>
import {getUUID, goToPage, showDanger, showSuccess} from '@/utils'
import Api from '@/apis/api';
import AddDeviceDialog from '@/components/AddDeviceDialog.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'DevicePage',
  components: { AddDeviceDialog, HeaderBar, Footer },
  data() {
    return {
      addDeviceDialogVisible: false,
      devices: [],
      agentId: this.$route.query.agentId
    }
  },
  mounted() {
    this.getDeviceList();
  },
  methods: {
    // 获取设备列表
    getDeviceList() {
      Api.device.getDeviceList(this.agentId, ({data}) => {
        if (data.code === 0) {
          this.devices = data.data[0].list.map((item)=>{item.isEdit=false;return item;})
        } else {
          showDanger(data.msg)
        }
      })
    },
    handleAddDevice() {
      // 添加设备逻辑
      this.addDeviceDialogVisible = true;
    },
    startEditRemark(index, row) {
      this.devices[index].isEdit = true;
    },
    stopEditRemark(index) {
      this.devices[index].isEdit = false;
    },
    handleUnbind(device) {
      // 解绑逻辑
      console.log('解绑设备', device);
    },
    handleDeviceAdded(deviceCode) {
      // 根据需要处理添加设备后逻辑，比如刷新设备列表等
      console.log('设备验证码：', deviceCode)
    },
  }
};
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
  background-position: center;
  -webkit-background-size: cover;
  -o-background-size: cover;
}

.table-container {
  background: #f9fafc;
  padding: 20px;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-top: 15px;
}

.add-device-btn {
  float: right;
  background: #409eff;
  border: none;
  border-radius: 10px;
  width: 105px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  gap: 8px;
  margin-bottom: 15px;
  &:hover {
    background: #3a8ee6;
  }
}

.device-list-title {
  float: left;
  font-size: 18px;
  font-weight: 700;
  margin: 5px;
  color: #2c3e50;
}

.el-icon-edit {
  color: #409eff;
  cursor: pointer;
  font-size: 14px;
  vertical-align: middle;
}

</style>