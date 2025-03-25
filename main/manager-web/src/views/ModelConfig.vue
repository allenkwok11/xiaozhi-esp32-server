<template>
  <div class="welcome">
    <HeaderBar />
    <div class="model-container">
      <el-menu :default-active="activeTab" class="el-menu-vertical-demo" @select="handleMenuSelect">
        <el-menu-item index="vad">语音活动检测</el-menu-item>
        <el-menu-item index="asr">语音识别</el-menu-item>
        <el-menu-item index="llm">大语言模型</el-menu-item>
        <el-menu-item index="intent">意图识别</el-menu-item>
        <el-menu-item index="tts">语音合成</el-menu-item>
        <el-menu-item index="memory">记忆</el-menu-item>
      </el-menu>
      <div class="content-container">
        <div class="import-export-btn">
          <el-button v-if="activeTab === 'tts'" type="primary" @click="ttsDialogVisible = true" style="margin-right: 10px;">
            模型设置
          </el-button>
          <el-button size="small" @click="handleImportExport">导入导出配置</el-button>
        </div>
        <el-main style="padding: 20px; display: flex; flex-direction: column;">
          <el-card class="model-card" shadow="always">
            <div class="model-header">
              <h2>大语言模型 (LLM)</h2>
              <el-button type="primary" @click="addModel" class="add-btn">添加</el-button>
            </div>
            <div class="model-search-operate" style="margin-bottom: 20px;">
              <el-input
                placeholder="请输入模型名称查询"
                v-model="search"
                style="width: 300px; margin-right: 10px"
              />
              <el-button @click="handleSearch">查询</el-button>
            </div>
            <el-table
              :data="modelList"
              style="width: 100%;"
              border
              stripe
              header-cell-class-name="header-cell"
            >
              <el-table-column type="selection" width="55"></el-table-column>
              <el-table-column label="模型名称" prop="candidateName"></el-table-column>
              <el-table-column label="模型编码" prop="code"></el-table-column>
              <el-table-column label="提供商" prop="supplier"></el-table-column>
              <el-table-column label="是否启用">
                <template slot-scope="scope">
                  <el-switch v-model="scope.row.isApplied" active-color="#409EFF" inactive-color="#C0CCDA"></el-switch>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <el-button
                    size="mini"
                    @click="editModel(scope.row)"
                    style="margin-right: 5px;"
                    type="text"
                    class="action-btn"
                  >修改</el-button>
                  <el-button
                    size="mini"
                    type="danger"
                    @click="deleteModel(scope.row)"
                    class="action-btn"
                  >删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="table-footer">
              <el-button @click="selectAll" class="footer-btn">全选</el-button>
              <el-button type="danger" @click="batchDelete" class="footer-btn">删除</el-button>
            </div>
          </el-card>
          <div class="pagination-container">
            <el-pagination
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[5, 10, 15]"
              :page-size="pageSize"
              layout="prev, pager, next"
              :total="total"
            />
          </div>
          <div class="copyright">
            ©2025 xiaozhi-esp32-server
          </div>
          <ModelEditDialog :visible.sync="editDialogVisible" :modelData="editModelData" @save="handleModelSave"/>
          <TtsModel :visible.sync="ttsDialogVisible" />
        </el-main>
      </div>
    </div>
  </div>
</template>

<script>
import HeaderBar from "@/components/HeaderBar.vue";
import ModelEditDialog from "@/components/ModelEditDialog.vue";
import TtsModel from "@/components/TtsModel.vue";

export default {
  components: { HeaderBar, ModelEditDialog, TtsModel },
  data() {
    return {
      activeTab: 'llm',
      search: '',
      editDialogVisible: false,
      editModelData: {},
      ttsDialogVisible: false,
      modelList: [
        { code: 'DeepSeek', candidateName: '深度求索', isApplied: true, supplier: '硅基流动' },
        { code: 'SmartAssist', candidateName: '智能助手', isApplied: false, supplier: '智脑科技' },
        { code: 'CogEngine', candidateName: '认知引擎', isApplied: true, supplier: '云智科技' },
      ],
      currentPage: 1,
      pageSize: 4,
      total: 20
    };
  },
  methods: {
    handleMenuSelect(index) {
      this.activeTab = index;
    },
    handleSearch() {
      console.log('查询：', this.search);
    },
    batchDelete() {
      console.log('批量删除');
    },
    addModel() {
      console.log('增加模型');
    },
    editModel(model) {
      this.editModelData = {
        code: model.code,
        name: model.candidateName,
        supplier: model.supplier,
      };
      this.editDialogVisible = true;
    },
    deleteModel(model) {
      console.log('删除：', model);
    },
    handleCurrentChange(page) {
      this.currentPage = page;
      console.log('当前页码：', page);
    },
    handleImportExport() {
      console.log('导入导出');
    },
    handleModelSave(formData) {
      console.log('保存的模型数据：', formData);
    },
    selectAll() {
      console.log('全选');
    }
  }
};
</script>

<style scoped>
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

.model-container {
  display: flex;
  margin-top: 25px;
}

.el-menu-vertical-demo {
  width: 250px;
  margin-right: 20px;
  background-color: #f8f9fa;
}

.content-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.model-search-operate {
  display: flex;
  align-items: center;
}

.model-search-operate > * {
  margin-right: 10px;
}

.el-table__header th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
}

.model-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.import-export-btn {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
  margin-right: 40px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.table-footer {
  margin-top: 20px;
  display: flex;
  align-items: center;
}

.footer-btn {
  margin-right: 10px;
}

.copyright {
  font-size: 12px;
  font-weight: 400;
  color: #979db1;
  margin-top: auto;
  padding-top: 30px;
  text-align: center;
}

.action-btn {
  padding: 0 8px;
}

.header-cell {
  font-weight: 500;
}

.add-btn {
  margin-right: 830px;
  padding: 8px 16px;
  border-radius: 4px;
  background-color: #409eff;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
