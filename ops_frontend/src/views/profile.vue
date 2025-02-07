<template>
  <div>
    <el-row>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <el-row>
              <el-col :span="3" class="centered">
                <el-avatar :size="70" :src="avatarImg"/>
              </el-col>
              <el-col :span="8" class="flex items-center">
                <div>
                  <div style="font-size: 16px; color: #000;">{{ user.fullname }}</div>
                  <div style="font-size: 8px; color: #878787;">{{ user.role }}</div>
                </div>
              </el-col>
              <el-divider direction="vertical" style="height: 80px;"/>
              <el-col :span="8" class="items-center">
                <div style="font-size: 14px; color: #878787;">邮箱</div>
                <div style="font-size: 12px; color: #000;"> {{ user.email }}</div>
                <div style="font-size: 14px; color: #878787;">上次登录</div>
                <div style="font-size: 12px; color: #000;">{{ moment(user.last_login).format("YYYY-MM-DD HH:mm:ss") }}
                </div>
              </el-col>
              <el-col :span="4" class="centered">
                <el-tooltip content="编辑" placement="bottom" effect="light">
                  <el-button circle color="#318800" style="font-size: 20px; width: 50px; height: 50px"
                             :icon="Edit"></el-button>
                </el-tooltip>
              </el-col>
            </el-row>
          </template>

          <el-row>
            <el-col :span="24">
              <div class="bg-gray-100 text-sm flex items-center h-8 px-2 py-5">帐号安全</div>
            </el-col>
          </el-row>

          <el-row class="flex items-center h-15 px-5">
            <el-col :span="4" class="px-3">邮 箱</el-col>
            <el-divider direction="vertical" style="height: 40px;"/>
            <el-col :span="12" class="px-3">
              <a :href="'mailto:' + user.email" class="text-blue-500">{{ user.email }}</a>
            </el-col>
            <el-divider direction="vertical" style="height: 40px;"/>
            <el-col :span="6" class="justify-center">
            </el-col>
          </el-row>
          <el-divider/>
          <el-row class="flex items-center h-15 px-5">
            <el-col :span="4" class="px-3">密码</el-col>
            <el-divider direction="vertical" style="height: 40px;"/>
            <el-col :span="12" class="px-3">用于保护账号信息和登录安全</el-col>
            <el-divider direction="vertical" style="height: 40px;"/>
            <el-col :span="6" class="flex justify-center">
              <el-button color="#318800" @click="changePassword">修改</el-button>
            </el-col>
          </el-row>
          <el-divider/>
          <el-row class="flex items-center h-15 px-5">
            <el-col :span="4" class="px-3">电话</el-col>
            <el-divider direction="vertical" style="height: 40px;"/>
            <el-col :span="12" class="px-3">{{ user.mobile }}</el-col>
            <el-divider direction="vertical" style="height: 40px;"/>
            <el-col :span="6" class="flex justify-center">
              <el-button color="#318800">修改</el-button>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    <el-dialog
        v-model="dialogVisible"
        title='修改密码'
        :show-close=false
        :close-on-click-modal=false
        width="30%">
      <el-form ref="ruleFormRef" :rules="rules" :model="ruleForm" label-width="120px">
        <el-form-item label="用户名" prop="username">
          <el-input disabled v-model="ruleForm.fullname"/>
        </el-form-item>
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="ruleForm.old_password" type="password" show-password/>
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="ruleForm.new_password" type="password" show-password/>
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="ruleForm.confirmPassword" type="password" show-password/>
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

<script setup lang="ts" name="user">
import {reactive, ref, computed} from 'vue';
import {storeToRefs} from "pinia";
import 'cropperjs/dist/cropper.css';
import avatar from '@/assets/img/img.jpg';
import {useUserStore} from "@/store/user";
import { ElMessage, FormRules, FormInstance } from 'element-plus';
import moment from "moment/moment";
import {Edit, EditPen} from "@element-plus/icons-vue";
import {changeSelfPassword} from "../api/user"

const userStore = useUserStore();
const {user} = storeToRefs(userStore);

const ruleForm = reactive({
  fullname: '',
  old_password: '',
  new_password: '',
  confirmPassword: '',
});

const avatarImg = ref(avatar);
const dialogVisible = ref(false);
const ruleFormRef = ref(null)

const changePassword = () => {
  dialogVisible.value = true;
  ruleForm.fullname = user.value.fullname;
};

const rules = reactive<FormRules>({
  old_password: [
    {required: true, message: '旧密码不能为空', trigger: 'blur'},
  ],
  new_password: [
    {required: true, message: '新密码不能为空', trigger: 'blur'},
    {min: 8, message: '新密码少于8个字符', trigger: 'blur'}
  ],
  confirmPassword: [
    {required: true, message: '确认密码不能为空', trigger: 'blur'},
    {
      validator: (rule, value, callback) => {
        if (value !== ruleForm.new_password) {
          callback(new Error('密码不匹配'));
        } else {
          callback();
        }
      }
    },
  ],
})

const onCancel = (formEl: FormInstance | null) => {
  if (!formEl) return;
  dialogVisible.value = false;
  formEl.resetFields();
};

const onSubmit = async (formEl: FormInstance | null) => {
  dialogVisible.value = false;
  if (!formEl) {
    console.log("return...")
    return
  }
  await formEl.validate((valid, fields) => {
    if (valid) {
      changeSelfPassword(ruleForm.old_password, ruleForm.new_password)
          .then(res => {
            if (res == undefined || res.status != 200) {
              ElMessage({
                message: "无效密码!",
                type: "error"
              })
            } else {
              ElMessage({
                message: "修改密码成功",
                type: "success"
              })
            }
          })
    }
  })
};

</script>

<style scoped>

.info-edit i {
  color: #eee;
  font-size: 25px;
}

.info-image:hover .info-edit {
  opacity: 1;
}


.centered {
  display: flex;
  justify-content: center;
  align-items: center;
}

.centered-wrap {
  display: flex;
  height: 100%;
  align-items: center;
  flex-wrap: wrap-reverse;
}

.el-avatar:hover::before {
  content: "";
  /*background-image: url('/src/assets/img/upload.png');*/
  background-color: white;
  background-size: cover;
  position: absolute;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  opacity: 0.5;
}
</style>
