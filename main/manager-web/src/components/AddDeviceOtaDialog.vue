<template>
  <el-dialog :visible.sync="visible" width="600px" center :close-on-click-modal="false" :close-on-press-escape="false">
    <div style="margin: 0 10px 10px;display: flex;align-items: center;gap: 10px;font-weight: 700;font-size: 20px;text-align: left;color: #3d4566;">
      <div style="width: 40px;height: 40px;border-radius: 50%;background: #5778ff;display: flex;align-items: center;justify-content: center;">
        <i class="el-icon-lightning" style="color: #fff;"></i>
      </div>
      {{ data.id?'编辑':'添加' }}设备
    </div>
    <div style="height: 1px;background: #e8f0ff;" />

    <div style="margin: 22px 15px;">
      <el-form ref="form" :model="data" label-width="80px">
        <el-form-item label="设备型号" prop="board" :rules="[{ required: true, message: '请输入设备型号', trigger: 'blur' }]">
          <el-input v-model="data.board" placeholder="请输入设备型号..."></el-input>
        </el-form-item>
        <el-form-item label="固件版本" prop="appVersion"  :rules="[{ required: true, message: '请输入固件版本', trigger: 'blur' }]">
          <el-input v-model="data.appVersion" placeholder="请输入固件版本..."></el-input>
        </el-form-item>
        <el-form-item label="升级地址" prop="url" :rules="[{ required: true, message: '请输入升级地址', trigger: 'blur' },{ type: 'url', message: '请输入正确的升级地址', trigger: 'blur' }]">
          <el-input type="textarea" v-model="data.url" placeholder="请输入升级地址..."></el-input>
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="data.isEnabled" size="mini" :active-value="1" :inactive-value="0" active-color="#13ce66" inactive-color="#ff4949"></el-switch>
        </el-form-item>
        <el-form-item label-width="0">
          <div style="display: flex;margin: 15px 15px;gap: 7px;">
            <div class="dialog-btn" @click="confirm">
              确定
            </div>
            <div class="dialog-btn" style="background: #e6ebff;border: 1px solid #adbdff;color: #5778ff;" @click="cancel">
              取消
            </div>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </el-dialog>
</template>

<script>
export default {
  name: 'AddDeviceOtaDialog',
  props: {
    visible: { type: Boolean, required: true },
    data: { type: Object, 
      default: () => ({
        id: "",
        board: "",
        appVersion: "",
        url: "",
        isEnabled: 1
      })
    }
  },
  data() {
    return {}
  },
  methods: {
    confirm() {
      this.$refs['form'].validate((valid) => {
          if (valid) {
            this.$emit(this.data.id?'confirmUpdate':'confirmSave',this.data)
            this.$emit('update:visible', false)
          } else {
            return false;
          }
        });
    },
    cancel() {
      this.$emit('update:visible', false)
    }
  }
}
</script>

<style scoped>
.dialog-btn {
  cursor: pointer;
  flex: 1;
  border-radius: 23px;
  background: #5778ff;
  height: 40px;
  font-weight: 500;
  font-size: 12px;
  color: #fff;
  line-height: 40px;
  text-align: center;
}

::v-deep .el-dialog {
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
::v-deep .el-dialog__headerbtn {
  display: none;
}
::v-deep .el-dialog__body {
  padding: 4px 6px;
}
::v-deep .el-dialog__header{
  padding: 10px;
}

</style>