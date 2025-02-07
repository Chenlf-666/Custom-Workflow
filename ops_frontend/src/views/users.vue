<template>
  <div>
    <div class="container">
      <div class="handle-box">
        <el-input
            v-model="queryStr"
            clearable
            placeholder="登录名/email"
            class="handle-input mr10"
            @keyup.enter.native="handleSearch"
            @blur="onBlur"
            @clear="onClear"></el-input>
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      </div>
      <!--      <el-table :data="tableData" max-height="calc(100vh - 260px)" border stripe table-layout="auto">-->
      <el-table :data="tableData"
                border
                stripe
                table-layout="auto"
                :default-sort="{ prop: 'fullname', order: 'ascending' }"
                ref="multipleTable"
                header-cell-class-name="table-header">
        <el-table-column prop="fullname" label="姓名" sortable></el-table-column>
        <el-table-column prop="username" label="登录名" sortable></el-table-column>
        <el-table-column prop="role" label="角色" sortable></el-table-column>
        <el-table-column prop="email" label="邮箱"></el-table-column>
        <el-table-column prop="mobile" label="电话"></el-table-column>
        <el-table-column prop="pwd_expire_date" :formatter="dateFormat" label="密码过期时间" sortable></el-table-column>
        <el-table-column label="操作" width="220px" align="center">
          <template #default="scope">
            <el-button text type="primary" size="small" :icon="RefreshLeft" @click="resetPassword(scope.row)"
                       v-permission="'super'" >重置密码</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <Pagination
            :current-page="pageIndex"
            :page-size="pageSize"
            :total="pageTotal"
            @onPageChange="handlePageChange"
        />
      </div>
    </div>
    <el-dialog
        v-model="dialogVisible"
        title='重置密码'
        :show-close=false
        :close-on-click-modal=false
        width="30%">
      <el-form ref="ruleFormRef" :rules="rules" :model="ruleForm" label-width="120px">
        <el-form-item label="用户名" prop="username">
          <el-input disabled v-model="ruleForm.fullname"/>
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="ruleForm.new_password" type="password" show-password/>
        </el-form-item>
      </el-form>
      <template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancel(ruleFormRef)">取 消</el-button>
					<el-button type="primary" @click="onSubmit(ruleFormRef)">确 定</el-button>
				</span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="basetable">
import {ref, reactive} from 'vue';
import {Edit, Eleme, RefreshLeft, Search, Loading} from '@element-plus/icons-vue';
import {getAllUsers, getUserDetail, resetUserPassword} from '../api/user';
import {ElMessageBox, ElMessage, FormInstance, FormRules} from "element-plus";
import Pagination from '@/components/Pagination.vue';
import {dateFormat} from "@/utils/dateFormat";


interface TableItem {
}

const ruleForm = reactive({
  username: '',
  fullname: '',
  new_password: ''
})

const ruleFormRef = ref(null)

const rules = reactive<FormRules>({
  new_password: [
    {required: true, message: '新密码不能为空', trigger: 'blur'},
    {min: 8, message: '新密码最少8位', trigger: 'blur'},
    {max: 32, message: '新密码最多32位', trigger: 'blur'},
  ]
})

const pageIndex = ref(1);
const pageSize = ref(20);
const queryStr = ref("");
const loading = ref(false)

const tableData = ref<TableItem[]>([]);
const pageTotal = ref(0);
// 获取表格数据
const getUserList = (pageSize: number, pageIndex: number, search?: string) => {
  tableData.value = [];
  getAllUsers(pageSize, pageIndex, search)
      .then(res => {
        tableData.value = res.data.results;
        pageTotal.value = res.data.count;
      })
      .catch(r => {
        console.log("error= " + r.toString())
      });
};

getUserList(pageSize.value, pageIndex.value);

// 查询操作
let finalSearch = ""
const handleSearch = () => {
  finalSearch = queryStr.value
  if (queryStr.value != "" && pageIndex.value == 1) {
    getUserList(pageSize.value, pageIndex.value, queryStr.value);
  }
  pageIndex.value = 1;
};

const onClear = () => {
  finalSearch = "";
  pageIndex.value = 1;
  getUserList(pageSize.value, pageIndex.value);
}
const onBlur = () => {
  if (queryStr.value == "") {
    finalSearch = "";
    pageIndex.value = 1;
    getUserList(pageSize.value, pageIndex.value);
  }
}

// 分页导航
const handlePageChange = (page: number, size: number) => {
  // console.log("call handlePageChange")
  pageIndex.value = page;
  pageSize.value = size;
  if (queryStr.value != "") {
    queryStr.value = finalSearch;
    getUserList(pageSize.value, pageIndex.value, queryStr.value);
  } else {
    getUserList(pageSize.value, pageIndex.value);
  }
}


const dialogVisible = ref(false);

const resetPassword = (row: any) => {
  getUserDetail(row.id).then(res => {
    ruleForm.username = res.data.username;
    ruleForm.fullname = res.data.fullname;
  })
  dialogVisible.value = true;
};

const onCancel = (formEl: FormInstance | null) => {
  if (!formEl) return;
  dialogVisible.value = false;
  formEl.resetFields();
};

const onSubmit = async (formEl: FormInstance | null) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      dialogVisible.value = false;
      ElMessageBox.confirm(
          `确定要重置 ${ruleForm.fullname}的密码吗？`,
          '警告',
          {type: 'warning'}
      ).then(() => {
        resetUserPassword(ruleForm.username, ruleForm.new_password).then(res => {
          if (res.status == 200){
            ElMessage({
              message: "成功重置此用户密码",
              type: "success"
            })
          }
          formEl.resetFields();
        })
      })
    }
  })
};
</script>


<style scoped>
.handle-box {
  margin-bottom: 20px;
}

.handle-input {
  width: 300px;
}

.mr10 {
  margin-right: 10px;
}

</style>
