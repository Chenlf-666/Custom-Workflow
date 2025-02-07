import axios from "../axios";

export function login(username:string, password:string){
    return axios.post("/auth/login", {
        username,
        password
    })
}

export function getUserInfo(){
    return axios.get("/auth/profile")
}

export function getMenuList(){
    return axios.get("/menu/tree")
}


export function getAllUsers(pageSize?:number, pageNo?:number, search?:string){
    if ( search ){
        return axios.get("/auth/users", {
            params:{
                pageSize,
                pageNo,
                search
            }
        })
    }
    return axios.get("/auth/users", {
            params:{
                pageSize,
                pageNo
            }
        })
}

export function getUserDetail(pk:number){
    return axios.get("/auth/users/" + pk)
}


export function changeSelfPassword(old_password:string, new_password:string){
    return axios.post("/auth/change-password", {
        old_password,
        new_password
    })
}

export function resetUserPassword(username:string, new_password:string){
    return axios.post("/auth/reset-user-password", {
        username,
        new_password
    })
}

export function getMenuTree(){
    return axios.get("/menu/tree")
}

export function createGroup(request: any){
    return axios.post("/auth/groups", request)
}

export function updateGroup(groupId: number, request: any){
    return axios.put("/auth/groups/" + groupId, request)
}

export function deleteGroup(groupId: number){
    return axios.delete("/auth/groups/" + groupId)
}

export function getAllGroups(pageSize?:number, pageNo?: number, name?:string){
    if ( name ){
        return axios.get("/auth/groups", {
            params:{
                pageSize,
                pageNo,
                name
            }
        })
    }
    return axios.get("/auth/groups", {
            params:{
                pageSize,
                pageNo
            }
        })
}

export function getGroupDetail(groupId: number){
    return axios.get("/auth/groups/" + groupId)
}
