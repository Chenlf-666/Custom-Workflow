<template>
	<div>
		<div class="container">
			<div class="handle-box">
				<el-input 
				v-model="queryStr" 
				clearable 
				placeholder="工作流名称" 
				class="handle-input mr10"
				@keyup.enter.native="handleSearch"
				@clear="onClear"></el-input>
				<el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
				<el-button type="primary" :icon="Plus" @click="handleAdd">创建工作流</el-button>
			</div>
			<el-table :data="tableData" stripe border header-cell-class-name="table-header" ref="multipleTable">
			<el-table-column prop="name" label="工作流名称" width="180px" sortable></el-table-column>
			<el-table-column prop="is_active" label="状态" width="180px">
        <template #default="scope">
          <div v-if="scope.row.is_active == true" class="flex items-center" style="color:green">
            <span class="ml-2">已激活</span>
          </div>
          <div v-else class="flex items-center" style="color:orange">
            <span class="ml-2">未激活</span>
          </div>
        </template>
      </el-table-column>
			<el-table-column prop="description" label="描述"></el-table-column>
			<el-table-column prop="create_time" :formatter="dateFormat" label="创建时间" width="180px" sortable></el-table-column>
			<el-table-column prop="update_time" :formatter="dateFormat" label="更新时间" width="180px" sortable></el-table-column>
			<el-table-column label="操作" width="220px" align="center">
				<template #default="scope">
				<el-button text type="primary" :icon="Edit" @click="handleEdit(scope.row)">
					编辑
				</el-button>
				<el-popconfirm width="200px" title="确定删除此工作流吗?" @confirm="confirmDelete(scope.$index, scope.row)" >
					<template #reference>
					<el-button text :icon="Delete" type="danger">删除</el-button>
					</template>
				</el-popconfirm>
				</template>
			</el-table-column>
			</el-table>
			<div class="pagination">
				<Pagination
        	:current-page="currentPage"
          :page-size="pageSize"
					:total="pageTotal"
					@onPageChange="handlePageChange">
				</Pagination>
			</div>
		</div>

	</div>
</template>

<script setup lang="ts" name="basetable">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { Delete, Edit, Search, Plus } from '@element-plus/icons-vue';
import { getCusWorkflowList, deleteCusWorkflow } from '../api/cusWorkflow';
import { dateFormat } from '../utils/dateFormat'
import Pagination from '@/components/Pagination.vue';
import {useRouter} from 'vue-router';

interface TableItem { }

const router = useRouter();
const currentPage = ref(1);
const pageSize = ref(20);
const queryStr = ref("");
const tableData = ref<TableItem[]>([]);
const pageTotal = ref(0);

// 获取表格数据
const getAllWorkflows = (pageSize: number, currentPage: number, name?: string) => {
	getCusWorkflowList(pageSize, currentPage, name).then(res => {
		tableData.value = res.data.results;
		pageTotal.value = res.data.count;
	});
};

getAllWorkflows(pageSize.value, currentPage.value);

// 查询操作
let finalSearch = ""
const handleSearch = () => {
	finalSearch = queryStr.value;
	currentPage.value = 1;
	getAllWorkflows(pageSize.value, currentPage.value, queryStr.value);
};

const onClear = () =>{
	getAllWorkflows(pageSize.value, currentPage.value);
}

// 分页导航
const handlePageChange = (page: number, size: number) => {
  currentPage.value = page;
  pageSize.value = size;
	if (queryStr.value != "") {
    queryStr.value = finalSearch;
		getAllWorkflows(pageSize.value, currentPage.value, queryStr.value);
	} else {
		getAllWorkflows(pageSize.value, currentPage.value);
	}
}

const handleAdd = () => {
	router.push({ path: '/customWorkflows/detail' })
}

let idx: number = -1;
const handleEdit = (row: any) => {
	idx = row.id
	router.push({ path: '/customWorkflows/detail', query: { workflowId: idx } })
}

const confirmDelete = (index: number, row: any) => {
	deleteCusWorkflow(row.id).then((res)=>{
		if (res && res.status == 204){
			tableData.value.splice(index, 1)
			pageTotal.value -= 1
			ElMessage({
        message: "成功删除此工作流",
        type: "success"
      })
		}
	}).catch(()=>{
		ElMessage({
      message: "删除此工作流失败",
      type: "error"
    })
	})
} 

</script>

<style scoped>
.handle-box {
	margin-bottom: 20px;
}

.handle-select {
	width: 120px;
}

.handle-input {
	width: 300px;
}

.table {
	width: 100%;
	font-size: 14px;
}

.red {
	color: #ff0000;
}

.mr10 {
	margin-right: 10px;
}

.table-td-thumb {
	display: block;
	margin: auto;
	width: 40px;
	height: 40px;
}
</style>
