import axios from "@/axios";

export function getTodayLoginCount(){
    return axios.get("/dashboard/daily-login")
}

export function getMyTasks(){
    return axios.get("/dashboard/mytasks")
}
