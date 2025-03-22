<template>
  <el-dialog :visible.sync="visible" width="400px" center>
    <div style="margin: 0 10px 10px;display: flex;align-items: center;gap: 10px;font-weight: 700;font-size: 20px;text-align: left;color: #3d4566;">
      <div style="width: 40px;height: 40px;border-radius: 50%;background: #5778ff;display: flex;align-items: center;justify-content: center;">
        <img src="@/assets/home/equipment.png" alt="" style="width: 18px;height: 15px;" />
      </div>
      添加智能体
    </div>
    <div style="height: 1px;background: #e8f0ff;" />
    <div style="margin: 22px 15px;">
      <div style="font-weight: 400;font-size: 14px;text-align: left;color: #3d4566;">
        <div style="color: red;display: inline-block;">*</div>智能体名称：
      </div>
      <div style="margin-top: 12px;">
        <el-input placeholder="请输入智能体名称.." v-model="agentName" />
      </div>
    </div>
    <div style="display: flex;margin: 15px 15px;gap: 7px;">
      <div class="dialog-btn" @click="confirm">
        确定
      </div>
      <div class="dialog-btn"
           style="background: #e6ebff;border: 1px solid #adbdff;color: #5778ff;"
           @click="cancel">
        取消
      </div>
    </div>
  </el-dialog>
</template>

<script>
import userApi from '@/apis/module/user';


export default {
  name: 'AddAgentDialog',
  props: {
    visible: { type: Boolean, required: true }
  },
  data() {
    return { agentName: "" }
  },
  methods: {
    confirm() {
      if (!this.agentName.trim()) {
        this.$message.error('请输入智能体名称');
        return;
      }
      userApi.addAgent(this.agentName, (res) => {
        this.$message.success('添加成功');
        this.$emit('confirm', res);
        this.$emit('update:visible', false);
        this.agentName = "";
      });
    },
    cancel() {
      this.$emit('update:visible', false)
      this.agentName = ""
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