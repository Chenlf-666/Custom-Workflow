<template>
    <el-row :gutter="5">
        <el-col :span="14">
            <el-row :gutter="10" class="mgb5">
                <el-col :span="8">
                    <el-card shadow="hover" :body-style="{ padding: '0px' }">
                        <div class="grid-content grid-con-1">
                            <el-icon class="grid-con-icon">
                                <User/>
                            </el-icon>
                            <div class="grid-cont-right">
                                <div class="grid-num">{{ todayLoginCount }}</div>
                                <div>用户访问量</div>
                            </div>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </el-col>
        <el-col :span="10">
            <div style="padding: 5px 0; height: calc(100vh - (100vh - 220px)/2 - 324px )">
                <to-do-list></to-do-list>
            </div>
        </el-col>
    </el-row>
</template>

<script setup lang="ts">
import {ref, onMounted} from "vue";
import {getTodayLoginCount} from '../api/dashboard';
import {useUserStore} from "@/store/user";
import {storeToRefs} from "pinia";
import avatar from '@/assets/img/img.jpg';
import ToDoList from "@/components/dashboard/toDoList.vue";


const userStore = useUserStore();
const {user} = storeToRefs(userStore);
const todayLoginCount = ref(0)


const getTodayLogin = () => {
    getTodayLoginCount().then(res => {
        if (res.status == 200) {
            todayLoginCount.value = res.data.count;
        }
    })
}

onMounted(() => {
    getTodayLogin();
})

</script>

<style scoped>

.filter > span {
    line-height: 32px;
    font-size: 14px;
}

.grid-content {
    display: flex;
    align-items: center;
    height: 100px;
}

.grid-cont-right {
    flex: 1;
    text-align: center;
    font-size: 14px;
    color: #999;
}

.grid-num {
    font-size: 30px;
    font-weight: bold;
}

.grid-con-icon {
    font-size: 50px;
    width: 100px;
    height: 100px;
    text-align: center;
    line-height: 100px;
    color: #fff;
}

.grid-con-1 .grid-con-icon {
    background: rgb(45, 140, 240);
}

.grid-con-1 .grid-num {
    color: rgb(45, 140, 240);
}

.grid-con-2 .grid-con-icon {
    background: rgb(100, 213, 114);
}

.grid-con-2 .grid-num {
    color: rgb(100, 213, 114);
}

.grid-con-3 .grid-con-icon {
    background: rgb(242, 94, 67);
}

.grid-con-3 .grid-num {
    color: rgb(242, 94, 67);
}

.mgb5 {
    margin-bottom: 5px;
}

.user-info-list {
    font-size: 14px;
    color: #999;
    line-height: 25px;
    width: 300%
}

.user-info-list span {
    margin-left: 70px;
}

</style>