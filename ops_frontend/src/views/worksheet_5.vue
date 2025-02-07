<template>
  <div v-if="isVisible">
    <div v-if="workflowId">
      <el-card>
        <div>
          <div class="container">
            <div class="handle-box">
              <el-select v-model="completedStatus" clearable class="mr10" @change="statusChange" @clear="onClearStatus" style="width: 240px" placeholder="请选择完成状态">
                <el-option v-for="item in statusInfo" :label="item.name" :key="item.id" :value="item.id"/>
              </el-select>
              <el-select v-model="currentTicketType" clearable class="mr10" @change="ticketTypeChange" style="width: 240px"  placeholder="请选择事务类型">
                <el-option v-for="item in ticketType" :label="item.name" :key="item.id" :value="item.id"/>
              </el-select>
              <el-input v-model="queryTickets" clearable placeholder="请输入任务名称" class="handle-input mr10" @clear="onClearQueryTickets"/>
              <el-button type="primary" :icon="Search" @click="searchTickets">搜索</el-button>
              <el-button type="primary" @click="addSheet" style="margin-left: 20px">新建</el-button>
            </div>
            <el-table :data="ticketsTableData" border stripe table-layout='auto' ref="multipleTable" header-cell-class-name="table-header">
              <el-table-column prop="name" label="任务名称"></el-table-column>
              <el-table-column prop="status_name" label="当前状态">
                <template #default="scope">
                  <div class="flex items-center">
                    <div class="demo-progress">
                      <el-progress type="circle" :percentage="scope.row.status_process" :width="25" :show-text="false" :color="customColors"/>
                    </div>
                    <span class="ml-2">{{ scope.row.status_name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="creator" label="创建人"></el-table-column>
              <el-table-column label="详细内容" width="500px">
                <template #default="{ row }">
                <el-table :data="row.display_values" style="border: none;" :show-header="false">
                  <el-table-column label="Key" align="left" width="120px">
                    <template #default="{ row: detailRow }">
                      {{ Object.keys(detailRow)[0] }}
                    </template>
                  </el-table-column>
                  <el-table-column label="Value" align="left">
                    <template #default="{ row: detailRow }">
                      <span v-html="formatNewlines(Object.values(detailRow)[0])"></span>
                    </template>
                  </el-table-column>
                </el-table>
              </template>
              </el-table-column>
              <el-table-column prop="create_time" label="创建时间" :formatter="dateFormat" sortable></el-table-column>
              <el-table-column prop="update_time" label="更新时间" :formatter="dateFormat" sortable width="200px"></el-table-column>
              <el-table-column label="操作" width="220px" align="center">
              <template #default="scope">
                <el-button text type="primary" :icon="Edit" @click="handleViewTicket(scope.row)">
                  详情
                </el-button>
                <el-button text type="primary" :icon="RefreshRight" @click="handleAssignTicket(scope.row)" 
                  :disabled="!scope.row.operators.some(userItem => userItem === user.fullname)">
                  移交
              </el-button>
              </template>
              </el-table-column>
            </el-table>
            <div class="pagination">
              <Pagination
                :current-page="ticketsCurrentPage"
                :page-size="ticketsPageSize"
                :total="totalTickets"
                @onPageChange="handleTicketsPageChange"
              />
            </div>
          </div>

          <el-dialog
            v-model="initTicketDlgVisble"
            :close-on-click-modal=false
            title="详情"
            width="50%"
            :destroy-on-close="true"
            @closed="onCancel(ruleFormRef)"
          >
            <el-form ref="ruleFormRef" :model="ruleForm" label-width="120px" :rules = "formRules">
            <el-form-item label="名称" prop="name">
              <el-input v-model="ruleForm.name" />
            </el-form-item>
            <template v-for="item in formItems">
              <el-form-item :label="item.label" :prop="item.prop" v-if="item.type === 'input'" :key="item.prop">
                <el-input v-model="ruleForm[item.prop]" />
              </el-form-item>
              <el-form-item :label="item.label" :prop="item.prop" v-if="item.type === 'textarea'" :key="item.prop">
                <el-input v-model="ruleForm[item.prop]" type="textarea"/>
              </el-form-item>
              <el-form-item :label="item.label" :prop="item.prop" v-if="item.type === 'select' && (item.special_url == '' || item.special_url == null )" :key="item.prop">
                <el-select v-model="ruleForm[item.prop]" filterable :multiple = item.multiple>
                  <el-option v-for="nitem in item.options" :label="nitem.value" :key="nitem.key" :value="nitem.key"/>
                </el-select>
              </el-form-item>
              <el-form-item :label="item.label" :prop="item.prop" v-if="item.type === 'select-param-special-url'" :key="item.prop">
                <el-select v-model="ruleForm[item.prop]" filterable :multiple = item.multiple>
                  <el-option v-for="nitem in specialUrlOptions" :label="nitem.name" :key="nitem.id" :value="nitem.id"/>
                </el-select>
              </el-form-item>
              <el-form-item :label="item.label" :prop="item.prop" v-if="item.type === 'select-for-foreign-key' || (item.type === 'select' && item.special_url && item.special_url.includes('/') )" :key="item.prop">
                <el-select v-model="ruleForm[item.prop]" filterable :multiple = item.multiple>
                  <el-option v-for="nitem in item.options" :label="nitem.name" :key="nitem.id" :value="nitem.id"/>
                </el-select>
              </el-form-item>
              <el-form-item :label="item.label" :prop="item.prop" v-if="item.type === 'radio'" :key="item.prop">
                <el-radio-group v-model="ruleForm[item.prop]">
                  <el-radio v-for="nitem in item.options" :label="nitem.key" :key="nitem.key" size="large">{{ nitem.value }}</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item :label="item.label" :prop="item.prop" v-if="item.type === 'checkbox'" :key="item.prop">
                <el-checkbox-group v-model="ruleForm[item.prop]">
                  <el-checkbox v-for="nitem in item.options" :label="nitem.key" :key="nitem.key" size="large">{{ nitem.value }}</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item :label="item.label" v-if = "item.type === 'switch'" :key="item.prop">
                <el-switch v-model="ruleForm[item.prop]" />
              </el-form-item>
              <el-form-item :label="item.label" v-if = "item.type === 'datepicker'" :key="item.prop">
                <el-date-picker v-model="ruleForm[item.prop]" :type="item.dateType" style="width: 100%" value-format="YYYY-MM-DD"/>
              </el-form-item>
              <el-form-item :label="item.label" v-if = "item.type === 'datepickerTime'" :key="item.prop">
                <el-date-picker v-model="ruleForm[item.prop]" :type="item.dateType" style="width: 100%" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss"/>
              </el-form-item>
            </template>
            </el-form>
            <span class="dialog-footer">
            <template v-for="item in transitionItems">
              <el-popconfirm
                v-if="item.alert_enable"
                :key="'popconfirm-' + item.id"
                confirm-button-text="确定"
                cancel-button-text="取消"
                icon="el-icon-info"
                icon-color="red"
                :title="item.alert_text"
                :content="item.alert_text"
                @confirm="onSubmit(ruleFormRef, item)"
                placement="right"
                width="200px"
              >
                <template #reference>
                  <el-button
                    type="primary"
                    :key="'popconfirm-' + item.id"
                  >
                    {{ '流转' + item.name }}
                  </el-button>
                </template>
              </el-popconfirm>
              <el-button
                v-else
                type="primary"
                @click="onSubmit(ruleFormRef, item)"
                :key="'button-' + item.id"
              >
                {{ '流转: ' + item.name }}
              </el-button>
            </template>
            </span>
          </el-dialog>

          <form-info
            :dialog-visible="viewTicketDlgVisble"
            :assign-dlg-visible="assignDlgVisible"
            :form-items="formItems"
            :transition-items="transitionItems"
            :ticket-id="ticketIdx"
            :enable-retreat="enableRetreat"
            :creator-name="creatorName"
            :nrule-form="ruleForm"
            :all-status-steps="allStatusSteps"
            :nspecial-url-field="specialUrlField"
            :nwhole-special-url="wholeSpecialUrl"
            :nwhole-special-url-bak="wholeSpecialUrlBak"
            :nspecial-url-options="specialUrlOptions"
            :current-status="currentStatus"
            :formRules="formRules"
            @onChange="onCancelViewTicket"
          />
        </div>
      </el-card>
    </div>
    <div class="error-page" v-else>
      <div class="error-code">4<span>0</span>4</div>
      <div class="error-desc">啊哦~ 你所访问的页面不存在</div>
      <div class="error-handle">
        <router-link to="/">
          <el-button type="primary" size="large">返回首页</el-button>
        </router-link>
        <el-button class="error-btn" type="primary" size="large" @click="goBack">返回上一页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" name="basetable">
import {ref, reactive, watch, onBeforeMount, onMounted} from 'vue';
import {ElMessage} from 'element-plus';
import {Delete, Edit, Search, RefreshRight} from '@element-plus/icons-vue';
import type {FormInstance, FormRules} from 'element-plus';
import { dateFormat } from '../utils/dateFormat';
import {getCusWorkflowList, getInitStatus, getTickets, addTickets, ticketsDetail, deleteTickets, getCurrentFields, getInitialTicketRelatedUrls, getEditTicketRelatedUrls} from '../api/cusWorkflow';
import axios from "../axios";
import formInfo from "@/components/workflows/customTicketForm.vue";
import { getUserInfo } from '@/api/user';
import Pagination from '@/components/Pagination.vue';
import { useRouter } from 'vue-router';
import {useUserStore} from "@/store/user";
import {storeToRefs} from "pinia";


let ticketIdx: number = -1;

const isVisible = ref(false);

const ruleFormRef = ref(null);
const initTicketDlgVisble = ref(false);
const viewTicketDlgVisble = ref(false);
const workflowId = ref(0)
const workflowList = ref<any[]>([])
const formItems = ref<any[]>([])
const transitionItems = ref<any[]>([])
const enableRetreat = ref(false)
const creatorName = ref('')
const specialUrlField = ref('')
const wholeSpecialUrl = ref('')
const wholeSpecialUrlBak = ref('')
const specialUrlOptions = ref<any[]>([])
const formRules = reactive<FormRules>({});

const userStore = useUserStore();
const {user} = storeToRefs(userStore);

const ruleForm = reactive({
  workflow: null as number | null | undefined,
  name: "",
  transition: null as number | null | undefined
})

const customColors = [
  { color: 'darkred', percentage: 21 },
  { color: 'red', percentage: 41 },
  { color: 'orangered', percentage: 61 },
  { color: 'orange', percentage: 81 },
  { color: 'green', percentage: 100 },
]

const router = useRouter();
const goBack = () => {
	router.go(-1);
};

const getAllWorkflows = () => {
	getCusWorkflowList(undefined, undefined, undefined, true).then(res => {
		workflowList.value = res.data.results;
	})
}

getAllWorkflows()

const resetRuleForm = () => {
  // 删除除 'workflow' 和 'name' 及 'transition' 之外的其他属性
  Object.keys(ruleForm).forEach(key => {
    if (key !== 'workflow' && key !== 'name' && key ! && key !== 'transition') {
      delete ruleForm[key];
    }
  });

  ruleForm.workflow = null;
  ruleForm.name = "";
  ruleForm.transition = null;
}

const addSheet = async () => {
  formRules.value = {};
  formItems.value = [];
  transitionItems.value = [];
  resetRuleForm();

  const initStatusResponse = await getInitStatus(workflowId.value);

  if (initStatusResponse.status === 200) {
    for (let item of initStatusResponse.data.fields) {
      const formItem = await switchFormItem(item);

      // formRules[formItem.prop] = [{ required: formItem.required, message: formItem.label + "不能为空",
      //   trigger: [1,2,3,4,5,6,7,8,9].includes(formItem.field_type) ? "blur" : "change" }];

      formRules[formItem.prop] = [{ required: formItem.required, message: formItem.label + "不能为空", trigger: "blur" }];

      formItems.value.push(formItem);
    }

    formRules["name"] = [{ required: true, message: "请填写名称!", trigger: "blur"}]
    for (let item of initStatusResponse.data.transitions) {
      const transitionItem = await switchFormItem(item, true);
      transitionItems.value.push(transitionItem);
    }

    initTicketDlgVisble.value = true;
  }
};

const switchFormItem = async (item: any, isTransition: boolean = false) => {
  let formItem = <any>{
    label: item.name,
    prop: item.field_key,
    required: item.required
  }
  if (isTransition) {
    return {
      type: 'transition',
      alert_enable: item.alert_enable,
      alert_text: item.alert_text,
      id: item.id,
      name: item.name
    };
  }else{
    if(item.default_value){
      if ([7].includes(item.field_type)){
        ruleForm[item.field_key] = JSON.parse(item.default_value.replace(/'/g, '"'))
      }else{
        ruleForm[item.field_key] = [9,10,11,12,13,14].includes(item.field_type) ? JSON.parse(item.default_value) : item.default_value;
      }
    }

    if(item.default_value == "" && item.field_type == 4){
      ruleForm[item.field_key] = false
    }

    if(item.field_value){
      ruleForm[item.field_key] = [9,10,11,12,13,14].includes(item.field_type) ? JSON.parse(item.field_value) : item.field_value;
      if(item.field_type == 4){
        ruleForm[item.field_key] = item.field_value
      }
    }

    if ([1, 2, 3].includes(item.field_type)){
      formItem.type = 'input';
    }else if (item.field_type == 8){
      formItem.type = 'textarea';
    }else if ([10,13].includes(item.field_type)){
      formItem.multiple = item.field_type == 13 ? true : false;
      if (item.special_url){
        if (item.special_url.includes('<')){
          specialUrlField.value = item.special_url.match(/<(.*?)>/)[1];
          wholeSpecialUrl.value = item.special_url;
          wholeSpecialUrlBak.value = item.special_url;
          formItem.type = 'select-param-special-url';
        }else{
          const options = await getSelectOptions(item);
          formItem.type = 'select';
          formItem.options = options;
          formItem.special_url = item.special_url;
        }
      }else{
        let cleanedChoice = item.field_choice.replace(/，/g, ',').replace(/“/g, '"').replace(/”/g, '"').replace(/'/g, '"');
        formItem.type = 'select';
        formItem.options = JSON.parse(cleanedChoice);
      }

    }else if ([9,12].includes(item.field_type)){
      let cleanedChoice = item.field_choice.replace(/，/g, ',').replace(/“/g, '"').replace(/”/g, '"');
      formItem.type = item.field_type == 12 ? 'checkbox' : 'radio';
      formItem.options = JSON.parse(cleanedChoice);
    }else if (item.field_type == 4){
      formItem.type = 'switch';
    }else if ([5].includes(item.field_type)){
      formItem.type = 'datepicker';
      formItem.dateType = 'date';
    }else if ([6,7].includes(item.field_type)){
      formItem.type = 'datepickerTime';
      formItem.dateType = item.field_type == 6 ? 'datetime' : 'datetimerange';
    }else if ([11,14].includes(item.field_type)){
      const options = await getForeignOptions(item);
      formItem.type = 'select-for-foreign-key';
      formItem.multiple = item.field_type == 14 ? true : false;
      formItem.options = options;
   }
    return formItem;
  }
}

const getForeignOptions = async (item) => {
  return new Promise((resolve, reject) => {
    if (ticketIdx == -1){
      getInitialTicketRelatedUrls(workflowId.value, item.id).then((res) => {
        if (res && res.status == 200) {
          axios.get(res.data.url).then((nres) => {
            const options = nres.data.results;
            resolve(options);
          })
        } else {
          reject("Failed to get options");
        }
      })
    }else{
      getEditTicketRelatedUrls(ticketIdx, item.id).then((res) => {
        if (res && res.status == 200) {
          axios.get(res.data.url).then((nres) => {
            const options = nres.data.results;
            resolve(options);
          })
        } else {
          reject("Failed to get options");
        }
      })
    }
  })
};

const getSelectOptions = async (item) => {
  return new Promise((resolve, reject) => {
    axios.get(item.special_url).then((res) => {
      if (res && res.status == 200){
        const options = res.data.results;
        resolve(options);
      } else{
        reject("Failed to get options");
      }
    })
  })
}

const onCancel = (formEl: FormInstance | null) => {
  if (!formEl) return;
  initTicketDlgVisble.value = false;
  ruleForm.name = '';
  formEl.resetFields();
}

const onCancelViewTicket = (isEdit: boolean) => {
  ticketIdx = -1;
  viewTicketDlgVisble.value = false;
  assignDlgVisible.value = false;
  if (isEdit){
    getTicketsList(workflowId.value, ticketsPageSize.value, ticketsCurrentPage.value, "", "", currentTicketType.value)
  }
}

// 创建工单包含初始化流转操作
const onSubmit = async (formEl: FormInstance | null, item: any) => {
if (!formEl) return
await formEl.validate((valid, fields) => {
  if (valid) {
    ruleForm.transition = item.id
    ruleForm.workflow = workflowId.value;
    addTickets(ruleForm).then(res => {
      if (res && res.status == 201){
        ElMessage({
          message: "创建成功!",
          type: "success"
        })
      }
      }).finally(()=>{
        initTicketDlgVisble.value = false
        getTicketsList(workflowId.value, ticketsPageSize.value, ticketsCurrentPage.value, "", "", currentTicketType.value)
      })
    }
  })
}

//所有工单信息

const completedStatus = ref()
const currentTicketType = ref()
const statusInfo = [{"name":"已完成", "id": true}, {"name":"未完成","id":false}]
const ticketType = [{"name": "待办的事务", "id": "duty"}, {"name": "我发起的事务", "id": "owner"}, {"name": "我参与的事务", "id": "worked"}]
const queryTickets = ref('')
const ticketsTableData = ref<any[]>([])
const ticketsCurrentPage = ref(1)
const ticketsPageSize = ref(20)
const totalTickets = ref(0)
let finalTicketsName = ''
let finalStatus = ''
let finalTicketType = ''
const assignDlgVisible = ref(false);

watch(ruleForm, (value)=>{
  if (specialUrlField.value in ruleForm && ruleForm[specialUrlField.value] !== undefined) {
    specialUrlOptions.value = []
      wholeSpecialUrl.value = wholeSpecialUrl.value.replace(/<.*?>/g, ruleForm[specialUrlField.value])
      axios.get(wholeSpecialUrl.value).then((res)=>{
        if (res && res.status == 200){
          specialUrlOptions.value = res.data.results
        }
      }).finally(()=>{
        wholeSpecialUrl.value = wholeSpecialUrlBak.value //还原
      })
    }
},{
  deep: true
})

const getTicketsList = (workflowId?: any, pageSize?: any, pageNum?: any, name?:string, isCompleted?: any, ticketType?: any) => {
  getTickets(workflowId, pageSize, pageNum, name, isCompleted, ticketType).then((res)=>{
    ticketsTableData.value = res.data.results;
    totalTickets.value = res.data.count;
  })
}

function formatNewlines(text) {
  if (text === undefined || text === null) {
    return '';
  }
  return String(text).replace(/\n/g, '<br>');
}

// 查询工单信息相关代码

const allStatusSteps = ref<any[]>([])
const currentStatus = ref()

const handleViewTicket = async (row: any) => {
  formRules.value = {};
  resetRuleForm();
  formItems.value = [];
  transitionItems.value = [];
  allStatusSteps.value = [];

  await getCurrentFields(row.id).then(async (res) => {
    ticketIdx = res.data.id;
    ruleForm.name = res.data.name;
    enableRetreat.value = res.data.enable_retreat;
    creatorName.value = res.data.creator;

    if (res.data.operators.includes(user.value.fullname)) {
      if (res && res.data.current_fields.length) {
        for (let item of res.data.current_fields) {
          const formItem = await switchFormItem(item);

          formRules[formItem.prop] = [{
            required: formItem.required, message: formItem.label + "不能为空",
            trigger: [1, 2, 3, 4, 5, 6, 7, 8, 9].includes(formItem.field_type) ? "blur" : "change"
          }];

          formItems.value.push(formItem);
        }
      }

      if (res && res.data.transitions.length) {
        for (let item of res.data.transitions) {
          const transitionItem = await switchFormItem(item, true);
          transitionItems.value.push(transitionItem);
        }
      }
    }
  });

  // 获取工单进度数据
  await ticketsDetail(row.id).then((res) => {
    if (res && res.status == 200) {
      allStatusSteps.value = res.data.status_list;
      currentStatus.value = res.data.status;
    }
  });

  viewTicketDlgVisble.value = true;
};

const handleAssignTicket = (row: any) => {
  ticketIdx = row.id;
  assignDlgVisible.value = true
}


const statusChange = (v: any) => {
  completedStatus.value = v
}

const ticketTypeChange = (v: any) => {
  currentTicketType.value = v
}

const onClearStatus = () => {
  finalStatus = ''
}

const onClearQueryTickets = () => {
  finalTicketsName = ''
}

const searchTickets = () => {
  finalTicketsName = queryTickets.value
  finalStatus = completedStatus.value
  finalTicketType = currentTicketType.value
  ticketsCurrentPage.value = 1
  getTicketsList(workflowId.value, ticketsPageSize.value, ticketsCurrentPage.value, finalTicketsName, finalStatus, finalTicketType)
}

const handleTicketsPageChange = (page: number, size: number) => {
  ticketsCurrentPage.value = page;
  ticketsPageSize.value = size;
  queryTickets.value = finalTicketsName;
  completedStatus.value = finalStatus;
  currentTicketType.value = finalTicketType;
  getTicketsList(workflowId.value, ticketsPageSize.value, ticketsCurrentPage.value, queryTickets.value, completedStatus.value, currentTicketType.value);
}

onBeforeMount(() => {
  getUserInfo().then((res => {
    if (res && res.status == 200) {
      const lastMenu = res.data.authed_menus.find(menu => menu.label === "审批流程");
      if (lastMenu.children.length > 0) {
        // 过滤出包含 workflow_id 的项
        const validChildren = lastMenu.children.filter(child => child.workflow_id);
        if (validChildren.length > 4) {
          workflowId.value = validChildren[4].workflow_id;
          getTicketsList(workflowId.value, ticketsPageSize.value, ticketsCurrentPage.value, "", "", currentTicketType.value);
        }
      }
    }
  }))
})

onMounted(() => {
  setTimeout(() => {
    isVisible.value = true;
  }, 500); // 延迟 0.2 秒
});

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

.checkbox-group {
  border: 1px solid #ebeef5;
  padding: 10px 15px;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  align-items: center;
}

.error-page {
	display: flex;
	justify-content: center;
	align-items: center;
	flex-direction: column;
	width: 100%;
	height: 100%;
	background: #f3f3f3;
	box-sizing: border-box;
}
.error-code {
	line-height: 1;
	font-size: 250px;
	font-weight: bolder;
	color: #2d8cf0;
}
.error-code span {
	color: #00a854;
}
.error-desc {
	font-size: 30px;
	color: #777;
}
.error-handle {
	margin-top: 30px;
	padding-bottom: 200px;
}
.error-btn {
	margin-left: 100px;
}

</style>
