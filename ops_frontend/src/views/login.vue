<template>
  <div class="login-container">
    <el-row class="login-main-box">

      <el-col :lg="10" :md="10" class="right bg-light-50 flex-col">
        <h2 class="title">欢迎来到运维平台</h2>
        <div class="sub-title">此网站用于公司内部运维使用</div>
        <div>
          <span class="line"></span>
          <span>帐号密码登录</span>
          <span class="line"></span>
        </div>
        <el-form ref="ruleFormRef" :rules="rules" :model="ruleForm" class="w-[300px]">
          <el-form-item prop="username">
            <el-input v-model="ruleForm.username" placeholder="请输入用户名" class="sign-box-input">
              <template #prefix>
                <img :src="user" class="sign-box-icon"/>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="ruleForm.password" type="password" placeholder="请输入密码">
              <template #prefix>
                <img :src="password" class="sign-box-icon"/>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button color="#626eef" class="w-[300px]" type="primary" :loading="loading"
                      @click="onSubmit(ruleFormRef)">登录
            </el-button>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>
    
  </div>
</template>

<script lang="ts" setup>
import {ref, reactive} from 'vue';
import {login, getUserInfo} from '@/api/user';
import {useRouter} from 'vue-router';
import {FormInstance, FormRules, ElMessage} from 'element-plus'
import jwt_decode, {JwtPayload} from 'jwt-decode';
import {useTagsStore} from "@/store/tags";
import {useUserStore} from "@/store/user";
import {User, Lock} from '@element-plus/icons-vue';
import password from '@/assets/img/password.svg';
import user from '@/assets/img/user.svg';

const userInfo = useUserStore();
// const {getUserInfo} = userInfo;

const router = useRouter();
const loading = ref(false);


const formSize = ref('default')
const ruleFormRef = ref<FormInstance>()
const ruleForm = reactive({
  username: '',
  password: '',
})

const rules = reactive<FormRules>({
  username: [
    {required: true, message: '用户名不能为空', trigger: 'blur'},
  ],
  password: [
    {required: true, message: '密码不能为空', trigger: 'blur'},
  ],
})

const onSubmit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      loading.value = true;
      login(ruleForm.username, ruleForm.password)
          .then(res => {
            if (res == undefined || res.status != 200) {
              ElMessage({
                message: "登录失败,无效的登录信息!",
                type: "error"
              })
            } else {
              ElMessage({
                message: "登录成功",
                type: "success"
              })
              localStorage.setItem("token", res.data.access);
              localStorage.setItem("refresh", res.data.refresh);
              const decoded = jwt_decode<JwtPayload>(res.data.access || '') || null;
              localStorage.setItem("expire", ((decoded.exp || 0) * 1000).toString());
              getUserInfo().then(res=>{
                if(res && res.status == 200 ){
                    userInfo.setUserInfo(res.data);
                }
                router.push("/");
              });
            }
          }).finally(() => {
        loading.value = false;
      })
    } else {
      console.log('error submit!', fields)
    }
  })
}
const tags = useTagsStore();
tags.clearTags();
</script>

<style scoped>
.sub-title {
  font-size: 12px;
  margin-top: 10px !important;
}
.login-container {
  @apply min-h-screen bg-indigo-500;
  background-color: #242f42;
  background-image: url(../../public/login-bg.png);
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
}

.login-main-box {
  width: 1000px;
  margin: 0 auto;
}


.login-container .left,
.login-container .right {
  @apply flex items-center justify-center;
}

.login-container .left {
  justify-content: flex-start;
}


.right {
  padding:  40px 0;
  margin: 0 auto;
  border-radius: 3px;
  box-shadow: 0 10px 5px rgba(0, 0, 0, 0.2);
}

.right .title {
  font-size: 30px;
}

.right > div {
  @apply flex items-center justify-center my-5 text-gray-300 space-x-2;
}

.right .line {
  @apply h-[1px] w-16 bg-gray-200;
}

.sign-box-icon {
  width: 16px;
  height: 16px;
}
</style>