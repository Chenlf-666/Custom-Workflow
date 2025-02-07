<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="auto" height="100%">
        <Aside />
      </el-aside>
      <el-container>
        <el-header style="padding: 0px">
          <Header />
        </el-header>
        <el-main>
          <div>
            <div class="content">
              <router-view v-slot="{ Component }" :key="$route.fullPath">
                <transition name="move" mode="out-in">
                  <keep-alive :include="tags.nameList">
                    <component :is="Component"></component>
                  </keep-alive>
                </transition>
              </router-view>
            </div>
          </div>
        </el-main>
<!--        <el-footer style="padding: 0px">-->
<!--          <Footer />-->
<!--        </el-footer>-->
      </el-container>
    </el-container>
  </div>
</template>
<script setup lang="ts">
import { useTagsStore } from '@/store/tags';
import Header from '@/layout/components/header.vue'
import Aside from '@/layout/components/sideBar.vue'
import Footer from '@/layout/components/footer.vue'
import vTags from '@/layout/components/tags.vue';
const tags = useTagsStore();
</script>


<style scoped>
.layout-container-demo .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
}

.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
  background: var(--el-color-primary-light-8);
}

.layout-container-demo .el-menu {
  border-right: none;
}

.layout-container-demo .el-main {
  padding: 0;
}

.layout-container-demo .toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  right: 20px;
}
.el-container {
  height: 100%;
}
.common-layout {
  height: 100%;
}
</style>