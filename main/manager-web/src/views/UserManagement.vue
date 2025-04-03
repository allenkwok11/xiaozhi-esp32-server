<template>
  <div class="welcome">
    <HeaderBar />

    <div class="operation-bar">
      <h2 class="page-title">用户管理</h2>
      <div class="right-operations">
        <el-input placeholder="请输入手机号码查询" v-model="searchPhone" class="search-input" @keyup.enter.native="handleSearch"/>
        <el-button class="btn-search" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <div class="main-wrapper">
      <div class="content-panel">
        <div class="content-area">
          <el-card class="user-card" shadow="never">
            <el-table ref="userTable" :data="userList" class="transparent-table" :header-cell-class-name="headerCellClassName">
              <el-table-column label="选择" type="selection" align="center" width="120"></el-table-column>
              <el-table-column label="用户Id" prop="userid" align="center"></el-table-column>
              <el-table-column label="手机号码" prop="mobile" align="center"></el-table-column>
              <el-table-column label="设备数量" prop="deviceCount" align="center"></el-table-column>
              <el-table-column label="状态" prop="status" align="center"></el-table-column>
              <el-table-column label="操作" align="center">
                <template slot-scope="scope">
                  <el-button size="mini" type="text" @click="resetPassword(scope.row)" style="color: #989fdd">重置密码</el-button>
                  <el-button size="mini" type="text"
                    v-if="scope.row.status === '正常'"
                    @click="disableUser(scope.row)">禁用账户</el-button>
                  <el-button size="mini" type="text"
                    v-if="scope.row.status === '禁用'"
                    @click="restoreUser(scope.row)">恢复账号</el-button>
                  <el-button size="mini" type="text" @click="deleteUser(scope.row)" style="color: #989fdd">删除用户</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="table_bottom">
              <div class="ctrl_btn">
                <el-button size="mini" type="primary" class="select-all-btn" @click="handleSelectAll">全选</el-button>
                <el-button size="mini" type="success" icon="el-icon-circle-check" @click="batchEnable">启用</el-button>
                <el-button size="mini" type="warning" @click="batchDisable"><i class="el-icon-remove-outline rotated-icon"></i>禁用</el-button>
                <el-button size="mini" type="danger" icon="el-icon-delete" @click="batchDelete">删除</el-button>
              </div>
              <div class="custom-pagination">
                <button class="pagination-btn" :disabled="currentPage === 1" @click="goFirst">首页</button>
                <button class="pagination-btn" :disabled="currentPage === 1" @click="goPrev">上一页</button>

                <button v-for="page in visiblePages" :key="page" class="pagination-btn" :class="{ active: page === currentPage }" @click="goToPage(page)">
                  {{ page }}
                </button>

                <button class="pagination-btn" :disabled="currentPage === pageCount" @click="goNext">下一页</button>
                <span class="total-text">共{{ total }}条记录</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <div class="copyright">
      ©2025 xiaozhi-esp32-server
    </div>
    <view-password-dialog :visible.sync="showViewPassword" :password="currentPassword"/>
  </div>
</template>

<script>
import HeaderBar from "@/components/HeaderBar.vue";
import adminApi from '@/apis/module/admin';
import ViewPasswordDialog from '@/components/ViewPasswordDialog.vue'

export default {
  components: { HeaderBar, ViewPasswordDialog },
  data() {
    return {
      showViewPassword: false,
      currentPassword: '',
      searchPhone: '',
      userList: [],
      currentPage: 1,
      pageSize: 5,
      total: 0
    };
  },
  created() {
    this.fetchUsers();
  },
  computed: {
    pageCount() {
      return Math.ceil(this.total / this.pageSize);
    },
    visiblePages() {
      const pages = [];
      const maxVisible = 3;
      let start = Math.max(1, this.currentPage - 1);
      let end = Math.min(this.pageCount, start + maxVisible - 1);

      if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1);
      }

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  methods: {
    fetchUsers() {
        adminApi.getUserList({
            page: this.currentPage,
            limit: this.pageSize,
            mobile: this.searchPhone
        }, ({ data }) => {
            if (data.code === 0) {
                this.userList = data.data.list.map(user => ({
                    ...user,
                    status: user.status === '1' ? '正常' : '禁用'
                }));
                this.total = data.data.total;
            }
        });
    },
    handleSearch() {
        this.currentPage = 1;
        this.fetchUsers();
    },
    handleSelectAll() {
      this.$refs.userTable.toggleAllSelection();
    },
    batchDelete() {
      const selectedUsers = this.$refs.userTable.selection;
      if (selectedUsers.length === 0) {
        this.$message.warning('请先选择需要删除的用户');
        return;
      }

      this.$confirm(`确定要删除选中的${selectedUsers.length}个用户吗？`, '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const loading = this.$loading({
          lock: true,
          text: '正在删除中...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });

        try {
          const results = await Promise.all(
            selectedUsers.map(user => {
              return new Promise((resolve) => {
                adminApi.deleteUser(user.userid, ({data}) => {
                  if (data.code === 0) {
                    resolve({success: true, userid: user.userid});
                  } else {
                    resolve({success: false, userid: user.userid, msg: data.msg});
                  }
                });
              });
            })
          );

          const successCount = results.filter(r => r.success).length;
          const failCount = results.length - successCount;

          if (failCount === 0) {
            this.$message.success(`成功删除${successCount}个用户`);
          } else if (successCount === 0) {
            this.$message.error(`删除失败，请重试`);
          } else {
            this.$message.warning(`成功删除${successCount}个用户，${failCount}个删除失败`);
          }

          this.fetchUsers();
        } catch (error) {
          this.$message.error('删除过程中发生错误');
        } finally {
          loading.close();
        }
      }).catch(() => {
        this.$message.info('已取消删除');
      });
    },
    batchEnable() {
      const selectedUsers = this.$refs.userTable.selection;
      if (selectedUsers.length === 0) {
        this.$message.warning('请先选择需要启用的用户');
        return;
      }
      selectedUsers.forEach(user => {
        user.status = '正常';
      });
      this.$message.success('启用操作成功');
    },
    batchDisable() {
      this.userList.forEach(user => {
      user.status = '禁用';
      });
      this.$message.success('状态已更新为禁用');
    },
    resetPassword(row) {
      this.$confirm('重置后将会生成新密码，是否继续？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }).then(() => {
        adminApi.resetUserPassword(row.userid, ({ data }) => {
          if (data.code === 0) {
            this.currentPassword = data.data
            this.showViewPassword = true
            this.$message.success('密码已重置，请通知用户使用新密码登录')
          }
        })
      })
    },
    disableUser(row) {
      row.status = '禁用';
      console.log('禁用用户：', row);
    },
    restoreUser(row) {
      row.status = '正常';
      console.log('恢复用户：', row);
    },
    deleteUser(row) {
        this.$confirm('确定要删除该用户吗？', '警告', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }).then(() => {
            adminApi.deleteUser(row.userid, ({data}) => {
                if (data.code === 0) {
                    this.$message.success('删除成功')
                    this.fetchUsers()
                } else {
                    this.$message.error(data.msg || '删除失败')
                }
            })
        }).catch(() => {})
    },
    headerCellClassName({columnIndex}) {
      if (columnIndex === 0) {
        return 'custom-selection-header'
      }
      return ''
    },
    goFirst() {
      this.currentPage = 1;
      this.fetchUsers();
    },
    goPrev() {
      if (this.currentPage > 1) {
        this.currentPage--;
         this.fetchUsers();
      }
    },
    goNext() {
      if (this.currentPage < this.pageCount) {
        this.currentPage++;
         this.fetchUsers();
      }
    },
    goToPage(page) {
      this.currentPage = page;
      this.fetchUsers();
    },
  }
};
</script>

<style lang="scss" scoped>
.welcome {
  min-width: 900px;
  min-height: 506px;
  height: 100vh;
  display: flex;
  position: relative;
  flex-direction: column;
  background-size: cover;
  background: linear-gradient(to bottom right, #dce8ff, #e4eeff, #e6cbfd) center;
  -webkit-background-size: cover;
  -o-background-size: cover;
}

.main-wrapper {
  margin: 5px 22px;
  border-radius: 15px;
  min-height: 600px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  background: rgba(237,242,255,0.5);
}

.operation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #ebeef5;
}

.page-title {
  font-size: 24px;
  margin: 0;
}

.right-operations {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.search-input {
  width: 240px;
}

.btn-search {
  background: linear-gradient(135deg, #6B8CFF, #A966FF);
  border: none;
  color: white;
}

.content-panel {
  flex: 1;
  display: flex;
  overflow: hidden;
  height: 100%;
  border-radius: 15px;
  background: transparent;
}

.content-area {
  flex: 1;
  height: 100%;
  min-width: 600px;
  overflow-x: auto;
  background-color: white;
}

.user-card {
  background: white;
  border: none;
  box-shadow: none;
}

.table_bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.ctrl_btn {
  display: flex;
  gap: 8px;
  padding-left: 26px;
  .el-button {
    min-width: 72px;
    height: 32px;
    padding: 7px 12px 7px 10px;
    font-size: 12px;
    border-radius: 4px;
    line-height: 1;
    font-weight: 500;
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
  }

  .el-button--primary {
    background: #5f70f3;
    color: white;
  }

  .el-button--success {
    background: #5bc98c;
    color: white;
  }

  .el-button--warning {
    background: #f6d075;
    color: black;
  }

  .el-button--danger {
    background: #fd5b63;
    color: white;
  }
}

.rotated-icon {
  display: inline-block;
  transform: rotate(45deg);
  margin-right: 4px;
  color: black;
}

.copyright {
  text-align: center;
  color: #979db1;
  font-size: 12px;
  font-weight: 400;
  margin-top: auto;
  padding: 30px 0 20px;
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
}

.custom-pagination {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 15px;

  .pagination-btn:first-child,
  .pagination-btn:nth-child(2),
  .pagination-btn:nth-last-child(2) {
    min-width: 60px;
    height: 32px;
    padding: 0 12px;
    border-radius: 4px;
    border: 1px solid #e4e7ed;
    background: #DEE7FF;
    color: #606266;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: #d7dce6;
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }

  .pagination-btn:not(:first-child):not(:nth-child(2)):not(:nth-last-child(2)) {
    min-width: 28px;
    height: 32px;
    padding: 0;
    border-radius: 4px;
    border: 1px solid transparent;
    background: transparent;
    color: #606266;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(245, 247, 250, 0.3);
    }
  }

  .pagination-btn.active {
    background: #5f70f3 !important;
    color: #ffffff !important;
    border-color: #5f70f3 !important;

    &:hover {
      background: #6d7cf5 !important;
    }
  }

  .total-text {
    color: #909399;
    font-size: 14px;
    margin-left: 10px;
  }
}

:deep(.transparent-table) {
  background: white;
  .el-table__header th {
    background: white !important;
    color: black;
  }

  &::before {
    display: none;
  }

  .el-table__body tr {
    background-color: white;
    td {
      border-top: 1px solid rgba(0, 0, 0, 0.04);
      border-bottom: 1px solid rgba(0, 0, 0, 0.04);
    }
  }
}

:deep(.custom-selection-header) {
  .el-checkbox {
    display: none !important;
  }

  &::after {
    content: '选择';
    display: inline-block;
    color: black;
    font-weight: bold;
    padding-bottom: 18px;
  }
}

:deep(.el-checkbox__inner) {
  background-color: #eeeeee !important;
  border-color: #cccccc !important;
}

:deep(.el-checkbox__inner:hover) {
  border-color: #cccccc !important;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #5f70f3 !important;
  border-color: #5f70f3 !important;
}

@media (min-width: 1144px) {
  .table_bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 40px;
  }
  :deep(.transparent-table) {
    .el-table__body tr {
      td {
        padding-top: 16px;
        padding-bottom: 16px;
      }
      & + tr {
        margin-top: 10px;
      }
    }
  }
}

</style>