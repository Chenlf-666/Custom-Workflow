<template>
	<div class="container">
		<div class="handle-box">
      <el-input
				v-model="queryStr"
        clearable
        placeholder="权限组名称"
        class="handle-input mr10"
        @keyup.enter.native="handleSearch"
        @clear="onClear">
			</el-input>
      <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      <el-button type="primary" :icon="Plus" @click="addPermission" v-permission="'admin'">添加权限组</el-button>
    </div>

		<el-table 
			:data="tableData" 
			border 
			stripe 
			table-layout='auto' 
			ref="multipleTable"         
			header-cell-class-name="table-header"
		>
      <el-table-column prop="name" label="权限组名称" sortable></el-table-column>
      <el-table-column prop="desc" label="描述"></el-table-column>
			<el-table-column label="用户名称" width="150px">
        <template #default="scope">
          <div v-if="scope.row.users.length">
            <el-popover effect="light" trigger="hover" width="50%">
              <template #default>
                <div>
                  <span v-for="(item, index) in scope.row.users" :key="item.id" style="display: inline-block; margin-right: 5px;">
                    {{ item.fullname }}<span v-if="(index + 1) % 2 === 0"> </span> <!-- 每两个用户后添加空格 -->
                  </span>
                </div>
              </template>
              <template #reference>
                <el-tag>{{ scope.row.users[0].fullname }}...</el-tag>
              </template>
            </el-popover>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" :formatter="dateFormat" label="创建时间" sortable></el-table-column>
      <el-table-column prop="update_time" :formatter="dateFormat" label="更新时间" sortable></el-table-column>
      <el-table-column label="操作" width="220px" align="center">
        <template #default="scope">
          <el-button text type="primary" :icon="Edit" @click="handleEdit(scope.row)" v-permission="'super'" >
            编辑
          </el-button>
          <el-button text type="danger" :icon="Delete" @click="handleDelete(scope.$index, scope.row)"
                     v-permission="'super'">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination">
      <Pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        @onPageChange="handleSizeChange"
      />
    </div>
		
		<el-dialog
      v-model="dlgVisible"
      :title="isCreate ? '添加权限组' : '编辑权限组'"	
      :show-close=false
      :close-on-click-modal=false
      :destroy-on-close="true"
      width="50%"
			@closed="onCancel(ruleFormRef)"
		>
      <el-form ref="ruleFormRef" :rules="rules" :model="ruleForm" label-width="120px">
        <el-form-item label="组名称" prop="name">
          <el-input v-model="ruleForm.name"/>
        </el-form-item>
        <el-form-item label="描述" prop="desc">
          <el-input v-model="ruleForm.desc"/>
        </el-form-item>
				<el-form-item label="用户" prop="user_ids">
					<el-select v-model="ruleForm.user_ids" filterable multiple :reserve-keyword="true" clearable :filter-method="filterMethod" placeholder="请选择需要添加的用户">
						<el-option v-for="item in usersInfo" :label="item.fullname" :key="item.id" :value="item.id"  />
					</el-select>
				</el-form-item>
				<el-form-item label="用户组权限" prop="menu_permissions">
					<div class="tree-wrapper">
						<el-tree
							ref="tree"
							:data="data"
							node-key="id"
							:show-checkbox=true
							:default-expand-all=false
							@check="handleCheck"
							:default-checked-keys="checkedKeys"
						/>
					</div>
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

<script setup lang="ts" name="permission">
import { ref, reactive } from 'vue';
import { ElTree, FormRules, FormInstance, ElMessage, ElMessageBox } from 'element-plus';
import { useUserStore } from '../store/user';
import { getMenuTree, getAllUsers, createGroup, getAllGroups, getGroupDetail, updateGroup, deleteGroup } from '../api/user';
import { Delete, Edit, Search, Plus } from '@element-plus/icons-vue';
import {dateFormat} from '@/utils/dateFormat'

const role = ref<string>('admin');
const dlgVisible = ref(false);
const isCreate = ref(false);
const userList = ref<any[]>([]);
const usersInfo = ref<any[]>([]);
const ruleFormRef = ref(null);
const queryStr = ref("");

interface Tree {
	id: string;
	label: string;
	children?: Tree[];
}

interface TableItem {
}

const tableData = ref<TableItem[]>([]);
const data = ref(<any>[])
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const parentTreeId = ref<any[]>([]) //记录含有子组件的父组件的id

const ruleForm = reactive({
  name: '',
  desc: '',
  user_ids: <number[]>[],
  menu_permissions: <any[]>[],
});

// 获取表格数据
const getGroupsList = (pageSize: number, currentPage: number, name?: string) => {
  getAllGroups(pageSize, currentPage, name).then(res => {
    tableData.value = res.data.results;
    total.value = res.data.count;
  });
};

getGroupsList(pageSize.value, currentPage.value);


const getAllUserInfo = () => {
  getAllUsers().then((res) => {
    userList.value = res.data.results;
    usersInfo.value = userList.value;
  })
}

getAllUserInfo()

const getMenus = () => {
  getMenuTree().then(res => {
    data.value = res.data.results;
    res.data.results.forEach((item)=>{
      if (item.label == "审批流程" || item.label == "测试管理" || item.label == "管理中心" || item.label == "系统配置"){
        parentTreeId.value.push(item.id)
      }
    })
  }).finally(()=>{
    data.value[0]["disabled"] = true;
  })
};

getMenus();

const permission = useUserStore();

const checkedKeys = ref<any>([1]);

// 保存权限
const tree = ref<InstanceType<typeof ElTree>>();

const handleChange = (val: string[]) => {
	tree.value!.setCheckedKeys(permission.defaultList[role.value]);
};

const addPermission = () => {
	isCreate.value = true
	dlgVisible.value = true
  ruleForm.name = '';
	ruleForm.user_ids = [];
	ruleForm.desc = '';
	ruleForm.menu_permissions = [1];
  checkedKeys.value = [1];
	if (tree.value) {
    tree.value.setCheckedKeys([]); // Reset checked keys in the tree
  }
}

const handleCheck = (checkedKeys: string[], info: any) => {
	ruleForm.menu_permissions = tree.value!.getCheckedKeys().concat(tree.value!.getHalfCheckedKeys());
};

const rules = reactive<FormRules>({
	name: [
		{ required: true, message: '名称不能为空', trigger: 'blur' },
	],
	menu_permissions: [
		{ required: true, message: '至少选择一个菜单权限', trigger: 'change' },
	]
})

let idx: number = -1;
const handleEdit = (row: any) => {
  idx = row.id;
	checkedKeys.value = [];
	ruleForm.menu_permissions = [];
  ruleForm.user_ids = [];
  getGroupDetail(idx).then(res => {
    ruleForm.name = res.data.name;
    ruleForm.desc = res.data.desc;
		res.data.authed_menus.forEach((item: any) => {
      checkedKeys.value.push(item.id);
			ruleForm.menu_permissions.push(item.id)
    })

    checkedKeys.value = checkedKeys.value.filter(key => !parentTreeId.value.includes(key)); //删除具有subs的父节点id，若前端含有父节点id，会默认选中父节点下的所有子节点数据

		if (tree.value) {
      tree.value.setCheckedKeys(checkedKeys.value);
    }
		res.data.users.forEach((item: any) => {
      ruleForm.user_ids.push(item.id);
    })
  }).finally(()=>{
    dlgVisible.value = true;
    isCreate.value = false;
  })
}

const onCancel = (formEl: FormInstance | null) => {
	idx = -1;
  if (!formEl) return;
	ruleForm.name = '';
	ruleForm.user_ids = [];
	ruleForm.menu_permissions = [1];
  checkedKeys.value = [1];
	ruleForm.desc = '';
  dlgVisible.value = false;
	isCreate.value = false;
  formEl.resetFields();
};


let finalSearch = ''
const handleSearch = () => {
  currentPage.value = 1;
  finalSearch = queryStr.value;
  getGroupsList(pageSize.value, currentPage.value, queryStr.value);
}

// 分页导航
const handleSizeChange = (page: number, size: number) => {
  currentPage.value = page;
  pageSize.value = size;
	if (queryStr.value != "") {
    queryStr.value = finalSearch;
		getGroupsList(pageSize.value, currentPage.value, queryStr.value);
	} else {
		getGroupsList(pageSize.value, currentPage.value);
	}
}

const onClear = () => {
  finalSearch = '';
  getGroupsList(pageSize.value, currentPage.value);
}

const handleDelete = (index: number, row: any) => {
  // 二次确认删除
  ElMessageBox.confirm(
      `确定要删除权限组 ${row.name} 吗？`,
      '警告',
      {type: 'warning'}
  )
      .then(() => {
        deleteGroup(row.id).then(res => {
          if (res.status == 204) {
            tableData.value.splice(index, 1);
            total.value -= 1;
						ElMessage({
							message: "成功删除权限组",
							type: "success"
						})
          }
        })
      })
};

const onSubmit = async (formEl: FormInstance | null) => {
	if (!formEl) return
	await formEl.validate((valid, fields) => {
		if (valid) {
			if (idx == -1){
				createGroup(ruleForm).then(res => {
					if (res && res.status == 201) {
						ElMessage({
								message: "成功创建权限组",
								type: "success"
							})

						formEl.resetFields();
					}
				}).finally(()=>{
					getGroupsList(pageSize.value, currentPage.value);
					dlgVisible.value = false;
					isCreate.value = false;
				})
			}else{
				updateGroup(idx, ruleForm).then(res => {
				if (res && res.status == 200){
					ElMessage({
								message: "成功编辑权限组",
								type: "success"
							})
						getGroupsList(pageSize.value, currentPage.value);
						formEl.resetFields();
					}
				}).finally(()=>{
					dlgVisible.value = false;
          formEl.resetFields();
				})
			}
		} else {
			console.log('error submit!', fields)
		}
	})
}

const filterMethod = (query: string) => {
  if (query) {
    usersInfo.value = userList.value.filter((item) => {
      return item.username.toLowerCase().includes(query.toLowerCase()) || item.fullname.toLowerCase().includes(query.toLowerCase())
    })
  } else {
    usersInfo.value = userList.value
  }
}

</script>

<style scoped>

.handle-input {
  width: 300px;
}

.handle-box {
  margin-bottom: 20px;
}

.mr10 {
  margin-right: 10px;
}

.tree-wrapper{
	border: 1px solid #d3e0ea;
	margin-bottom: 20px;
	width: 100%;
}

.label {
	font-size: 14px;
}

</style>
