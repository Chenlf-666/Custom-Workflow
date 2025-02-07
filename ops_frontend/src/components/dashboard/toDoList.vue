<template>
  <div class="card-container">
    <el-card shadow="hover" class="full-height-card">
    <template #header>
      <div class="clearfix">
        <span>待办事项</span>
      </div>
    </template>
    <el-table v-show="!noDataFlag"
              :show-header="false"
              :data="todoList"
              @row-click="onClickTask"
              class="table-container"
              >
      <el-table-column width="40">
        <template #default="scope">
          <el-checkbox v-model="scope.row.completed" :disabled="scope.row.completed"></el-checkbox>
        </template>
      </el-table-column>
      <el-table-column>
        <template #default="scope">
          <div class="todo-item" 
            :class="{'todo-item-del': scope.row.completed, 'clickable': !scope.row.completed}"
            :style="{ cursor: !scope.row.completed ? 'pointer' : 'default' }">
            <div v-if="scope.row.type == 1">
              你的JIRA密码即将过期，请尽快更新你的密码
            </div>
            <div v-if="scope.row.type == 2">
              新的【{{ scope.row.reference_name }}】事项待处理
            </div>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <div v-show="noDataFlag" style="text-align: center;">
      <img class="no-data-chart" :src="noData">
    </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import {ref} from 'vue';
import noData from "@/assets/img/no-data.png";
import {getMyTasks} from "@/api/dashboard";
import {useRouter} from 'vue-router';

const router = useRouter();

const noDataFlag = ref(false)
const todoList = ref([]);

const getMyTaskList = async () => {
  await getMyTasks().then(res => {
    if (res.status == 200) {
      todoList.value = res.data.results;
    }
  })
}

getMyTaskList();

const onClickTask = (row) => {
  if (row.completed) return;
  if (row.type == 1) {
    router.push("/profile")
  }
  if (row.type == 2) {
    router.push(`/worksheet_${row.order}`)
  }
}

</script>

<style scoped>
.card-container {
  display: flex;
  height: 100%;
}

.full-height-card {
  flex: 1;
}
.table-container {
  width: 100%;
  height: calc(100vh - (100vh - 220px)/2 - 450px );
}
.no-data-chart {
  display: inline;
}

.todo-item-del {
  text-decoration: line-through;
  color: #999;
}

</style>