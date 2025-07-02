<template>
  <el-dialog :visible="visible" :close-on-click-modal="false" @update:visible="handleVisibleChange" width="57%" center custom-class="custom-dialog"
    :show-close="false" class="center-dialog">

    <div style="margin: 0 18px; text-align: left; padding: 10px; border-radius: 10px;">
      <div style="font-size: 30px; color: #3d4566; margin-top: -15px; margin-bottom: 20px; text-align: center;">
        {{ title }}
      </div>

      <button class="custom-close-btn" @click="handleClose">×</button>

      <el-form :model="form" label-width="100px" :rules="rules" ref="form" class="custom-form">
        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
          <el-form-item label="Type" prop="modelType" style="flex: 1;">
            <el-select v-model="form.modelType" placeholder="please select type" class="custom-input-bg" style="width: 100%;">
              <el-option v-for="item in modelTypes" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="code" prop="providerCode" style="flex: 1;">
            <el-input v-model="form.providerCode" placeholder="please enter provider code" class="custom-input-bg"></el-input>
          </el-form-item>
        </div>

        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
          <el-form-item label="Name" prop="name" style="flex: 1;">
            <el-input v-model="form.name" placeholder="please enter provider name" class="custom-input-bg"></el-input>
          </el-form-item>
          <el-form-item label="Sort" prop="sort" style="flex: 1;">
            <el-input-number v-model="form.sort" :min="0" controls-position="right" class="custom-input-bg"
              style="width: 100%;"></el-input-number>
          </el-form-item>
        </div>

        <div style="font-size: 20px; font-weight: bold; color: #3d4566; margin-bottom: 15px;">
          field configuration
          <div style="display: inline-block; float: right;">
            <el-button type="primary" @click="addField" size="small" style="background: #5bc98c; border: none;"
              :disabled="hasIncompleteFields">
              Add
            </el-button>
            <el-button type="primary" @click="toggleSelectAllFields" size="small"
              style="background: #5f70f3; border: none; margin-left: 10px;">
              {{ isAllFieldsSelected ? 'unselect all' : 'select all' }}
            </el-button>
            <el-button type="danger" @click="batchRemoveFields" size="small"
              style="background: red; border: none; margin-left: 10px;">
              Batch Delete
            </el-button>
          </div>
        </div>
        <div style="height: 2px; background: #e9e9e9; margin-bottom: 22px;"></div>

        <div class="fields-container">
          <el-table :data="form.fields" style="width: 100%;" border size="medium" :key="tableKey">
            <el-table-column label="select" align="center" width="50">
              <template slot-scope="scope">
                <el-checkbox v-model="scope.row.selected" @change="handleFieldSelectChange"></el-checkbox>
              </template>
            </el-table-column>
            <el-table-column label="field key">
              <template slot-scope="scope">
                <template v-if="scope.row.editing">
                  <el-input v-model="scope.row.key" placeholder="Field Key"></el-input>
                </template>
                <template v-else>
                  {{ scope.row.key }}
                </template>
              </template>
            </el-table-column>
            <el-table-column label="Field Label">
              <template slot-scope="scope">
                <template v-if="scope.row.editing">
                  <el-input v-model="scope.row.label" placeholder="Field Label"></el-input>
                </template>
                <template v-else>
                  {{ scope.row.label }}
                </template>
              </template>
            </el-table-column>
            <el-table-column label="Field Type">
              <template slot-scope="scope">
                <template v-if="scope.row.editing">
                  <el-select v-model="scope.row.type" placeholder="type">
                    <el-option label="string" value="string"></el-option>
                    <el-option label="number" value="number"></el-option>
                    <el-option label="boolean" value="boolean"></el-option>
                    <el-option label="dictionary" value="dict"></el-option>
                    <el-option label="Semicolon-separated list" value="array"></el-option>
                  </el-select>
                </template>
                <template v-else>
                  {{ getTypeLabel(scope.row.type) }}
                </template>
              </template>
            </el-table-column>
            <el-table-column label="Default Value">
              <template slot-scope="scope">
                <template v-if="scope.row.editing">
                  <el-input v-model="scope.row.default" placeholder="please enter default value"></el-input>
                </template>
                <template v-else>
                  {{ scope.row.default }}
                </template>
              </template>
            </el-table-column>
            <el-table-column label="Operation" width="150" align="center">
              <template slot-scope="scope">
                <el-button v-if="!scope.row.editing" type="primary" size="mini" @click="startEditing(scope.row)">
                  Edit
                </el-button>
                <el-button v-else type="success" size="mini" @click="stopEditing(scope.row)">
                  Complete
                </el-button>
                <el-button type="danger" size="mini" @click="removeField(scope.$index)">
                  Delete
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form>
    </div>

    <div style="display: flex; justify-content: center;">
      <el-button type="primary" @click="submit" class="save-btn" :loading="saving">save</el-button>
    </div>
  </el-dialog>
</template>

<script>
export default {
  props: {
    title: String,
    visible: Boolean,
    form: Object,
    modelTypes: Array
  },
  data() {
    return {
      saving: false,
      rules: {
        modelType: [{ required: true, message: 'please select type', trigger: 'change' }],
        providerCode: [{ required: true, message: 'please select provider code', trigger: 'blur' }],
        name: [{ required: true, message: 'please select provider name', trigger: 'blur' }]
      },
      isAllFieldsSelected: false,
      tableKey: 0 // 用于强制表格重新渲染
    };
  },
  computed: {
    hasIncompleteFields() {
      return this.form.fields && this.form.fields.some(field =>
        !field.key || !field.label || !field.type
      );
    }
  },
  methods: {
    getTypeLabel(type) {
      const typeMap = {
        'string': 'String',
        'number': 'Number',
        'boolean': 'Boolean',
        'dict': 'Dictionary',
        'array': 'Semicolon-separated list'
      };
      return typeMap[type];
    },

    startEditing(row) {
      this.$set(row, 'editing', true);
    },

    stopEditing(row) {
      this.$set(row, 'editing', false);

      const index = this.form.fields.indexOf(row);
      if (index > -1) {
        this.form.fields.splice(index, 1);
        this.form.fields.push(row);
        this.forceTableRerender();
      }
    },

    handleFieldSelectChange() {
      this.isAllFieldsSelected = this.form.fields.length > 0 &&
        this.form.fields.every(field => field.selected);
    },

    toggleSelectAllFields() {
      this.isAllFieldsSelected = !this.isAllFieldsSelected;
      this.form.fields = this.form.fields.map(field => ({
        ...field,
        selected: this.isAllFieldsSelected
      }));
    },

    handleVisibleChange(val) {
      this.$emit('update:visible', val);
      if (!val) {
        this.resetForm();
      }
    },

    handleClose() {
      this.resetForm();
      this.$emit('update:visible', false);
      this.$emit('cancel');
    },

    addField() {
      if (this.hasIncompleteFields) {
        this.$message.warning({
          message: 'please complete the editing of current field first',
          showClose: true
        });
        return;
      }

      this.form.fields.unshift({
        key: '',
        label: '',
        type: 'string',
        default: '',
        selected: false,
        editing: true
      });
      this.forceTableRerender();
    },

    removeField(index) {
      this.$confirm('confirm to delete this field?', 'note', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(() => {
        this.form.fields = this.form.fields.filter((_, i) => i !== index);
        this.updateSelectAllStatus();
        this.forceTableRerender();
        this.$message.success({
          message: 'delete successfully',
          showClose: true
        });
      }).catch(() => {
        this.$message.info({
          message: 'deletion cancelled',
          showClose: true
        });
      });
    },

    batchRemoveFields() {
      const selectedFields = this.form.fields.filter(field => field.selected);
      if (selectedFields.length === 0) {
        this.$message.warning({
          message: 'please select field to be deleted',
          showClose: true
        });
        return;
      }
      this.$confirm(`confirm to delete ${selectedFields.length} selected fields?`, 'note', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(() => {
        this.form.fields = this.form.fields.filter(field => !field.selected);
        this.isAllFieldsSelected = false;
        this.forceTableRerender();
        this.$message.success({
          message: `delete ${selectedFields.length} field successfully`,
          showClose: true
        });
      }).catch(() => {
        this.$message.info({
          message: 'deletion cancelled',
          showClose: true
        });
      });
    },

    updateSelectAllStatus() {
      this.isAllFieldsSelected = this.form.fields.length > 0 &&
        this.form.fields.every(field => field.selected);
    },

    forceTableRerender() {
      this.tableKey += 1; // 改变key值强制表格重新渲染
    },

    submit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          const editingField = this.form.fields.find(field => field.editing);
          if (editingField) {
            this.$message.warning({
              message: 'please complete the edit of  current field',
              showClose: true
            });
            return;
          }

          this.form.fields = this.form.fields.map(field => ({
            ...field,
            selected: false
          }));
          this.isAllFieldsSelected = false;

          this.saving = true;
          this.$emit('submit', {
            form: this.form,
            done: () => {
              this.saving = false;
              this.resetForm();
            }
          });
        }
      });
    },

    resetForm() {
      this.$refs.form.resetFields();
      if (this.form.fields) {
        this.form.fields.forEach(field => {
          field.selected = false;
          field.editing = false;
        });
      }
      this.isAllFieldsSelected = false;
      this.forceTableRerender();
    },

  },
  watch: {
    visible(val) {
      if (!val) {
        this.resetForm();
      }
    }
  }
};
</script>

<style lang="scss" scoped>
::v-deep .custom-dialog.el-dialog {
  margin-top: 0 !important;
  border-radius: 20px !important;
}

::v-deep .custom-dialog .el-dialog__header {
  padding: 0;
  border-bottom: none;
}

.custom-close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  border: 2px solid #cfcfcf;
  background: none;
  font-size: 30px;
  font-weight: lighter;
  color: #cfcfcf;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  padding: 0;
  outline: none;
}

.custom-close-btn:hover {
  color: #409EFF;
  border-color: #409EFF;
}

.custom-form .el-form-item {
  margin-bottom: 20px;
}

.custom-form .el-form-item__label {
  color: #3d4566;
  font-weight: normal;
  text-align: right;
  padding-right: 20px;
}

.custom-input-bg .el-input__inner {
  background-color: #f6f8fc;
  height: 32px;
}

.custom-input-bg .el-input__inner::-webkit-input-placeholder {
  color: #9c9f9e;
}

.fields-container {
  margin-bottom: 20px;
}

.save-btn {
  background: #e6f0fd;
  color: #237ff4;
  border: 1px solid #b3d1ff;
  width: 150px;
  height: 40px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.save-btn:hover {
  background: linear-gradient(to right, #237ff4, #9c40d5);
  color: white;
  border: none;
}

.el-table {
  border-radius: 4px;
}

.el-table::before {
  display: none;
}

.el-table th,
.el-table td {
  padding: 8px 0;
}

.el-button.is-circle {
  border-radius: 2px;
}
</style>