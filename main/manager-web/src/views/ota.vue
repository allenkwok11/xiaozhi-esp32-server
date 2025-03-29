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
          <el-breadcrumb-item>OTA管理</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="table-container">
         <h3 class="device-list-title">OTA设备列表</h3>
        <el-button type="primary" class="add-device-btn" @click="handleAddDeviceOta()">
          + 添加设备
        </el-button>
        <el-table :data="otaList" style="width: 100%; margin-top: 20px" border>
          <el-table-column label="设备型号" prop="board" flex></el-table-column>
          <el-table-column label="固件版本" prop="appVersion" width="140"></el-table-column>
          <el-table-column label="升级地址" prop="url"></el-table-column>
          <el-table-column label="是否启用" width="100" align="center">
            <template slot-scope="scope">
              <el-switch v-model="scope.row.isEnabled" size="mini" :active-value="1" :inactive-value="0" active-color="#13ce66" inactive-color="#ff4949" @change="handleToggleEnabled(scope.row.id, $event)"></el-switch>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template slot-scope="scope">
              <el-button size="mini" type="text" @click="handleAddDeviceOta(scope.row)" style="color: #ff4949">
                编辑
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <!-- 分页 -->
        <el-pagination background :current-page="page.pageNo" :page-size="page.pageSize" :pager-count="5" layout="prev, pager, next" :total="page.total" style="margin-top: 4px;text-align: right;"></el-pagination>
      </div>
    </el-main>
    <!-- 底部 -->
    <Footer :visible="true" />
    <!-- 添加设备OTA对话框 -->
    <AddDeviceOtaDialog :visible.sync="addDeviceOtaDialogVisible" :data="otaData" @confirmSave="handleSaveDeviceOta" @confirmUpdate="handleUpdateDeviceOta" />
  </div>
</template>

<script>
import {getUUID, goToPage, showDanger, showSuccess} from '@/utils'
import Api from '@/apis/api';
import AddDeviceOtaDialog from '@/components/AddDeviceOtaDialog.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'DeviceOtaPage',
  components: { AddDeviceOtaDialog, HeaderBar, Footer },
  data() {
    return {
      addDeviceOtaDialogVisible: false,
      otaList: [],
      otaData: {},
      page: {
        pageNo: 1,
        pageSize: 10,
        total: 0
      }
    }
  },
  mounted() {
    this.fetchDeviceOtaList();
  },
  methods: {
    // 获取设备列表
    fetchDeviceOtaList() {
      Api.ota.getOtaList(this.page, ({data}) => {
        if (data.code === 0) {
          this.page = {...this.page,total:parseInt(data.data.total)}
          this.otaList = data.data.records
        } else {
          showDanger(data.msg)
        }
      })
    },
    handleAddDeviceOta(ota) {
      if (ota) {
        this.otaData = ota
      }
      // 添加设备逻辑
      this.addDeviceOtaDialogVisible = true;
    },
    handleSaveDeviceOta(ota) {
      console.log('添加设备', ota);
      Api.ota.saveOta(ota, ({data}) => {
        if (data.code === 0) {
          showSuccess('添加成功')
          this.fetchDeviceOtaList()
        } else {
          showDanger(data.msg)
        }
        this.otaData = {}
      })
    },
    handleUpdateDeviceOta(ota) {
      // 解绑逻辑
      console.log('修改设备', ota);
      Api.ota.updateOta(ota, ({data}) => {
        if (data.code === 0) {
          showSuccess('修改成功')
          this.fetchDeviceOtaList()
        } else {
          showDanger(data.msg)
        }
        this.otaData = {}
      })
    },
    handleToggleEnabled(id, isEnabled) {
      // 启用禁用逻辑
      Api.ota.toggleEnabled({id, isEnabled}, ({data}) => {
        if (data.code === 0) {
          showSuccess('更新成功')
          this.fetchDeviceOtaList()
        } else {
          showDanger(data.msg)
        }
      })
    }
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