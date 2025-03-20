<template>
  <div class="welcome">
      <!-- 公共头部 -->
      <HeaderBar :devices="devices" @search-result="handleSearchResult" />
      <el-main style="padding: 20px;display: flex;flex-direction: column;">
        <div>
          <!-- 首页内容 -->
          <div class="add-device">
            <div class="add-device-bg">
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
              <div class="add-device-btn" @click="showAddDialog">
                <div class="left-add">
                  添加设备
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
              <el-breadcrumb-item><router-link to="/home">智能体</router-link></el-breadcrumb-item>
              <el-breadcrumb-item>设备管理</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <!-- 设备列表-->
          <el-card class="box-card" shadow="hover" style="margin-top: 20px;">
            <div slot="header" class="clearfix" style="text-align: left;">
              <span>设备列表</span>
            </div>
            <div style="display: flex;flex-direction: column;align-items: end;padding: 0 20px;gap: 10px;">
              <el-table :data="devices" style="width: 100%">
                <el-table-column prop="device_type" label="设备型号">
                </el-table-column>
                <el-table-column prop="app_version" label="固件版本" width="180">
                </el-table-column>
                <el-table-column prop="mac_address" label="MAC地址">
                </el-table-column>
                <el-table-column prop="bind_time" label="绑定时间">
                </el-table-column>
                <el-table-column prop="recent_chat_time" label="最近对话">
                </el-table-column>
                <el-table-column prop="desc" label="备注">
                  <template slot-scope="scope">
                    <div v-if="scope.row.isEdit">
                      <el-input
                        placeholder="请输入内容"
                        v-model="scope.row.desc"
                        @blur="handleEditSave(scope.row)"
                        clearable>
                      </el-input>
                    </div>
                    <div v-else>
                      {{ scope.row.desc }}
                      <i class="el-icon-edit" style="color:#1890ff;cursor: pointer;" @click="handleEdit(scope.row)"></i>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="OTA升级" width="100" align="center">
                  <template slot-scope="scope">
                    <el-switch v-model="scope.row.ota_upgrade" :active-value="1" :inactive-value="0" active-color="#13ce66" inactive-color="#ff4949">
                    </el-switch>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80" align="center">
                  <template slot-scope="scope">
                    <el-button size="mini" type="danger">解绑</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-pagination
                :page-size="10"
                :pager-count="5"
                layout="prev, pager, next"
                :total="150">
              </el-pagination>
          </div>
          </el-card>
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
    showAddDialog() {
      this.addDeviceDialogVisible = true
    },
    goToRoleConfig() {
      // 点击配置角色后跳转到角色配置页
      this.$router.push('/role-config')
    },
    handleDeviceAdded(deviceCode) {
      // 根据需要处理添加设备后逻辑，比如刷新设备列表等
      console.log('设备验证码：', deviceCode)
    },
    handleEdit(row) {
      row.isEdit=true
    },
    handleEditSave(row) {
      row.isEdit=false
    },
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
.add-device {
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
.add-device-bg {
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

.add-device-btn {
  display: flex;
  align-items: center;
  margin-left: 75px;
  margin-top: 15px;
  cursor: pointer;

  .left-add {
    width: 105px;
    height: 34px;
    border-radius: 17px;
    background: #5778ff;
    color: #fff;
    font-size: 10px;
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