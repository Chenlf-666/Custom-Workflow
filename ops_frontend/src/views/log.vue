<template>
    <div class="container">
      <div class="handle-box">
        <el-select v-model="actorId" clearable filterable :reserve-keyword="true" class="mr10" @change="actorIdChange" @clear="onClearActor" style="width: 240px">
            <el-option v-for="item in actorInfo" :label="item.fullname" :key="item.id" :value="item.id"/>
        </el-select>
        <el-select v-model="actionId" clearable filterable :reserve-keyword="true" class="mr10" @change="actionIdChange" @clear="onClearAction" style="width: 240px">
            <el-option v-for="item in actionInfo" :label="item.name" :key="item.id" :value="item.id"/>
        </el-select>
				<el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
			</div>
      <el-table :data="tableData"
                border
                stripe
                :default-sort="{ prop: 'fullname', order: 'ascending' }"
                ref="multipleTable"
                header-cell-class-name="table-header">
        <el-table-column prop="operator" label="姓名" sortable></el-table-column>
        <el-table-column prop="action" label="操作类型">
          <template #default="scope">
						<span v-if="scope.row.action == 0">创建</span>
            <span v-else-if="scope.row.action == 1">更新</span>
            <span v-else-if="scope.row.action == 2">删除</span>
						<span v-else>登录</span>
					</template>
        </el-table-column>
        <el-table-column prop="model" label="模块"></el-table-column>
        <el-table-column prop="timestamp" label="时间" :formatter="dateFormat" sortable></el-table-column>
        <el-table-column label="详情" width="220px" align="center">
          <template #default="scope">
            <el-button text type="primary" :icon="View" @click="handleView(scope.row)"
                       :disabled="logInfoTable[scope.row] || scope.row.action == '3' ? true : false"
                       v-permission="'admin'" >详细信息</el-button>
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

      <el-dialog
        v-model="logVisible"
        :close-on-click-modal=false
        width="75%"
        align-center
        title="日志详情"
        :destroy-on-close="true"
        @closed="handleClose"
      >
        <div>
          <el-table :data="logInfoTable"
                border
                stripe
                ref="multipleTable"
                header-cell-class-name="table-header">
            <el-table-column prop="actionName" label="名称"></el-table-column>
            <el-table-column prop="before" label="修改前"></el-table-column>
            <el-table-column prop="after" label="修改后"></el-table-column>
          </el-table>
        </div>

      </el-dialog>
    </div>
</template>

<script lang="ts" setup>

import { getAuditLog } from "@/api/log"
import { getAllUsers } from "@/api/user"
import { ref, reactive } from 'vue';
import Pagination from '@/components/Pagination.vue';
import { dateFormat } from '../utils/dateFormat';
import { View, Search } from '@element-plus/icons-vue';

const pageIndex = ref(1);
const pageSize = ref(20);
const pageTotal = ref(0);
const actionId = ref();
const actorId = ref();
const logVisible = ref(false);
const actorInfo = <any>ref([]);
const logInfoTable = <any>ref([]);
const actionInfo = [{"name":"创建", "id": 0}, {"name":"更新","id":1},{"name":"删除", "id": 2},{"name":"登录", "id": 3}]
let finalSearchActionId = '';
let finalSearchActorId = '';


interface TableItem {}
const getUsers = () => {
  getAllUsers().then((res)=>{
    actorInfo.value = res.data.results;
  })
} 

getUsers()

const actorIdChange = (v) => {
  actorId.value = v;
}

const onClearActor = () => {
  finalSearchActorId = '';
  pageIndex.value = 1;
  getAlllogs(pageIndex.value, pageSize.value, actionId.value, actorId.value);
}

const onClearAction = () => {
  finalSearchActionId = '';
  pageIndex.value = 1;
  getAlllogs(pageIndex.value, pageSize.value, actionId.value, actorId.value);
}

const actionIdChange = (v) => {
  actionId.value = v;
}

const handleSearch = () => {
  finalSearchActionId = actionId.value;
  finalSearchActorId = actorId.value;
  if (pageIndex.value == 1 && (finalSearchActionId != '' || finalSearchActorId != '')){
    getAlllogs(pageIndex.value, pageSize.value, actionId.value, actorId.value);
  }
  pageIndex.value = 1;
}


const tableData = ref<TableItem[]>([]);

const getAlllogs = (pageIndex: number, pageSize: number, actionId?:any, actorId?:any) => {
  tableData.value = [];
  getAuditLog(pageIndex, pageSize, actionId, actorId).then(res => {
    tableData.value = res.data.results;
    pageTotal.value = res.data.count;
  })
}

const handleView = (v: any) => {
  logInfoTable.value = [];
  if (v.changes){
    let temp = Object.keys(v.changes);
    temp && temp.length && temp.forEach((item, index)=>{
      logInfoTable.value.push({"actionName":item, "before":v.changes[item][0], "after":v.changes[item][1]});
    })
  }
  logVisible.value = true;
}

const handleClose = () => {
  logVisible.value = false;
}

getAlllogs(pageIndex.value, pageSize.value, actionId.value, actorId.value)

// 分页导航
const handlePageChange = (page: number, size: number) => {
  pageIndex.value = page;
  pageSize.value = size;
  actionId.value = finalSearchActionId;
  actorId.value = finalSearchActorId;
  getAlllogs(pageIndex.value, pageSize.value, actionId.value, actorId.value);
}

</script>

<style scoped>
.mr10 {
  margin-right: 10px;
}

.handle-box {
  margin-bottom: 20px;
  display: flex;
}

</style>