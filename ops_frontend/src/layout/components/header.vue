<template>
  <div class="header">
    <div class="header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item class="routeName">{{state.routeName?.name}}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="header-right">
      <div class="header-user-con">
        <!-- 用户头像 -->
        <el-avatar class="user-avator" :size="30" :src="imgurl" />
        <!-- 用户名下拉菜单 -->
        <el-dropdown class="user-name" trigger="click" @command="handleCommand">
          <span class="el-dropdown-link">
            {{ user.fullname }}
            <el-icon class="el-icon--right">
              <arrow-down />
            </el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, watch, reactive, toRefs, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from "@/store/user";

import { useRouter, useRoute } from 'vue-router';
import imgurl from '../../assets/img/default-user-header.png';
import { breadcrumbs } from "@/contants";
import lodash from 'lodash';

const userStore = useUserStore();
const { user } = storeToRefs(userStore);
const message: number = 2;
interface obj {
  name: string,
  url: string
}
let state: any = reactive({
  routeName: {
    name: '网站首页',
    url: '/'
  }
})

// 用户名下拉菜单选择事件
const router = useRouter();
const handleCommand = (command: string) => {
  if (command == 'logout') {
    localStorage.clear();
    userStore.clearUserInfo();
    router.push('/login');
  } else if (command == 'profile') {
    router.push('/profile');
  }
};
const route = useRoute();
const onRoutes = computed(() => {
  return route.path;
});
watch([onRoutes], (value, oldValue) => {
  state.routeName = lodash.find(breadcrumbs, item => lodash.isEqual(item.url, value[0]));
}, {immediate: true})

</script>

<style scoped>
.routeName {
  font-size: 18px;
  font-weight: 700;
}
.header {
  position: relative;
  box-sizing: border-box;
  width: 100%;
  height: 60px;
  font-size: 22px;
  color: blue;
  background-color: white;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}

.collapse-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  float: left;
  padding: 0 21px;
  cursor: pointer;
}

.header .logo {
  width: 250px;
  line-height: 70px;
}

.header-right {
}

.header-user-con {
  display: flex;
  height: 60px;
  align-items: center;
}

.btn-fullscreen {
  transform: rotate(45deg);
  margin-right: 5px;
  font-size: 24px;
}

.btn-bell,
.btn-fullscreen {
  position: relative;
  width: 30px;
  height: 30px;
  text-align: center;
  border-radius: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-bell-badge {
  position: absolute;
  right: 4px;
  top: 0px;
  width: 8px;
  height: 8px;
  border-radius: 4px;
  background: #f56c6c;
  color: #fff;
}

.btn-bell .el-icon-lx-notice {
  color: #242424;
}

.user-name {
  margin-left: 10px;
}

.user-avator {
  margin-left: 20px;
}

.el-dropdown-link {
  color: #242424;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.el-dropdown-menu__item {
  text-align: center;
}

.el-breadcrumb {
  line-height: 60px;
}
</style>
