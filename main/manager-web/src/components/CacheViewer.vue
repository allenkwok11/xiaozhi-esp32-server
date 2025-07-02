<template>
  <el-dialog
    title="CDN Resource Cache Status"
    :visible.sync="visible"
    width="70%"
    :before-close="handleClose"
  >
    <div v-if="isLoading" class="loading-container">
      <p>Loading Cache Information...</p>
    </div>
    
    <div v-else>
      <div v-if="!cacheAvailable" class="no-cache-message">
        <i class="el-icon-warning-outline"></i>
        <p>Your browser does not support Cache API or Service Worker is not installed</p>
        <el-button type="primary" @click="refreshPage">Refresh Page</el-button>
      </div>
      
      <div v-else>
        <el-alert
          v-if="cacheData.totalCached === 0"
          title="No cached CDN resources found"
          type="warning"
          :closable="false"
          show-icon
        >
          <p>Service Worker initialization not completed or the cache not established. pls refresh the page or wait and try again.</p>
        </el-alert>
        
        <div v-else>
          <el-alert
            title="CDN resource cache status"
            type="success"
            :closable="false"
            show-icon
          >
            Total {{ cacheData.totalCached }} cached resources found
          </el-alert>
          
          <h3>JavaScript Resources ({{ cacheData.js.length }})</h3>
          <el-table :data="cacheData.js" stripe style="width: 100%">
            <el-table-column prop="url" label="URL" width="auto" show-overflow-tooltip />
            <el-table-column prop="cached" label="状态" width="100">
              <template slot-scope="scope">
                <el-tag type="success" v-if="scope.row.cached">Cached</el-tag>
                <el-tag type="danger" v-else>Not cached</el-tag>
              </template>
            </el-table-column>
          </el-table>
          
          <h3>CSS Resources ({{ cacheData.css.length }})</h3>
          <el-table :data="cacheData.css" stripe style="width: 100%">
            <el-table-column prop="url" label="URL" width="auto" show-overflow-tooltip />
            <el-table-column prop="cached" label="状态" width="100">
              <template slot-scope="scope">
                <el-tag type="success" v-if="scope.row.cached">Cached</el-tag>
                <el-tag type="danger" v-else>Not Cached</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
    
    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose">Close</el-button>
      <el-button type="primary" @click="refreshCache">Refresh Cache Status</el-button>
      <el-button type="danger" @click="clearCache">Clear Cache</el-button>
    </span>
  </el-dialog>
</template>

<script>
import {
  getCacheNames,
  checkCdnCacheStatus,
  clearAllCaches,
  logCacheStatus
} from '../utils/cacheViewer';

export default {
  name: 'CacheViewer',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isLoading: true,
      cacheAvailable: false,
      cacheData: {
        css: [],
        js: [],
        totalCached: 0,
        totalNotCached: 0
      }
    };
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.loadCacheData();
      }
    }
  },
  methods: {
    async loadCacheData() {
      this.isLoading = true;
      
      try {
        // 先检查是否支持缓存API
        if (!('caches' in window)) {
          this.cacheAvailable = false;
          this.isLoading = false;
          return;
        }
        
        // 检查是否有Service Worker缓存
        const cacheNames = await getCacheNames();
        this.cacheAvailable = cacheNames.length > 0;
        
        if (this.cacheAvailable) {
          // 获取CDN缓存状态
          this.cacheData = await checkCdnCacheStatus();
          
          // 在控制台输出完整缓存状态
          await logCacheStatus();
        }
      } catch (error) {
        console.error('load cache data failed:', error);
        this.$message.error('load cache data failed');
      } finally {
        this.isLoading = false;
      }
    },
    
    async refreshCache() {
      this.loadCacheData();
      this.$message.success('Refresh cache status');
    },
    
    async clearCache() {
      this.$confirm('confirm to clear all caches?', 'Warning', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          const success = await clearAllCaches();
          if (success) {
            this.$message.success('Cache cleared');
            await this.loadCacheData();
          } else {
            this.$message.error('Clear cache failed');
          }
        } catch (error) {
          console.error('clear cache failed:', error);
          this.$message.error('clear cache failed');
        }
      }).catch(() => {
        this.$message.info('clearing cache cancelled');
      });
    },
    
    refreshPage() {
      window.location.reload();
    },
    
    handleClose() {
      this.$emit('update:visible', false);
    }
  }
};
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.loading-spinner {
  margin-bottom: 10px;
}

.no-cache-message {
  text-align: center;
  padding: 20px;
}

.no-cache-message i {
  font-size: 48px;
  color: #E6A23C;
  margin-bottom: 10px;
}

h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-weight: 500;
}
</style> 