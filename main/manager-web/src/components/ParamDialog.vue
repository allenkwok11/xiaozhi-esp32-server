<template>
  <el-dialog :title="title" :visible.sync="visible" width="500px">
    <el-form :model="form" :rules="rules" ref="form" label-width="100px">
      <el-form-item label="参数编码" prop="paramCode">
        <el-input v-model="form.paramCode" placeholder="请输入参数编码"></el-input>
      </el-form-item>
      <el-form-item label="参数值" prop="paramValue">
        <el-input v-model="form.paramValue" placeholder="请输入参数值"></el-input>
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input type="textarea" v-model="form.remark" placeholder="请输入备注"></el-input>
      </el-form-item>
    </el-form>
    <div slot="footer" class="dialog-footer">
      <el-button @click="cancel">取 消</el-button>
      <el-button type="primary" @click="submit">确 定</el-button>
    </div>
  </el-dialog>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: '新增参数'
    },
    visible: {
      type: Boolean,
      default: false
    },
    form: {
      type: Object,
      default: () => ({
        id: null,
        paramCode: '',
        paramValue: '',
        remark: ''
      })
    }
  },
  data() {
    return {
      rules: {
        paramCode: [
          { required: true, message: "请输入参数编码", trigger: "blur" }
        ],
        paramValue: [
          { required: true, message: "请输入参数值", trigger: "blur" }
        ]
      }
    };
  },
  methods: {
    submit() {
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.$emit('submit', this.form);
        }
      });
    },
    cancel() {
      this.$emit('cancel');
    }
  }
};
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
