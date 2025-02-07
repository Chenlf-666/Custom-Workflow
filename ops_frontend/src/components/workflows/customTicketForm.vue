<template>
  <div>
    <el-dialog
      v-model="viewTicketDlgVisble"
      :close-on-click-modal=false
      :title="'工单详情: ' + ruleForm.name"
      width="65%"
      :destroy-on-close="true"
      @closed="onViewCancel(ruleFormRef)"
    >
      <el-collapse v-model="activeNames">
        <el-collapse-item title="操作日志" name="1">
          <el-steps process-status="wait" align-center direction="vertical">
            <el-step
              v-for="step in allLogList"
              :key="step.id"
              :description="`${step.participant} 于 ${new Date(step.create_time).toLocaleString()} ${step.source_state ? '在 ' + step.source_state + ' 状态下' : ''}执行了 ${step.transition_name} 操作`"
            >
            </el-step>
          </el-steps>
        </el-collapse-item>
        <el-collapse-item title="工单进度" name="2">
          <el-steps :active="props.allStatusSteps?.findIndex(step => step.id === props.currentStatus)" finish-status="success" align-center>
            <el-step
              v-for="step in props.allStatusSteps"
              :key="step.id"
              :title="step.name"
            >
              <template #description>
                <div v-for="(field, index) in step.fields" :key="index" style="font-size: 11px">
                  <template v-if="field.field_name !== undefined">
                    <span :style="{color : 'black', width: '100px', textAlign: 'left'}">{{ field.field_name + ': ' }} </span>
                    <span v-if="field.display_value !== undefined" :style="{ color: 'green' }">{{ field.display_value }}</span>
                  </template>
                  <template v-if="index !== step.fields.length - 1 && field.field_name !== undefined"><br></template>
                </div>
                <div v-for="user in step.users" :key="user.name">
                  <span :style="{ color: user.is_confirm ? '#63AF57' : '' }">{{ user.name }}: {{ user.is_confirm ? '已确认' : '未确认' }}</span>
                  <br />
                </div>
              </template>
            </el-step>
          </el-steps>
        </el-collapse-item>
        <el-collapse-item title="工单信息" name="3" v-if = 'props.formItems?.length' >
          <el-form ref="ruleFormRef" :model="ruleForm" label-width="120px" :rules="props.formRules">
            <template v-for="item in props.formItems">
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
                  <el-option v-for="nitem in specialUrlOptions" :label="nitem.name" :key="nitem.name" :value="nitem.name"/>
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
        </el-collapse-item>
      </el-collapse>
      <span class="dialog-footer">
        <!-- <el-button  type="primary" @click="onSubmit(ruleFormRef, item, true)" >
          编辑
        </el-button> -->
        <template v-for="item in props.transitionItems">
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
                style="margin-top: 10px"
              >
                {{ item.name }}
              </el-button>
            </template>
          </el-popconfirm>
          <el-button
            v-else
            type="primary"
            @click="onSubmit(ruleFormRef, item)"
            :key="'button-' + item.id"
            style="margin-top: 10px;"
          >
            {{ item.name }}
          </el-button>
        </template>
        <el-button type="danger" @click="onRetreat" v-if="props.enableRetreat" style="margin-top: 10px" :disabled="props.creatorName !== user.fullname">
          撤回
        </el-button>
      </span>
    </el-dialog>

    <el-dialog
        v-model="assignTicketDlgVisible"
        appendToBody 
        :close-on-click-modal=false
        title='移交工单'
        width="50%"
        @closed="onAssignCancel(ruleFormRef)"
      >
        <el-form :rules="rules" :model="ruleForm" label-width="150px" ref="ruleFormRef">
          <el-form-item label="移交用户" prop="user_ids">
            <el-select v-model="ruleForm.user_ids"
                       placeholder="请选择移交的用户"
                       filterable
                       multiple
                       :filter-method="filterMethod"
                       style="width:500px" >
              <el-option v-for="item in usersInfo" :label="item.fullname" :key="item.id" :value="item.id"/>
            </el-select>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="onAssignCancel(ruleFormRef)">取 消</el-button>
            <el-button type="primary" @click="onAssignSubmit(ruleFormRef)">确 定</el-button>
          </span>
        </template>
      </el-dialog>
  </div>
</template>

<script setup lang="ts" name="basetable">
import {ref, reactive, watch} from 'vue';
import {ElMessage, ElMessageBox} from 'element-plus';
import {Delete, Edit, Search} from '@element-plus/icons-vue';
import type {FormInstance, FormRules} from 'element-plus';
import {getAllUsers} from '../../api/user';
import { updateTickets, addTicketsTransition, addTicketRetreat, getTicketsLog, assignTickets} from '../../api/cusWorkflow';
import axios from "../../axios";
import { storeToRefs } from 'pinia';
import { useUserStore } from "../../store/user";

const userStore = useUserStore();
const { user } = storeToRefs(userStore);
const ruleFormRef = ref(null)
const viewTicketDlgVisble = ref(false)
const assignTicketDlgVisible = ref(false)
const pageSize = ref(20)
const specialUrlField = ref('')
const wholeSpecialUrl = ref('')
const wholeSpecialUrlBak = ref('')
const specialUrlOptions = ref<any[]>([])
const allLogList = ref<any[]>([])
let activeNames = ["2", "3"]
const usersInfo = ref<any[]>([])


const props = defineProps({
  dialogVisible: Boolean,
  assignDlgVisible: Boolean,
  formItems: {
    type: Array as () => Array<{ prop: string, type: string, label: string, multiple: boolean, special_url: string, 
      options: Array<{ name: string, key: string, value: string, id: number }>, dateType: string }>
  },
  transitionItems: {
    type: Array as () => Array<{ alert_enable: boolean, alert_text: string, id: number, name: string }>
  },
  ticketId: {
    type: Number,
    default: -1
  },
  allStatusSteps: {
    type: Array as () => Array<{ id: number, name: string, fields: Array<{ field_name: string, display_value: string }>, users: Array<{ name: string, is_confirm: boolean }> }>
  },
  nspecialUrlOptions: {
    type: Array
  },
  formRules: {
    type: Object
  },
  currentStatus: Number,
  nspecialUrlField: String,
  nwholeSpecialUrl: String,
  nwholeSpecialUrlBak: String,
  enableRetreat: Boolean,
  creatorName: String,
  nruleForm: {}
})

interface FormDisplayEmits {
  (event: 'onChange', edit: boolean): void;
}

interface UserItem {
  email: string;
  first_name: string;
  fullname: string;
  id: number;
  is_superuser: boolean;
  last_name: string;
  username: string
}

const emits = defineEmits<FormDisplayEmits>();
const UserList = ref<UserItem[]>([]);

const ruleForm = reactive({
  workflow: null as number | null | undefined,
  name: "",
  transition: null as number | null | undefined,
  user_ids: []  
})

const getAllUserInfo = () => {
  getAllUsers().then((res) => {
    UserList.value = res.data.results;
    usersInfo.value = UserList.value;
  })
}

const rules = reactive<FormRules>({
	user_ids: [
		{ required: true, message: '请选择需要移交的用户!', trigger: 'change' },
	]
})

const onSubmit = async (formEl: FormInstance | null, item: any, isEdit: boolean = false) => {
  if (!formEl) {
    ruleForm.transition = item.id
    addTicketsTransition(props.ticketId, ruleForm).then(res => {
      if (res && res.status == 200){
        ElMessage({
            message: "流转成功",
            type: "success"
          })
        }
      }).finally(()=>{
        emits('onChange', true);
        viewTicketDlgVisble.value = false
      })
  }else{
    await formEl.validate((valid, fields) => {
    if (valid) {
      if (isEdit){
        updateTickets(props.ticketId, ruleForm).then((res)=>{
          if (res && res.status == 200){
            ElMessage({
              message: "编辑成功",
              type: "success"
            })
          }
        }).finally(()=>{
          emits('onChange', true);
          viewTicketDlgVisble.value = false
        })
      }else{
        ruleForm.transition = item.id
        addTicketsTransition(props.ticketId, ruleForm).then(res => {
          if (res && res.status == 200){
            ElMessage({
                message: "流转成功",
                type: "success"
              })
            }
          }).finally(()=>{
            emits('onChange', true);
            viewTicketDlgVisble.value = false
          })
        }
      }
    })
  }
}

const onRetreat = () => {
  addTicketRetreat(props.ticketId).then((res)=>{
    if (res && res.status == 200){
      ElMessage({
        message: "回撤成功",
        type: "success"
      })
    }
  }).finally(()=>{
    emits('onChange', true);
    viewTicketDlgVisble.value = false;
  })
}

//所有工单信息

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

watch(() => props.dialogVisible, (newVal) => {
  viewTicketDlgVisble.value = newVal;
  Object.assign(ruleForm, props.nruleForm)
  specialUrlField.value = props.nspecialUrlField || "";
  specialUrlOptions.value = props.nspecialUrlOptions || [];
  wholeSpecialUrl.value = props.nwholeSpecialUrl || "";
  wholeSpecialUrlBak.value = props.nwholeSpecialUrlBak || "";

  if(newVal){
    getTicketsLog(props.ticketId).then((res)=>{
      if (res && res.status == 200){
        allLogList.value = res.data.results
      }
    })
  }
})

watch(() => props.assignDlgVisible, (newVal) => {
  assignTicketDlgVisible.value = newVal;
  if(newVal){
    getAllUserInfo()
  }
})

const onViewCancel = (formEl: FormInstance | null) => {
  emits('onChange', false);
  if (!formEl) return;
  viewTicketDlgVisble.value = false;
  formEl.resetFields();
}

const onAssignCancel = (formEl: FormInstance | null) => {
  emits('onChange', false);
  if (!formEl) return;
  assignTicketDlgVisible.value = false;
  formEl.resetFields();
}

const onAssignSubmit = async (formEl: FormInstance | null) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      assignTicketDlgVisible.value = false;
      assignTickets(props.ticketId, ruleForm).then(res => {
        if (res && res.status == 200) {
          ElMessage({
            message: "成功移交用户",
            type: "success"
          })
        }
      }).finally(() => {
        formEl.resetFields();
        emits('onChange', true)
      })
    } else {
      console.log('error assign!', fields)
    }
  })
}

const filterMethod = (query: string) => {
  if (query) {
    usersInfo.value = UserList.value.filter((item) => {
      return item.username.toLowerCase().includes(query.toLowerCase()) || item.fullname.toLowerCase().includes(query.toLowerCase())
    })
  } else {
    usersInfo.value = UserList.value
  }
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
