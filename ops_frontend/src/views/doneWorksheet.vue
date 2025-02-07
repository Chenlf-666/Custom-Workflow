<template>
  <div>
    <el-card header="所有工单信息" style="margin-top: 20px">
      <div>
        <div class="container">
          <div class="handle-box">
            <el-select v-model="flowQueryId" clearable filterable :reserve-keyword="true" class="mr10" @change="flowQueryIdChange" @clear="onClearFlow" style="width: 240px" placeholder="请选择工作流">
              <el-option v-for="item in workflowList" :label="item.name" :key="item.id" :value="item.id"/>
            </el-select>
            <el-select v-model="completedStatus" clearable class="mr10" @change="statusChange" @clear="onClearStatus" style="width: 240px" placeholder="请选择完成状态">
              <el-option v-for="item in statusInfo" :label="item.name" :key="item.id" :value="item.id"/>
            </el-select>
            <el-input v-model="queryTickets" clearable placeholder="请输入工单名称" class="handle-input mr10" @clear="onClearQueryTickets"/>
            <el-button type="primary" :icon="Search" @click="searchTickets">搜索</el-button>
          </div>
          <el-table :data="ticketsTableData" border stripe table-layout='auto' ref="multipleTable" header-cell-class-name="table-header">
            <el-table-column prop="name" label="任务名称"></el-table-column>
            <el-table-column prop="workflow_name" label="类型"></el-table-column>
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
              <template #default="scope">
                <div v-for="(value, index) in scope.row.display_values" :key="index">
                  <span v-for="(itemValue, itemName) in value" :key="itemName">
                    {{ itemName }}: {{ itemValue }}<br>
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="创建时间" :formatter="dateFormat" sortable></el-table-column>
            <el-table-column prop="update_time" label="更新时间" :formatter="dateFormat" sortable></el-table-column>
            <el-table-column label="操作" width="220px" align="center">
            <template #default="scope">
              <el-button text type="primary" :icon="Edit" @click="handleViewTicket(scope.row)" v-permission="'super'" >
                详情
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

        <form-info
          :dialog-visible="viewTicketDlgVisble"
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
</template>

<script setup lang="ts" name="basetable">
import {ref, reactive, watch} from 'vue';
import {ElMessage} from 'element-plus';
import {Delete, Edit, Search} from '@element-plus/icons-vue';
import type {FormRules} from 'element-plus';
import { dateFormat } from '../utils/dateFormat';
import {getCusWorkflowList, getTickets, addTickets, ticketsDetail, deleteTickets, getCurrentFields, getInitialTicketRelatedUrls, getEditTicketRelatedUrls} from '../api/cusWorkflow';
import axios from "../axios";
import formInfo from "@/components/workflows/customTicketForm.vue";


let ticketIdx: number = -1;

const viewTicketDlgVisble = ref(false);
const workflowId = ref()
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

const ruleForm = reactive({
  workflow: null as number | null | undefined,
  name: "",
  transition: null as number | null | undefined
})

const getAllWorkflows = () => {
	getCusWorkflowList().then(res => {
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
      ruleForm[item.field_key] = [9,10,11,12,13,14].includes(item.field_type) ? JSON.parse(item.default_value) : item.default_value;
      if(item.field_type == 4){
        ruleForm[item.field_key] = item.default_value == "1" ? true : false
      }
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
    }else if ([5,6,7].includes(item.field_type)){
      formItem.type = 'datepicker';
      formItem.dateType = item.field_type == 5 ? 'date' : (item.field_type == 6 ? 'datetime' : 'datetimerange');

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

const onCancelViewTicket = (isEdit: boolean) => {
  ticketIdx = -1;
  viewTicketDlgVisble.value = false;
  if (isEdit){
    getTicketsList(undefined, ticketsPageSize.value, ticketsCurrentPage.value)
  }
}

//所有工单信息

const flowQueryId = ref()
const completedStatus = ref()
const statusInfo = [{"name":"已完成", "id": true}, {"name":"未完成","id":false}]
const queryTickets = ref('')
const ticketsTableData = ref<any[]>([])
const ticketsCurrentPage = ref(1)
const ticketsPageSize = ref(20)
const totalTickets = ref(0)

const customColors = [
  { color: 'darkred', percentage: 21 },
  { color: 'red', percentage: 41 },
  { color: 'orangered', percentage: 61 },
  { color: 'orange', percentage: 81 },
  { color: 'green', percentage: 100 },
]

let finalFlowId = ''
let finalTicketsName = ''
let finalStatus = ''

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

const getTicketsList = (workflowId?: any, pageSize?: any, pageNum?: any, name?:string, isCompleted?: any) => {
  getTickets(workflowId, pageSize, pageNum, name, isCompleted, "worked").then((res)=>{
    ticketsTableData.value = res.data.results;
    totalTickets.value = res.data.count;
  })
}

getTicketsList(undefined, ticketsPageSize.value, ticketsCurrentPage.value)

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

    // if (res && res.data.current_fields.length) {
    //   for (let item of res.data.current_fields) {
    //     const formItem = await switchFormItem(item);
    //
    //     // formRules[formItem.prop] = [{ required: formItem.required, message: formItem.label + "不能为空",
    //     //   trigger: [1,2,3,4,5,6,7,8,9].includes(formItem.field_type) ? "blur" : "change" }];
    //
    //     formRules[formItem.prop] = [{ required: formItem.required, message: formItem.label + "不能为空", trigger: "blur" }];
    //
    //     formItems.value.push(formItem);
    //   }
    // }
    //
    // if (res && res.data.transitions.length) {
    //   for (let item of res.data.transitions) {
    //     const transitionItem = await switchFormItem(item, true);
    //     transitionItems.value.push(transitionItem);
    //   }
    // }
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

const flowQueryIdChange = (v: any) => {
  flowQueryId.value = v
} 

const onClearFlow = () => {
  finalFlowId = ''
}

const statusChange = (v: any) => {
  completedStatus.value = v
}

const onClearStatus = () => {
  finalStatus = ''
}

const onClearQueryTickets = () => {
  finalTicketsName = ''
}

const searchTickets = () => {
  finalFlowId = flowQueryId.value
  finalTicketsName = queryTickets.value
  finalStatus = completedStatus.value
  ticketsCurrentPage.value = 1
  getTicketsList(finalFlowId, ticketsPageSize.value, ticketsCurrentPage.value, finalTicketsName, finalStatus)
}

const handleTicketsPageChange = (page: number, size: number) => {
  ticketsCurrentPage.value = page;
  ticketsPageSize.value = size;
  queryTickets.value = finalTicketsName;
  flowQueryId.value = finalFlowId;
  completedStatus.value = finalStatus;
  getTicketsList(flowQueryId.value, ticketsPageSize.value, ticketsCurrentPage.value, queryTickets.value, completedStatus.value);
}

const handleDeleteTicket = (index: number, row: any) => {
	deleteTickets(row.id).then((res)=>{
		if (res && res.status == 204){
			ticketsTableData.value.splice(index, 1)
			ElMessage({
						message: "成功删除此工单",
						type: "success"
					})
			getTicketsList(flowQueryId.value, ticketsPageSize.value, ticketsCurrentPage.value, queryTickets.value, completedStatus.value)
		}
	}).catch(()=>{
		ElMessage({
						message: "删除此工单失败",
						type: "error"
					})
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

.checkbox-group {
  border: 1px solid #ebeef5;
  padding: 10px 15px;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  align-items: center;
}

</style>
