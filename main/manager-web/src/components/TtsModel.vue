<template>
  <el-dialog
      :visible.sync="localVisible"
      width="75%"
      @close="handleClose"
      :show-close="false"
      :append-to-body="true">
    <button class="custom-close-btn" @click="handleClose">
      ×
    </button>
    <div class="scroll-wrapper">
      <div
          class="table-container"
          ref="tableContainer"
          @scroll="handleScroll"
      >
        <el-table
            :data="filteredTtsModels"
            style="width: 100%;"
            class="data-table"
            header-row-class-name="table-header"
            :fit="true">
          <el-table-column label="选择" width="50" align="center">
            <template slot-scope="scope">
              <el-checkbox v-model="scope.row.selected"></el-checkbox>
            </template>
          </el-table-column>
          <el-table-column label="音色编码" align="center" min-width="50">
            <template slot-scope="scope">
              <el-input v-if="scope.row.editing" v-model="scope.row.voiceCode"></el-input>
              <span v-else>{{ scope.row.voiceCode }}</span>
            </template>
          </el-table-column>
          <el-table-column label="音色名称" align="center" min-width="50">
            <template slot-scope="scope">
              <el-input v-if="scope.row.editing" v-model="scope.row.voiceName"></el-input>
              <span v-else>{{ scope.row.voiceName }}</span>
            </template>
          </el-table-column>
          <el-table-column label="语言类型" align="center" min-width="50">
            <template slot-scope="scope">
              <el-input v-if="scope.row.editing" v-model="scope.row.languageType"></el-input>
              <span v-else>{{ scope.row.languageType }}</span>
            </template>
          </el-table-column>
          <el-table-column label="试听" align="center" min-width="225" class-name="audio-column">
            <template slot-scope="scope">
              <div class="custom-audio-container">
                <AudioPlayer :audioUrl="getAudioUrl(scope.row.voiceCode)"/>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="备注" align="center" min-width="120">
            <template slot-scope="scope">
              <el-input
                  v-if="scope.row.editing"
                  type="textarea"
                  :rows="1"
                  autosize
                  v-model="scope.row.remark"
                  placeholder="这里是备注"
                  class="remark-input"></el-input>
              <span v-else>{{ scope.row.remark }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="150">
            <template slot-scope="scope">
              <template v-if="!scope.row.editing">
                <el-button type="primary" size="mini" @click="startEdit(scope.row)"
                           style="background: #5cca8e;border:None">编辑
                </el-button>
                <el-button type="primary" size="mini" @click="deleteRow(scope.row)" style="background: red;border:None">
                  删除
                </el-button>
              </template>
              <el-button
                  v-else
                  type="success"
                  size="mini"
                  @click="saveEdit(scope.row)"
                  class="save-Tts">保存
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 自定义滚动条 -->
      <div class="custom-scrollbar" ref="scrollbar">
        <div class="custom-scrollbar-track" ref="scrollbarTrack" @click="handleTrackClick">
          <div class="custom-scrollbar-thumb" ref="scrollbarThumb" @mousedown="startDrag"></div>
        </div>
      </div>
    </div>
    <div class="action-buttons">
      <el-button type="primary" size="mini" @click="toggleSelectAll" style="background: #606ff3;border: None">
        {{ selectAll ? '取消全选' : '全选' }}
      </el-button>
      <el-button type="primary" size="mini" @click="addNew" style="background: #f6cf79;border: None; color: #000012">新增</el-button>
      <el-button type="primary" size="mini" @click="batchDelete" style="background: red;border:None">删除</el-button>
    </div>
  </el-dialog>
</template>

<script>
import AudioPlayer from './AudioPlayer.vue'

export default {
  components: {AudioPlayer},
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      localVisible: this.visible,
      activeModel: 'EdgeTTS',
      searchQuery: '',
      editDialogVisible: false,
      editVoiceData: {},
      ttsModels: [
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: 'AAAA国少', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
        {voiceCode: 'wawaxiaohe', voiceName: '湾湾小何', languageType: '中文', remark: '', selected: false},
      ],
      currentPage: 1,
      pageSize: 4,
      total: 20,
      isDragging: false,
      startY: 0,
      scrollTop: 0,
      selectAll: false,
      selectedRows: []
    };
  },
  watch: {
    visible(newVal) {
      this.localVisible = newVal;
      if (newVal) {
        this.$nextTick(() => {
          this.updateScrollbar();
        });
      }
    },
    filteredTtsModels() {
      this.$nextTick(() => {
        this.updateScrollbar();
      });
    }
  },
  computed: {
    filteredTtsModels() {
      return this.ttsModels.filter(model =>
          model.voiceName.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  mounted() {
    this.updateScrollbar();
    window.addEventListener('resize', this.updateScrollbar);
    window.addEventListener('mouseup', this.stopDrag);
    window.addEventListener('mousemove', this.handleDrag);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateScrollbar);
    window.removeEventListener('mouseup', this.stopDrag);
    window.removeEventListener('mousemove', this.handleDrag);
  },
  methods: {
    handleClose() {
      this.localVisible = false;
      this.$emit('update:visible', false);
      this.ttsModels.forEach(model => {
        model.remark = '';
      });
    },
    getAudioUrl(voiceCode) {
      return `https://music.163.com/song/media/outer/url?id=5257138.mp3`;
    },
    updateScrollbar() {
      const container = this.$refs.tableContainer;
      const scrollbarThumb = this.$refs.scrollbarThumb;
      const scrollbarTrack = this.$refs.scrollbarTrack;

      if (!container || !scrollbarThumb || !scrollbarTrack) return;

      const {scrollHeight, clientHeight} = container;
      const trackHeight = scrollbarTrack.clientHeight;
      const thumbHeight = Math.max((clientHeight / scrollHeight) * trackHeight, 20);

      scrollbarThumb.style.height = `${thumbHeight}px`;
      this.updateThumbPosition();
    },
    updateThumbPosition() {
      const container = this.$refs.tableContainer;
      const scrollbarThumb = this.$refs.scrollbarThumb;
      const scrollbarTrack = this.$refs.scrollbarTrack;

      if (!container || !scrollbarThumb || !scrollbarTrack) return;

      const {scrollHeight, clientHeight, scrollTop} = container;
      const trackHeight = scrollbarTrack.clientHeight;
      const thumbHeight = scrollbarThumb.clientHeight;
      const maxTop = trackHeight - thumbHeight;
      const thumbTop = (scrollTop / (scrollHeight - clientHeight)) * (trackHeight - thumbHeight);

      scrollbarThumb.style.top = `${Math.min(thumbTop, maxTop)}px`;
    },
    handleScroll() {
      this.updateThumbPosition();
    },
    startDrag(e) {
      this.isDragging = true;
      this.startY = e.clientY;
      this.scrollTop = this.$refs.tableContainer.scrollTop;
      e.preventDefault();
    },
    stopDrag() {
      this.isDragging = false;
    },
    handleDrag(e) {
      if (!this.isDragging) return;

      const container = this.$refs.tableContainer;
      const scrollbarTrack = this.$refs.scrollbarTrack;
      const scrollbarThumb = this.$refs.scrollbarThumb;
      const deltaY = e.clientY - this.startY;
      const trackHeight = scrollbarTrack.clientHeight;
      const thumbHeight = scrollbarThumb.clientHeight;
      const maxScrollTop = container.scrollHeight - container.clientHeight;

      const scrollRatio = (trackHeight - thumbHeight) / maxScrollTop;
      container.scrollTop = this.scrollTop + deltaY / scrollRatio;
    },
    handleTrackClick(e) {
      const container = this.$refs.tableContainer;
      const scrollbarTrack = this.$refs.scrollbarTrack;
      const scrollbarThumb = this.$refs.scrollbarThumb;

      if (!container || !scrollbarTrack || !scrollbarThumb) return;

      const trackRect = scrollbarTrack.getBoundingClientRect();
      const thumbHeight = scrollbarThumb.clientHeight;
      const clickPosition = e.clientY - trackRect.top;
      const thumbCenter = clickPosition - thumbHeight / 2;

      const trackHeight = scrollbarTrack.clientHeight;
      const maxTop = trackHeight - thumbHeight;
      const newTop = Math.max(0, Math.min(thumbCenter, maxTop));

      scrollbarThumb.style.top = `${newTop}px`;
      container.scrollTop = (newTop / (trackHeight - thumbHeight)) * (container.scrollHeight - container.clientHeight);
    },
    // 按钮组
    startEdit(row) {
      row.editing = true;
      this.$set(row, 'originalData', {...row});
    },

    saveEdit(row) {
      row.editing = false;
      delete row.originalData;
      // 这里可以添加保存到服务器的逻辑
    },

    toggleSelectAll() {
      this.selectAll = !this.selectAll;
      this.filteredTtsModels.forEach(row => {
        row.selected = this.selectAll;
      });
    },

    addNew() {
      const newRow = {
        voiceCode: '新编码',
        voiceName: '新音色',
        languageType: '中文',
        remark: '',
        selected: false,
        editing: true
      };
      this.ttsModels.unshift(newRow);
    },

    deleteRow(row) {
      const index = this.ttsModels.indexOf(row);
      this.ttsModels.splice(index, 1);
    },

    batchDelete() {
      this.ttsModels = this.ttsModels.filter(row => !row.selected);
    }
  }
};
</script>

<style scoped>

::v-deep .el-dialog {
  border-radius: 8px !important;
  overflow: hidden;
  top: 8vh !important;
}

::v-deep .el-dialog__header {
  display: none !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* 表格样式 */
::v-deep .data-table .el-table__header th {
  color: black;
  padding: 6px 0 !important;
}

::v-deep .data-table .el-table__row td {
  padding: 8px 0 12px !important;
}

::v-deep .data-table {
  border: none !important;
}

::v-deep .data-table.el-table::before {
  display: none !important;
}

::v-deep .data-table .el-table__header-wrapper {
  border-bottom: 2px solid #f1f2fb !important;
}

::v-deep .data-table .el-table__body-wrapper .el-table__body td {
  border: none !important;
}

/* 关闭按钮 */
.custom-close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 30px;
  height: 30px;
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

/* 备注文本 */
::v-deep .remark-input .el-textarea__inner {
  background-color: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
  padding: 8px 12px;
  resize: none;
  max-height: 40px !important;
  line-height: 1.5;
}

::v-deep .remark-input .el-textarea__inner::placeholder {
  color: black !important;
  opacity: 0.7;
}

::v-deep .remark-input .el-textarea__inner {
  background-color: #f4f6fa;
}

::v-deep .remark-input .el-textarea__inner:focus {
  background-color: #edeffb;
}

/* 滚动容器 */
.scroll-wrapper {
  display: flex;
  max-height: 55vh;
  position: relative;
}

.table-container {
  flex: 1;
  overflow-y: scroll;
  scrollbar-width: none; /* Firefox */
  padding-right: 15px; /* 为滚动条留出空间 */
  width: calc(100% - 16px); /* 减去滚动条宽度 */
}

.table-container::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

/* 自定义滚动条 */
.custom-scrollbar {
  width: 8px;
  background: #f1f1f1;
  border-radius: 4px;
  position: relative;
  margin-left: 8px;
  height: 100%;
  top: 55px;
}

.custom-scrollbar-track {
  position: relative;
  height: 380px;
  cursor: pointer;
}

.custom-scrollbar-thumb {
  position: absolute;
  width: 100%;
  background: #9dade7;
  border-radius: 4px;
  cursor: grab;
  transition: background 0.2s;
}

.custom-scrollbar-thumb:hover {
  background: #6b84d9;
}

.custom-scrollbar-thumb:active {
  cursor: grabbing;
}

.save-Tts {
  background: #796dea;
  border: None;
}

.save-Tts:hover {
  background: #8b80f0;
}

.custom-audio-container audio {
  display: none;
}

/* 新增按钮组样式 */
.action-buttons {
  bottom: 20px;
  padding-top: 10px;
}

</style>