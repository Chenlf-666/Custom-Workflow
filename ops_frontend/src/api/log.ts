import axios from "../axios";

export function getAuditLog(pageNo?:number, pageSize?:number, action?:any, actor?: any){
    return axios.get("/auth/auditlog", {
            params:{
                pageNo,
                pageSize,
                action,
                actor
            }
        })
}
