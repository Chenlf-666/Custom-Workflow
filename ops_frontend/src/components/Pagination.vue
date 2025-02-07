<template>
  <el-pagination
    :current-page="currentPage"
    :page-size="pageSize"
    :total="total"
    :page-sizes="[20, 50, 100, 200]"
    small
    layout="total, sizes, prev, pager, next"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  ></el-pagination>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

interface PaginationProps {
  currentPage: number;
  pageSize: number;
  total: number;
}

interface PaginationEmits  {
  (event: 'onPageChange', currentPage: number, pageSize: number): void;
}

const props = defineProps<PaginationProps>();
const emits = defineEmits<PaginationEmits>();

const currentPageRef = ref(props.currentPage);
const pageSizeRef = ref(props.pageSize);

watch(()=> props.currentPage, (newVal) => {
  currentPageRef.value = newVal;
});

watch(currentPageRef, (newVal) => {
  emits('onPageChange', newVal, pageSizeRef.value);
});

watch(pageSizeRef, (newVal) => {
  emits('onPageChange', currentPageRef.value, newVal);
});

const handleSizeChange = (size: number) => {
  pageSizeRef.value = size;
  currentPageRef.value = 1;
};

const handleCurrentChange = (page: number) => {
  currentPageRef.value = page;
};

</script>
