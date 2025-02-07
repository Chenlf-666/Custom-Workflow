import { defineStore } from 'pinia';

// import { usePermissStore } from "@/store/permiss";

interface ObjectList {
	[key: string]: string[];
}

interface UserInfo {
    id: number
    username: string
    fullname: string
    email: string
    is_superuser: boolean
    is_staff: boolean
    is_active: boolean
    mobile: string
    last_login: string
    role: string
    pwd_expire_date: number
}

export const useUserStore = defineStore('user', {
    state: () => {
        return {
            user: <UserInfo>{},
            // key: <string[]>[],
			defaultList: <ObjectList>{
				super: ['super', 'admin', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16' ],
				admin: ['admin', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'],
				user: ['1', '2', '3', '4', '5', '6', '7', '8']
			}
        }
    },
    getters:{
        key(state){
            if (state.user.is_superuser){
                return state.defaultList['super'];
            }else if(state.user.is_staff){
                return state.defaultList['admin'];
            }else{
                return state.defaultList['user'];
            }
        }
    },
    actions: {
        setUserInfo(val: UserInfo){
            this.user = val;
        },
        clearUserInfo(){
            this.user = <UserInfo>{};
        }
    },
    persist: {
        enabled: true,
        strategies: [
            {
                key: 'user',
                storage: localStorage,
            },
        ]
    }
});

