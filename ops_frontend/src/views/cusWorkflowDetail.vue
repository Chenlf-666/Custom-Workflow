<template>
	<div>
		<el-tabs v-model="tabIndex" @tab-change="tabChange">
			<el-tab-pane label="基础信息" name="1">
        <el-card v-loading="loading">
          <el-form ref="infoRuleFormRef" :rules="infoRules" :model="infoForm" style="text-align: center" class="flex">
						<el-form-item label="工作流名称" prop="name" style="margin-left: 20px">
              <el-input v-model="infoForm.name" style="width:200px"/>
            </el-form-item>
						<el-form-item label="描述信息" prop="description" style="margin-left: 20px">
              <el-input v-model="infoForm.description" style="width:200px"/>
            </el-form-item>
						<el-form-item label="是否激活" style="margin-left: 20px">
							<el-switch v-model="infoForm.is_active" />
						</el-form-item>
            <el-form-item style="margin-left: 20px">
              <el-button type="primary" @click="handleInfoForm(infoRuleFormRef)">
								设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
			</el-tab-pane>
			<el-tab-pane label="自定义字段" name="2" :disabled="workflowId == 0">
				<div class="container">
					<div class="handle-box">
						<el-input 
							v-model="fieldQueryStr" 
							clearable 
							placeholder="字段名称" 
							class="handle-input mr10"
							@keyup.enter.native="handleSearchField"
							@clear="onClearField">
						</el-input>
						<el-button type="primary" :icon="Search" @click="handleSearchField">搜索</el-button>
						<el-button type="primary" :icon="Plus" @click="handleAddField" v-permission="'super'">新增字段</el-button>
					</div>
					<el-scrollbar>
						<el-table :data="fieldTableData" stripe border header-cell-class-name="table-header">
							<el-table-column prop="name" label="字段名称"></el-table-column>
							<el-table-column prop="field_key" label="字段标识"></el-table-column>
							<el-table-column prop="field_type" label="字段类型">
								<template #default="scope">
									<div v-if="scope.row.field_type === 1">字符串</div>
									<div v-else-if="scope.row.field_type === 2">整型</div>
									<div v-else-if="scope.row.field_type === 3">浮点型</div>
									<div v-else-if="scope.row.field_type === 4">布尔型</div>
									<div v-else-if="scope.row.field_type === 5">日期</div>
									<div v-else-if="scope.row.field_type === 6">日期时间</div>
									<div v-else-if="scope.row.field_type === 7">范围日期</div>
									<div v-else-if="scope.row.field_type === 8">文本域</div>
									<div v-else-if="scope.row.field_type === 9">单选框</div>
									<div v-else-if="scope.row.field_type === 10">下拉列表</div>
									<div v-else-if="scope.row.field_type === 11">外键</div>
									<div v-else-if="scope.row.field_type === 12">多选框</div>
									<div v-else-if="scope.row.field_type === 13">多选下拉</div>
									<div v-else-if="scope.row.field_type === 14">多选外键</div>
									<div v-else>N/A</div>
								</template>
							</el-table-column>
							<el-table-column prop="order_id" label="字段顺序" sortable></el-table-column>
							<el-table-column label="操作" width="360" align="center">
								<template #default="scope" v-permission="15">
									<el-button text type="primary" :icon="Edit" @click="handleEditField(scope.row)" v-permission="'super'">
										编辑
									</el-button>
									<el-popconfirm width="200px" title="确定删除该字段吗?" @confirm="confirmDeleteField(scope.$index, scope.row)" >
										<template #reference>
											<el-button text :icon="Delete" type="danger" v-permission="'super'">删除</el-button>
										</template>
									</el-popconfirm>
								</template>
							</el-table-column>
						</el-table>
					</el-scrollbar>
          <div class="pagination">
            <Pagination
              :current-page="fieldCurrentPage"
              :page-size="fieldPageSize"
              :total="totalField"
              @onPageChange="handleFieldSizeChange"
            />
          </div>
				</div>
			</el-tab-pane>
			<el-tab-pane label="状态" name="3" :disabled="workflowId == 0">
				<div class="container">
					<div class="handle-box">
						<el-input 
							v-model="statusQueryStr" 
							clearable 
							placeholder="状态名称" 
							class="handle-input mr10"
							@keyup.enter.native="handleSearchStatus"
							@clear="onClearStatus">
						</el-input>
						<el-button type="primary" :icon="Search" @click="handleSearchStatus">搜索</el-button>
						<el-button type="primary" :icon="Plus" @click="handleAddStatus" v-permission="'super'">新增状态</el-button>
					</div>
					<el-scrollbar>
						<el-table :data="statusTableData" stripe border header-cell-class-name="table-header">
							<el-table-column prop="name" label="状态名称"></el-table-column>
							<el-table-column prop="order_id" label="状态顺序" sortable></el-table-column>
							<el-table-column prop="state_type" label="状态类型">
								<template #default="scope">
									<div v-if="scope.row.state_type === 0">初始状态</div>
									<div v-else-if="scope.row.state_type === 1">普通状态</div>
									<div v-else-if="scope.row.state_type === 2">结束状态</div>
									<div v-else>N/A</div>
								</template>
							</el-table-column>
							<el-table-column prop="participant_type" label="参与者类型">
								<template #default="scope">
									<div v-if="scope.row.participant_type === 0">无</div>
									<div v-else-if="scope.row.participant_type === 1">用户</div>
									<div v-else-if="scope.row.participant_type === 2">权限组</div>
									<div v-else-if="scope.row.participant_type === 3">自定义字段</div>
									<div v-else>N/A</div>
								</template>
							</el-table-column>
							<el-table-column prop="participant" label="参与者">
								<template #default="scope">
									<div v-if="scope.row.participant_names">
										<el-popover effect="light" trigger="hover" placement="top" width="auto">
											<template #default>
												<div v-for="item in scope.row.participant_names">
													{{ item }}
												</div>
											</template>
											<template #reference>
												<el-tag>{{ scope.row.participant_names[0] }}...</el-tag>
											</template>
										</el-popover>
									</div>
								</template>
							</el-table-column>
							<el-table-column label="操作" width="360" align="center">
								<template #default="scope" v-permission="15">
									<el-button text type="primary" :icon="Edit" @click="handleEditStatus(scope.row)" v-permission="'super'">
										编辑
									</el-button>
									<el-popconfirm width="200px" title="确定删除该字段吗?" @confirm="confirmDeleteStatus(scope.$index, scope.row)" >
										<template #reference>
											<el-button text :icon="Delete" type="danger" v-permission="'super'">删除</el-button>
										</template>
									</el-popconfirm>
								</template>
							</el-table-column>
						</el-table>
					</el-scrollbar>
          <div class="pagination">
            <Pagination
              :current-page="statusCurrentPage"
              :page-size="statusPageSize"
              :total="totalStatus"
              @onPageChange="handleStatusSizeChange"
            />
          </div>
				</div>
			</el-tab-pane>
			<el-tab-pane label="流转" name="4" :disabled="workflowId == 0">
				<div class="container">
					<div class="handle-box">
						<el-input 
							v-model="transQueryStr" 
							clearable 
							placeholder="流转名称" 
							class="handle-input mr10"
							@keyup.enter.native="handleSearchTrans"
							@clear="onClearTrans">
						</el-input>
						<el-button type="primary" :icon="Search" @click="handleSearchTrans">搜索</el-button>
						<el-button type="primary" :icon="Plus" @click="handleAddTrans" v-permission="'super'">新增</el-button>
					</div>
					<el-scrollbar>
						<el-table :data="transTableData" stripe border header-cell-class-name="table-header">
							<el-table-column prop="name" label="流转名称"></el-table-column>
							<el-table-column prop="source_state_name" label="源状态"></el-table-column>
							<el-table-column prop="dest_state_name" label="目的状态"></el-table-column>
							<el-table-column label="操作" width="360" align="center">
								<template #default="scope" v-permission="15">
									<el-button text type="primary" :icon="Edit" @click="handleEditTrans(scope.row)" v-permission="'super'">
										编辑
									</el-button>
									<el-popconfirm width="200px" title="确定删除该流转吗?" @confirm="confirmDeleteTrans(scope.$index, scope.row)" >
										<template #reference>
											<el-button text :icon="Delete" type="danger" v-permission="'super'">删除</el-button>
										</template>
									</el-popconfirm>
								</template>
							</el-table-column>
						</el-table>
					</el-scrollbar>
          <div class="pagination">
            <Pagination
              :current-page="transCurrentPage"
              :page-size="transPageSize"
              :total="totalTrans"
              @onPageChange="handleTransSizeChange"
            />
          </div>
				</div>
			</el-tab-pane>

			<el-tab-pane label="流程图" name="5" :disabled="workflowId == 0">
				<graph-test 
					:workflow-id = workflowId
					:tab-index = tabIndex
				/>
			</el-tab-pane>
    </el-tabs>


		<!-- 增加/编辑自定义字段弹出框 -->
		<el-dialog
      v-model="fieldDlgVisible"
      :show-close=false
			:close-on-click-modal=false
      :title="isAddField ? '新增自定义字段' : '编辑自定义字段'"
      width="40%"
			:destroy-on-close="true"
			@closed="onCancelField(ruleFormRef)"
		>
			<el-form ref="ruleFormRef" :rules="fieldRules" :model="fieldForm" label-width="150px">
				<el-form-item label="名称" prop="name">
					<el-input v-model="fieldForm.name" />
				</el-form-item>
				<el-form-item label="字段类型" prop="field_type">
					<el-select v-model="fieldForm.field_type" filterable :reserve-keyword="true" placeholder="请选择字段类型">
						<el-option v-for="item in fieldTypeList" :label="item.name" :key="item.id" :value="item.id"  />
					</el-select>
				</el-form-item>
				<el-form-item label="字段标识" prop="field_key">
					<el-input v-model="fieldForm.field_key" />
				</el-form-item>
				<el-form-item label="顺序" prop="order_id">
					<el-input-number v-model="fieldForm.order_id" />
				</el-form-item>
				<el-form-item prop="default_value">
					<template #label>
						<span style="display:inline-flex; align-items: center;">
							默认值
							<el-tooltip effect="dark" content="一般格式为字符串，多选/下拉框均为列表格式如[1,2]" placement="bottom" >
								<el-icon ><Warning style="width: 20px; height: 20px;"/></el-icon>
							</el-tooltip>
						</span>
					</template>
					<el-input v-model="fieldForm.default_value" placeholder="一般格式为字符串，多选/下拉框均为列表格式如[1,2]"/>
				</el-form-item>
				<el-form-item prop="field_choice" v-if="fieldForm.field_type !== 11 && fieldForm.field_type !== 14" label="字段选项">
					<template #label>
						<span style="display:inline-flex; align-items: center;">
							字段选项
							<el-tooltip effect="dark" content='一般格式为{"key":"0", "value":"测试"}; 多选/下拉框格式为[{"key":1,"value":"a"},{"key":2,"value":"b"}]' placement="bottom" >
								<el-icon ><Warning style="width: 20px; height: 20px;"/></el-icon>
							</el-tooltip>
						</span>
					</template>
					<el-input v-model="fieldForm.field_choice" placeholder='一般格式{"key":"0", "value":"测试"}; 多选/下拉框格式如[{"key":1,"value":"a"},{"key":2,"value":"b"}]'/>
				</el-form-item>
				<el-form-item label="外键类型" prop="foreign_type">
					<el-select v-model="fieldForm.foreign_type" filterable :reserve-keyword="true"  placeholder="请选择绑定的关联字段">
						<el-option v-for="item in contentTypeList" :label="item.model_name" :key="item.id" :value="item.id"  />
					</el-select>
				</el-form-item>
				<el-form-item label="是否必填" prop="required">
					<el-switch v-model="fieldForm.required"></el-switch>
				</el-form-item>
				<el-form-item label="是否显示" prop="displayed">
					<el-switch v-model="fieldForm.displayed"></el-switch>
				</el-form-item>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancelField(ruleFormRef)">取 消</el-button>
					<el-button type="primary" @click="onSubmitField(ruleFormRef)">确 定</el-button>
				</span>
			</template>
		</el-dialog>


		<!-- 增加/编辑工作流状态弹出框 -->
		<el-dialog
      v-model="statusDlgVisible"
      :show-close=false
			:close-on-click-modal=false
      :title="isAddStatus ? '新增状态' : '编辑状态'"
      width="40%"
			:destroy-on-close="true"
			@closed="onCancelStatus(ruleFormRef)"
		>
			<el-form ref="ruleFormRef" :rules="statusRules" :model="statusForm" label-width="150px">
				<el-form-item label="名称" prop="name">
					<el-input v-model="statusForm.name" />
				</el-form-item>
				<el-form-item label="状态顺序" prop="order_id">
					<el-input-number v-model="statusForm.order_id" />
				</el-form-item>
				<el-form-item label="状态类型" prop="state_type">
          <el-select clearable v-model="statusForm.state_type" style="width:500px">
            <el-option label="初始状态" :value="0" :key="0"/>
            <el-option label="普通状态" :value="1" :key="1"/>
						<el-option label="结束状态" :value="2" :key="2"/>
          </el-select>
        </el-form-item>
				<el-form-item label="参与者类型" prop="participant_type">
          <el-select clearable v-model="statusForm.participant_type" style="width:500px" @change="participantTypeChange">
            <el-option label="无" :value="0" :key="0"/>
            <el-option label="用户" :value="1" :key="1"/>
						<el-option label="权限组" :value="2" :key="2"/>
						<el-option label="自定义字段" :value="3" :key="3"/>
          </el-select>
        </el-form-item>
				<el-form-item label="参与者" prop="participant" v-if="statusForm.participant_type !== 0">
					<el-select v-model="statusForm.participant" filterable multiple :reserve-keyword="true" :filter-method="filterMethod" placeholder="请选择用户" v-if="statusForm.participant_type == 1">
						<el-option v-for="item in usersInfo" :label="item.fullname" :key="item.id" :value="item.id"  />
					</el-select>
					<el-select v-model="statusForm.participant" filterable multiple :reserve-keyword="true" placeholder="请选择权限组" v-else-if="statusForm.participant_type == 2">
						<el-option v-for="item in roleGroupList" :label="item.name" :key="item.id" :value="item.id"  />
					</el-select>
					<el-select v-model="statusForm.participant" filterable :reserve-keyword="true" placeholder="请选择自定义字段" v-else-if="statusForm.participant_type == 3">
						<el-option v-for="item in fieldTableData" :label="item.name" :key="item.id" :value="item.id"  />
					</el-select>
				</el-form-item>
				<el-form-item label="允许撤回" prop="enable_retreat">
					<el-switch v-model="statusForm.enable_retreat" />
				</el-form-item>
				<el-form-item label="关联字段" prop="field_info">
					<el-select v-model="statusForm.field_info" filterable multiple :reserve-keyword="true"  placeholder="请选择绑定的关联字段">
						<el-option v-for="item in fieldTableData" :label="item.name" :key="item.id" :value="item.id"  />
					</el-select>
				</el-form-item>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancelStatus(ruleFormRef)">取 消</el-button>
					<el-button type="primary" @click="onSubmitStatus(ruleFormRef)">确 定</el-button>
				</span>
			</template>
		</el-dialog>

		<!-- 增加/编辑流转弹出框 -->
		<el-dialog
      v-model="transDlgVisible"
      :show-close=false
			:close-on-click-modal=false
      :title="isAddTrans ? '新增流转' : '编辑流转'"
      width="40%"
			:destroy-on-close="true"
			@closed="onCancelTrans(ruleFormRef)"
		>
			<el-form ref="ruleFormRef" :rules="transRules" :model="transForm" label-width="150px">
				<el-form-item label="名称" prop="name">
					<el-input v-model="transForm.name" />
				</el-form-item>
				<el-form-item label="源状态" prop="source_state">
					<el-select v-model="transForm.source_state" filterable :reserve-keyword="true"  placeholder="请选择流转的源状态">
						<el-option v-for="item in statusTableData" :label="item.name" :key="item.id" :value="item.id"  />
					</el-select>
				</el-form-item>
				<el-form-item label="目的状态" prop="dest_state">
					<el-select v-model="transForm.dest_state" filterable :reserve-keyword="true"  placeholder="请选择流转的目的状态">
						<el-option v-for="item in statusTableData" :label="item.name" :key="item.id" :value="item.id"  />
					</el-select>
				</el-form-item>
				<el-form-item label="点击弹窗提示" prop="alert_enable">
					<el-switch v-model="transForm.alert_enable" />
				</el-form-item>
				<el-form-item label="弹窗内容" prop="alert_text">
					<el-input v-model="transForm.alert_text" />
				</el-form-item>
				<el-form-item label="处理方式" prop="trans_type">
          <el-select clearable v-model="transForm.trans_type" style="width:500px">
            <el-option label="只需要单个处理" :value="1" :key="1"/>
            <el-option label="需要全部处理" :value="2" :key="2"/>
          </el-select>
        </el-form-item>
				<el-form-item label="触发器" prop="trigger_types">
          <el-select clearable v-model="transForm.trigger_types" multiple :reserve-keyword="true" placeholder="请选择触发器"  style="width:500px">
            <el-option label="发送消息给后续人员" :value="1" :key="1"/>
          </el-select>
        </el-form-item>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancelTrans(ruleFormRef)">取 消</el-button>
					<el-button type="primary" @click="onSubmitTrans(ruleFormRef)">确 定</el-button>
				</span>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="basetable">
import {ref, reactive, onMounted, onBeforeMount, watch} from 'vue';
import {ElMessage, ElMessageBox} from 'element-plus';
import {Delete, Edit, Search, Plus, VideoPlay} from '@element-plus/icons-vue';
import type {FormInstance, FormRules} from 'element-plus';
import {addCusWorkflow, getCusWorkflowList, updateCusWorkflow, cusWorkflowDetail, getContentTypes, 
	addWorkflowField, updateField, fieldDetail, deleteField, getFieldList, getWorkflowStatus, addWorkflowStatus, 
	workflowStatusDetail, updateWorkflowStatus, deleteWorkflowStatus, getTransitions, addTransition, transitionDetail,
  updateTransition, deleteTransition} from '../api/cusWorkflow'
import { getAllUsers, getAllGroups } from '../api/user';
import {useRouter} from 'vue-router';
import { dateFormat } from '../utils/dateFormat';
import { workflowDetail } from '../api/workflow';
import graphTest from '@/components/workflows/customWorkflowGraph.vue'

const router = useRouter();

let idx: number = -1;
const infoRuleFormRef = ref(null);
const ruleFormRef = ref(null)
const workflowId = ref(0);
const loading = ref(false);
const dialogVisible = ref(false);
const isCreate = ref(false);
const tableData = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = ref(20);
const queryStr = ref("");
const total = ref(0);
const tabIndex = ref('1');
const pageIndex = ref(1);

const infoForm = reactive({
	name: '',
	description: '',
	is_active: false
})

const tabChange = (v: string) => {
  queryStr.value = '';
	pageIndex.value = 1;
	if (v == "2"){
		getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value);
	}else if (v == "3"){
		getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value);
	}else if (v == "4"){
		getAllTransList(workflowId.value, transPageSize.value, transCurrentPage.value);
		getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value);
	}
}

onBeforeMount(async ()=>{
	if (Number(router?.currentRoute?.value?.query?.workflowId)){
		workflowId.value = Number(router?.currentRoute?.value?.query?.workflowId)
	}
})

const getCurrentWorkflowInfo = (id) => {
	cusWorkflowDetail(id).then((res) => {
		if (res && res.status == 200) {
			infoForm.name = res.data.name;
			infoForm.description = res.data.description;
			infoForm.is_active = res.data.is_active;
		}
	})
}

watch(workflowId, (value)=>{
	workflowId.value && getCurrentWorkflowInfo(workflowId.value);
	getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value, fieldQueryStr.value);
})

const infoRules = reactive<FormRules>({
	name: [
			{required: true, message: '工作流名称不能为空', trigger: 'blur'},
	],
	description: [
			{required: true, message: '描述信息不能为空', trigger: 'blur'},
	]
})

const handleInfoForm = async (formEl: FormInstance | null) => {
	if (!formEl) return
	await formEl.validate((valid, fields) => {
		if (valid){
			if (workflowId.value){
				updateCusWorkflow(workflowId.value, infoForm).then(res=>{
					if (res && res.status == 200){
						ElMessage({
							message: "成功编辑自定义工作流",
							type: "success"
						})
					}
				})
			}else{
				addCusWorkflow(infoForm).then(res=>{
					if (res && res.status == 201){
						ElMessage({
							message: "成功创建自定义工作流",
							type: "success"
						})
					}
					workflowId.value = res.data.id;
					router.push({ path: '/customWorkflows/detail', query: { workflowId: res.data.id } })
				})
			}
		}else{
			console.log('设置打包参数失败!', fields)
		}
	})
}

// 自定义字段相关操作
const fieldDlgVisible = ref(false);
const fieldTypeList = [{"id": 1, "name": "字符串"}, {"id": 2, "name": "整型"}, {"id": 3, "name": "浮点型"}, {"id": 4, "name": "布尔型"}, {"id": 5, "name": "日期"}, 
	{"id": 6, "name": "日期时间"}, {"id": 7, "name": "范围日期"}, {"id": 8, "name": "文本域"}, {"id": 9, "name": "单选框"}, {"id": 10, "name": "下拉列表"}, 
	{"id": 11, "name": "外键"}, {"id": 12, "name": "多选框"}, {"id": 13, "name": "多选下拉"}, {"id": 14, "name": "多选外键"}];
const contentTypeList = ref<any[]>([]);
const isAddField = ref(false);
const fieldTableData = ref<any[]>([]);
let idxField: number = -1;
const fieldPageSize = ref(20);
const fieldCurrentPage = ref(1);
const totalField = ref(0);
const fieldQueryStr = ref("");

const fieldForm = reactive({
	name: '',
	default_value: '',
	field_choice: '',
	field_type: null as number | undefined | null,
	foreign_type: '',
	order_id: 1,
	field_key: '',
	special_url: '',
	required: false,
	displayed: false
})

const fieldRules = reactive<FormRules>({
	name: [
			{required: true, message: '字段名称不能为空', trigger: 'blur'},
	],
	field_key: [
			{required: true, message: '字段标识不能为空', trigger: 'blur'},
	],
	field_type: [
			{required: true, message: '字段类型不能为空', trigger: 'blur'},
	]	
})

const onCancelField = (formEl: FormInstance | null) =>{
  if (!formEl) return;
	formEl.resetFields();
	fieldDlgVisible.value = false;
	isAddField.value = false;

	fieldForm.default_value = '';
	fieldForm.field_choice = '';
	fieldForm.field_key = '';
	fieldForm.field_type = null;
	fieldForm.foreign_type = '';
	fieldForm.name = '';
	fieldForm.order_id = 1;
	fieldForm.special_url = '';
	fieldForm.required = false;
	fieldForm.displayed = false;
	idxField = -1;
}

const getContentTypeList = () => {
	contentTypeList.value = [];
	getContentTypes().then(res => {
		contentTypeList.value = res.data.results;
	})
}

getContentTypeList()

const getAllFieldLIst = (workflowId: number, pageSize: number, currentPage: number, name?: string) => {
	getFieldList(workflowId, pageSize, currentPage, name).then(res => {
    fieldTableData.value = res.data.results;
    totalField.value = res.data.count;
  });
}

const handleAddField = () => {
	isAddField.value = true;
	fieldDlgVisible.value = true;
}

const handleEditField = (row: any) => {
	idxField = row.id;
	fieldDetail(workflowId.value, row.id).then(res=>{
		fieldForm.default_value = res.data.default_value;
		fieldForm.field_choice = res.data.field_choice;
		fieldForm.field_key = res.data.field_key;
		fieldForm.field_type = res.data.field_type;
		fieldForm.foreign_type = res.data.foreign_type;
		fieldForm.name = res.data.name;
		fieldForm.order_id = res.data.order_id;
		fieldForm.special_url = res.data.special_url;
		fieldForm.required = res.data.required;
		fieldForm.displayed = res.data.displayed;
	}).finally(()=>{
		fieldDlgVisible.value = true;
    isAddField.value = false;
	})
}

let fieldFinalSearch = "";
const handleSearchField = () => {
	fieldCurrentPage.value = 1;
	fieldFinalSearch = fieldQueryStr.value;
	getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value, fieldQueryStr.value);
};

const onClearField = () => {
  fieldFinalSearch = '';
	getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value);
}

const handleFieldSizeChange = (page: number, size: number) => {
  fieldCurrentPage.value = page;
  fieldPageSize.value = size;
	if (fieldQueryStr.value != "") {
    fieldQueryStr.value = fieldFinalSearch;
		getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value, fieldQueryStr.value);
	} else {
		getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value);
	}
}

const confirmDeleteField = (index: number, row: any) => {
	deleteField(workflowId.value, row.id).then((res)=>{
		if (res && res.status == 204){
			fieldTableData.value.splice(index, 1)
			ElMessage({
						message: "成功删除该自定义字段",
						type: "success"
					})
			getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value);
		}
	}).catch(()=>{
		ElMessage({
			message: "删除该自定义字段失败",
			type: "error"
		})
	})
} 

const onSubmitField = async (formEl: FormInstance | null) => {
	if (!formEl) return
	await formEl.validate((valid, fields) => {
		if (valid){
			if (idxField !== -1){
				updateField(workflowId.value, idxField, fieldForm).then(res=>{
					if (res && res.status == 200){
						ElMessage({
							message: "成功编辑该自定义字段",
							type: "success"
						})
					}
				}).finally(()=>{
					fieldDlgVisible.value = false;
					getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value);
					formEl.resetFields();
				})
			}else{
				addWorkflowField(workflowId.value, fieldForm).then(res=>{
					if (res && res.status == 200){
						ElMessage({
							message: "成功创建自定义字段",
							type: "success"
						})
					}
				}).finally(()=>{
					formEl.resetFields();
					fieldDlgVisible.value = false;
					getAllFieldLIst(workflowId.value, fieldPageSize.value, fieldCurrentPage.value);
				})
			}
		}else{
			console.log('设置打包参数失败!', fields)
		}
	})
}


// 状态相关操作
const usersInfo = ref<any[]>([]);
const userList = ref<any[]>([]);
const roleGroupList = ref<any[]>([]);
const statusDlgVisible = ref(false);
const isAddStatus = ref(false)
const statusTableData = ref<any[]>([]);
let idxStatus: number = -1;
const statusPageSize = ref(20);
const statusCurrentPage = ref(1);
const totalStatus = ref(0);
const statusQueryStr = ref("");

const statusForm = reactive({
	name: '',
	state_type: '',
	participant_type: 0,
	participant: <any[]>[] || null as number | undefined | null,
	enable_retreat: false,
	field_info: <any[]>[],
	order_id: 1,
})

const getAllUserInfo = () => {
  getAllUsers().then((res) => {
    userList.value = res.data.results;
    usersInfo.value = userList.value;
  })
}

getAllUserInfo()

const getRoleGroups = () => {
	getAllGroups().then((res)=>{
		roleGroupList.value = res.data.results;
	})
}

getRoleGroups()

const participantTypeChange = () => {
	statusForm.participant = [];
}

const filterMethod = (query: string) => {
  if (query) {
    usersInfo.value = userList.value.filter((item) => {
      return item.username.toLowerCase().includes(query.toLowerCase()) || item.fullname.toLowerCase().includes(query.toLowerCase())
    })
  } else {
    usersInfo.value = userList.value
  }
}

const statusRules = reactive<FormRules>({
	name: [
			{required: true, message: '状态名称不能为空', trigger: 'blur'},
	],
	state_type: [
			{required: true, message: '状态类型不能为空', trigger: 'change'},
	],
	participant_type: [
			{required: true, message: '参与者类型不能为空', trigger: 'change'},
	],
	participant: [
			{required: true, message: '参与者不能为空', trigger: 'change'},
	]
})

const onCancelStatus = (formEl: FormInstance | null) =>{
  if (!formEl) return;
	statusDlgVisible.value = false;
	isAddStatus.value = false;
	formEl.resetFields();
	statusForm.enable_retreat = false;
	statusForm.state_type = '';
	statusForm.participant_type = 0;
	statusForm.participant = [];
	statusForm.field_info = [];
	statusForm.name = '';
	statusForm.order_id =1;
	idxStatus = -1;
}


const getAllStatusLIst = (workflowId: number, pageSize: number, currentPage: number, name?: string) => {
	getWorkflowStatus(workflowId, pageSize, currentPage, name).then(res => {
    statusTableData.value = res.data.results;
    totalStatus.value = res.data.count;
  });
}

const handleAddStatus = () => {
	isAddStatus.value = true;
	statusDlgVisible.value = true;
}

const handleEditStatus = (row: any) => {
	idxStatus = row.id;
	statusForm.field_info = [];
	workflowStatusDetail(workflowId.value, row.id).then(res=>{
		statusForm.name = res.data.name;
		statusForm.enable_retreat = res.data.enable_retreat;
		statusForm.state_type = res.data.state_type;
		statusForm.participant_type = res.data.participant_type;
		statusForm.order_id = res.data.order_id;
		if (res.data.participant_type !== 3){
			statusForm.participant = res.data.participant_ids;
		}else{
			statusForm.participant = res.data.participant_ids[0]
		}

		res.data.fields.forEach((item: any) => {
      statusForm.field_info.push(item.id);
    })
	}).finally(()=>{
		statusDlgVisible.value = true;
    isAddStatus.value = false;
	})
}

let statusFinalSearch = "";
const handleSearchStatus = () => {
	statusCurrentPage.value = 1;
	statusFinalSearch = statusQueryStr.value;
	getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value, statusQueryStr.value);
};

const onClearStatus = () => {
  statusFinalSearch = '';
	getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value);
}

const handleStatusSizeChange = (page: number, size: number) => {
  statusCurrentPage.value = page;
  statusPageSize.value = size;
	if (statusQueryStr.value != "") {
    statusQueryStr.value = statusFinalSearch;
		getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value, statusQueryStr.value);
	} else {
		getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value);
	}
}

const confirmDeleteStatus = (index: number, row: any) => {
	deleteWorkflowStatus(workflowId.value, row.id).then((res)=>{
		if (res && res.status == 204){
			statusTableData.value.splice(index, 1)
			ElMessage({
						message: "成功删除该状态",
						type: "success"
					})
			getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value);
		}
	}).catch(()=>{
		ElMessage({
			message: "删除该状态失败",
			type: "error"
		})
	})
} 

const onSubmitStatus = async (formEl: FormInstance | null) => {
	if (!formEl) return
	if (typeof statusForm.participant === "number"){
		statusForm.participant = [statusForm.participant]
	}
	await formEl.validate((valid, fields) => {
		if (valid){
			if (idxStatus !== -1){
				updateWorkflowStatus(workflowId.value, idxStatus, statusForm).then(res=>{
					if (res && res.status == 200){
						ElMessage({
							message: "成功编辑该工作流状态",
							type: "success"
						})
					}
				}).finally(()=>{
					statusDlgVisible.value = false;
					getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value);
					formEl.resetFields();
				})
			}else{
				addWorkflowStatus(workflowId.value, statusForm).then(res=>{
					if (res && res.status == 200){
						ElMessage({
							message: "成功创建该工作流状态",
							type: "success"
						})
					}
				}).finally(()=>{
					formEl.resetFields();
					statusDlgVisible.value = false;
					getAllStatusLIst(workflowId.value, statusPageSize.value, statusCurrentPage.value);
				})
			}
		}else{
			console.log('设置工作流状态失败!', fields)
		}
	})
}

// 流转相关操作
const transDlgVisible = ref(false);
const isAddTrans = ref(false)
const transTableData = ref<any[]>([]);
let idxTrans: number = -1;
const transPageSize = ref(20);
const transCurrentPage = ref(1);
const totalTrans = ref(0);
const transQueryStr = ref("");

const transForm = reactive({
	name: '',
	alert_enable: false,
	alert_text: '',
	source_state: null as number | undefined | null,
	dest_state: null as number | undefined | null,
	trans_type: null,
	trigger_types: <any[]>[]
})

const transRules = reactive<FormRules>({
	name: [
			{required: true, message: '流转名称不能为空', trigger: 'blur'},
	],
	source_state: [
			{required: true, message: '源状态不能为空', trigger: 'change'},
	],
	dest_state: [
			{required: true, message: '目的状态不能为空', trigger: 'change'},
	],
	trans_type: [
			{required: true, message: '处理方式不能为空', trigger: 'change'},
	]
})

const onCancelTrans = (formEl: FormInstance | null) =>{
  if (!formEl) return;
	transDlgVisible.value = false;
	isAddTrans.value = false;
	formEl.resetFields();
	transForm.alert_enable = false;
	transForm.trans_type = null;
	transForm.source_state = null;
	transForm.dest_state = null;
	transForm.alert_text = '';
	transForm.name = '';
	transForm.trigger_types = [];
	idxTrans = -1;
}

const getAllTransList = (workflowId: number, pageSize: number, currentPage: number, name?: string) => {
	getTransitions(workflowId, pageSize, currentPage, name).then(res => {
    transTableData.value = res.data.results;
    totalTrans.value = res.data.count;
  });
}

const handleAddTrans = () => {
	isAddTrans.value = true;
	transDlgVisible.value = true;
}

const handleEditTrans = (row: any) => {
	idxTrans = row.id;
	transForm.trigger_types = [];
	transitionDetail(workflowId.value, row.id).then(res=>{
		transForm.name = res.data.name;
		transForm.alert_enable = res.data.alert_enable;
		transForm.alert_text = res.data.alert_text;
		transForm.trans_type = res.data.trans_type;
		transForm.source_state = res.data.source_state;
		transForm.dest_state = res.data.dest_state;
		res.data.triggers.forEach((item: any) => {
      transForm.trigger_types.push(item.type);
    })
	}).finally(()=>{
		transDlgVisible.value = true;
    isAddTrans.value = false;
	})
}

let transFinalSearch = "";
const handleSearchTrans = () => {
	transCurrentPage.value = 1;
	transFinalSearch = transQueryStr.value;
	getAllTransList(workflowId.value, transPageSize.value, transCurrentPage.value, transQueryStr.value);
};

const onClearTrans = () => {
  transFinalSearch = '';
	getAllTransList(workflowId.value, transPageSize.value, transCurrentPage.value);
}

const handleTransSizeChange = (page: number, size: number) => {
  transCurrentPage.value = page;
  transPageSize.value = size;
	if (transQueryStr.value != "") {
    transQueryStr.value = transFinalSearch;
		getAllTransList(workflowId.value, transPageSize.value, transCurrentPage.value, transQueryStr.value);
	} else {
		getAllTransList(workflowId.value, transPageSize.value, transCurrentPage.value);
	}
}

const confirmDeleteTrans = (index: number, row: any) => {
	deleteTransition(workflowId.value, row.id).then((res)=>{
		if (res && res.status == 204){
			transTableData.value.splice(index, 1)
			ElMessage({
						message: "成功删除该流转",
						type: "success"
					})
			getAllTransList(workflowId.value, transPageSize.value, transCurrentPage.value);
		}
	}).catch(()=>{
		ElMessage({
			message: "删除该流转失败",
			type: "error"
		})
	})
} 

const onSubmitTrans = async (formEl: FormInstance | null) => {
	if (!formEl) return
	await formEl.validate((valid, fields) => {
		if (valid){
			if (idxTrans !== -1){
				updateTransition(workflowId.value, idxTrans, transForm).then(res=>{
					if (res && res.status == 200){
						ElMessage({
							message: "成功编辑该流转",
							type: "success"
						})
					}
				}).finally(()=>{
					transDlgVisible.value = false;
					getAllTransList(workflowId.value, transPageSize.value, transCurrentPage.value);
					formEl.resetFields();
				})
			}else{
				addTransition(workflowId.value, transForm).then(res=>{
					if (res && res.status == 200){
						ElMessage({
							message: "成功创建该工作流流转",
							type: "success"
						})
					}
				}).finally(()=>{
					formEl.resetFields();
					transDlgVisible.value = false;
					getAllTransList(workflowId.value, transPageSize.value, transCurrentPage.value);
				})
			}
		}else{
			console.log('设置工作流流转失败!', fields)
		}
	})
}

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
