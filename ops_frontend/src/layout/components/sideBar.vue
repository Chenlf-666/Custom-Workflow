<template>
  <el-row class="tac">
    <el-col :span="24">
      <div class="logo-container">
        <el-image class="logo-image" :src="imgUrl"/>
        <span :class="['logoText', !isCollapse ? 'logoTextShow' : 'logoTextHide']">Workflow</span>
      </div>
      <el-menu
          :default-active="onRoutes"
          :collapse="isCollapse"
          :collapse-transition="true"
          active-text-color="#ffd04b"
          background-color="#242f42"
          class="el-menu-vertical-demo"
          text-color="#fff"
          unique-opened
          router
      >
        <template v-for="item in currentSideBar">
          <template v-if="item.subs">
            <el-sub-menu :index="item.index" :key="item.index">
              <template #title>
                <el-icon>
                  <component :is="item.icon"></component>
                </el-icon>
                <span>{{ item.title }}</span>
              </template>
              <template v-for="subItem in item.subs">
                <el-menu-item :index="subItem.index" class="subtitle-span">
                  {{ subItem.title }}
                </el-menu-item>
              </template>
            </el-sub-menu>
          </template>
          <template v-else>
            <el-menu-item :index="item.index" :key="item.index" class="title-span">
              <el-icon>
                <component :is="item.icon"></component>
              </el-icon>
              <template #title>{{ item.title }}</template>
            </el-menu-item>
          </template>
        </template>
      </el-menu>
      <div class="icon-menu" @click="() => (isCollapse = !isCollapse)">
        <el-icon>
          <Expand v-if="isCollapse"/>
          <Fold v-else/>
        </el-icon>
      </div>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import {computed, ref, onBeforeMount} from 'vue';
import {useRoute} from "vue-router";
import imgUrl from '@/assets/img/logo.png';
import { sideBarList } from '@/contants';
import { getUserInfo } from '@/api/user';


const isCollapse = ref(false)

const route = useRoute()
const onRoutes = computed(() => {
  return route.path
})

const currentSideBar = ref(<any>[])
let indexList = <any>[]
let dynamicSiderBar = <any>[]
let currentWorksheetIndex = 1

const getCurrentSideBar = (indexList, sideBarList, dynamicSiderBar) => {
    const filteredSideBar = <any>[]
    const filterSideBar = (sidebar) => {
      sidebar.forEach((item) => {
        if (indexList.includes(item.index) || (item.subs && item.subs.some((subItem) => indexList.includes(subItem.index)))) {
          const newItem = { ...item }
          if (item.subs && item.title != "审批流程") {
            const filteredSubs = item.subs.filter((subItem) => indexList.includes(subItem.index))
            newItem.subs = filteredSubs
          }else if (item.subs && item.title == "审批流程"){
            let filteredSubs = item.subs.filter((subItem) => indexList.includes(subItem.index))
            filteredSubs = [...filteredSubs, ...dynamicSiderBar]
            newItem.subs = filteredSubs
          }
          filteredSideBar.push(newItem)
        }else{
          if(item.title == "审批流程"){
            if (dynamicSiderBar.length > 0){
              const dynamicSubs = {icon: 'Tickets', index: '3', title: '审批流程', permission: '1', subs: [...dynamicSiderBar]}
              filteredSideBar.push(dynamicSubs)
            }
          }
        }
      })
    }
    filterSideBar(sideBarList)
    return filteredSideBar
}

onBeforeMount(()=>{
	getUserInfo().then((res=>{
    indexList = []
    dynamicSiderBar = []
    currentWorksheetIndex = 1
    res.data.authed_menus.forEach((item)=>{
      if(item.children && item.children.length){
        item.children.forEach((citem, cindex)=>{
          indexList.push(citem.index)
          if (/\d/.test(citem.index)){
            dynamicSiderBar.push({"index": "/worksheet_" + currentWorksheetIndex, "title": citem.label, "permission": 1})
            currentWorksheetIndex += 1
          }
        })
      }else{
        indexList.push(item.index)
      }
    })
    currentSideBar.value = getCurrentSideBar(indexList, sideBarList, dynamicSiderBar)
  }))
})


</script>

<style lang="less" scoped>
.el-menu-item div {
  padding: 0 18px !important;
}
.logo-image {
  margin-left: 10px; 
  margin-right: 10px; 
  width: 36px; 
  height: 36px
}
.logoText {
  transition: 0.2s all ease;
}
.logoTextShow {
  display: block;
}
.logoTextHide {
  display: none;
}
.icon-menu {
  font-size: 22px; 
  color: white;
  margin-left: 18px; 
  margin-top: 10px;
  cursor: pointer;
}
.tac {
  height: 100%;
}
.el-row {
  background-color: #242f42;
}

.el-menu-vertical-demo {
  max-height: calc(100vh - 70px);
  border-right: none !important;
  overflow-x: hidden;
  overflow-y: auto;
  &::-webkit-scrollbar {
    width: 4px;
    background: rgba(255,255,255,0.2);
  }
  &::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.6);
    border-radius: 10px;
  }
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  height: calc(100vh - 108px);
}

.el-menu--collapse {
  width: 60px;
  height: calc(100vh - 108px);
  background: #242f42;
}
.logo-container {
  display: flex;
  align-items: center;
  color: white; 
  height: 60px; 
  cursor: pointer; 
  box-sizing: border-box;
  padding-left: 2px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}
.subtitle-span {
  padding-left: 49px !important;
  border-right: 2px solid transparent;
  box-sizing: border-box;
  color: rgba(255,255,255,0.7);
}
.title-span {
  border-right: 2px solid transparent;
  box-sizing: border-box;
}
.title-span.is-active {
  border-color: var(--el-color-primary);
  color: rgba(255,255,255,1);
  background: rgba(64, 158, 255, 0.2);
}
.title-span.is-active .el-icon {
  color: var(--el-color-primary);
}
.subtitle-span.is-active {
  border-color: var(--el-color-primary);
  color: rgba(255,255,255,1);
  background: rgba(64, 158, 255, 0.2);
}
</style>
