<template>
  <el-dialog :title="title"
    :visible.sync="visible"
    width="500px"
    class="param-dialog-wrapper"
    :append-to-body="true"
    :close-on-click-modal="false"
    :key="dialogKey"
    custom-class="custom-param-dialog"
    :show-close="false"
  >
    <div class="dialog-container">
      <div class="dialog-header">
        <h2 class="dialog-title">{{ title }}</h2>
        <button class="custom-close-btn" @click="cancel">×</button>
      </div>

      <el-form :model="form" :rules="rules" ref="form" label-width="100px" label-position="left" class="param-form">
        <el-form-item label="参数编码" prop="paramCode" class="form-item">
          <el-input v-model="form.paramCode" placeholder="请输入参数编码" class="custom-input"></el-input>
        </el-form-item>

        <el-form-item label="参数值" prop="paramValue" class="form-item">
          <el-input v-model="form.paramValue" placeholder="请输入参数值" class="custom-input"></el-input>
        </el-form-item>

        <el-form-item label="值类型" prop="valueType" class="form-item">
          <el-select v-model="form.valueType" placeholder="请选择值类型" class="custom-select">
            <el-option v-for="item in valueTypeOptions" :key="item.value" :label="item.label" :value="item.value"/>
          </el-select>
        </el-form-item>

        <el-form-item label="备注" prop="remark" class="form-item remark-item">
          <el-input type="textarea" v-model="form.remark" placeholder="请输入备注" :rows="3" class="custom-textarea"></el-input>
        </el-form-item>
      </el-form>

      <div class="dialog-footer">
        <el-button type="primary" @click="submit" class="save-btn">
          保存
        </el-button>
        <el-button @click="cancel" class="cancel-btn">
          取消
        </el-button>
      </div>
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
        valueType: 'string',
        remark: ''
      })
    }
  },
  data() {
    return {
      dialogKey: Date.now(),
      valueTypeOptions: [
        { value: 'string', label: '字符串(string)' },
        { value: 'number', label: '数字(number)' },
        { value: 'boolean', label: '布尔值(boolean)' },
        { value: 'array', label: '数组(array)' }
      ],
      rules: {
        paramCode: [
          { required: true, message: "请输入参数编码", trigger: "blur" }
        ],
        paramValue: [
          { required: true, message: "请输入参数值", trigger: "blur" }
        ],
        valueType: [
          { required: true, message: "请选择值类型", trigger: "change" }
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
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.dialogKey = Date.now();
      }
    }
  }
};
</script>

<style>
.custom-param-dialog {
  border-radius: 20px !important;
  overflow: hidden;

  .el-dialog__header {
    display: none;
  }

  .el-dialog__body {
    padding: 0 !important;
    border-radius: 20px;
  }
}
</style>

<style scoped lang="scss">
.param-dialog-wrapper {
  .dialog-container {
    padding: 20px 30px;
  }

  .dialog-header {
    position: relative;
    margin-bottom: 20px;
    text-align: center;
  }

  .dialog-title {
    font-size: 24px;
    color: #3d4566;
    margin: 0;
    padding: 0;
    font-weight: normal;
  }

  .custom-close-btn {
    position: absolute;
    top: 0;
    right: 0;
    width: 35px;
    height: 35px;
    border-radius: 50%;
    border: 2px solid #cfcfcf;
    background: none;
    font-size: 24px;
    color: #cfcfcf;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    outline: none;
    transition: all 0.2s ease;

    &:hover {
      color: #409EFF;
      border-color: #409EFF;
    }
  }

  .param-form {
    .form-item {
      margin-bottom: 20px;

      :deep(.el-form-item__label) {
        color: #3d4566;
        font-weight: normal;
        padding-right: 20px;
        text-align: right;
      }
    }

    .custom-input {
      :deep(.el-input__inner) {
        background-color: #f6f8fc;
        border-radius: 8px;
        border: 1px solid #e0e3e9;
        height: 40px;
        padding: 0 12px;
        transition: all 0.3s;

        &:focus {
          border-color: #5b8cff;
          box-shadow: 0 0 0 2px rgba(91, 140, 255, 0.2);
          background-color: #fff;
        }

        &::placeholder {
          color: #9c9f9e;
        }
      }
    }

    .custom-select {
      width: 100%;

      :deep(.el-input__inner) {
        background-color: #f6f8fc;
        border-radius: 8px;
        border: 1px solid #e0e3e9;
        height: 40px;
        transition: all 0.3s;

        &:focus {
          border-color: #5b8cff;
          box-shadow: 0 0 0 2px rgba(91, 140, 255, 0.2);
          background-color: #fff;
        }

        &::placeholder {
          color: #9c9f9e;
        }
      }
    }

    .custom-textarea {
      :deep(.el-textarea__inner) {
        background-color: #f6f8fc;
        border-radius: 8px;
        border: 1px solid #e0e3e9;
        padding: 12px;
        transition: all 0.3s;

        &:focus {
          border-color: #5b8cff;
          box-shadow: 0 0 0 2px rgba(91, 140, 255, 0.2);
          background-color: #fff;
        }

        &::placeholder {
          color: #9c9f9e;
        }
      }
    }

    .remark-item :deep(.el-form-item__label) {
      margin-top: -4px;
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: center;
    padding: 15px 0 0;
    margin-top: 10px;

    .save-btn {
      width: 120px;
      height: 40px;
      font-size: 16px;
      border-radius: 8px;
      transition: all 0.3s ease;
      background: #e6f0fd;
      color: #237ff4;
      border: 1px solid #b3d1ff;

      &:hover {
        background: #237ff4;
        color: white;
        border: none;
      }
    }

    .cancel-btn {
      width: 120px;
      height: 40px;
      font-size: 16px;
      border-radius: 8px;
      transition: all 0.3s ease;
      background: #f6f8fc;
      color: #3d4566;
      border: 1px solid #e0e3e9;
      margin-left: 20px;

      &:hover {
        background: #e9e9e9;
        border-color: #d9d9d9;
      }
    }
  }
}
</style>
