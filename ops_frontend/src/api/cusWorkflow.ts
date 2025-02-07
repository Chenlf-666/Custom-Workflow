import axios from "../axios";

export function addCusWorkflow(request: any){
    return axios.post("/custom_workflows", request)
}

export function getCusWorkflowList(pageSize?:number, pageNo?: number, name?:string, usable?:boolean){
    return axios.get("/custom_workflows", {
        params:{
            pageSize,
            pageNo,
            name,
            usable
        }
    })
}

export function cusWorkflowDetail(pk:any){
    return axios.get("/custom_workflows/" + pk)
}

export function updateCusWorkflow(pk: any, request: any){
    return axios.put("/custom_workflows/" + pk, request)
}

export function deleteCusWorkflow(pk:number){
    return axios.delete("/custom_workflows/" + pk)
}

export function getFieldList(pk:any, pageSize?:number, pageNo?: number, name?:string){
    return axios.get("/custom_workflows/" + pk + "/field", {
        params:{
            pageSize,
            pageNo,
            name
        }
    })
}

export function addWorkflowField(workflowId: any, request: any){
    return axios.post("/custom_workflows/" + workflowId + "/field", request)
}

export function fieldDetail(workflowId:any, fieldId: any){
    return axios.get("/custom_workflows/" + workflowId + "/field/" + fieldId)
}

export function updateField(workflowId: any, fieldId: any, request: any){
    return axios.put("/custom_workflows/" + workflowId + "/field/" + fieldId, request)
}

export function deleteField(workflowId: any, fielId: any){
    return axios.delete("/custom_workflows/" + workflowId + "/field/" + fielId)
}

export function getInitStatus(workflowId: any, pageSize?:number, pageNo?: number,){
    return axios.get("/custom_workflows/" + workflowId + "/init_status", {
        params:{
            pageSize,
            pageNo,
        }
    })
}

export function getWorkflowStatus(workflowId: any, pageSize?:number, pageNo?: number, name?:string){
    return axios.get("/custom_workflows/" + workflowId + "/status", {
        params:{
            pageSize,
            pageNo,
            name
        }
    })
}

export function addWorkflowStatus(workflowId: any, request: any){
    return axios.post("/custom_workflows/" + workflowId + "/status", request)
}

export function workflowStatusDetail(workflowId:any, statusId: any){
    return axios.get("/custom_workflows/" + workflowId + "/status/" + statusId)
}

export function updateWorkflowStatus(workflowId: any, statusId: any, request: any){
    return axios.put("/custom_workflows/" + workflowId + "/status/" + statusId, request)
}

export function deleteWorkflowStatus(workflowId: any, statusId: any){
    return axios.delete("/custom_workflows/" + workflowId + "/status/" + statusId)
}

export function getTransitions(workflowId: any, pageSize?:number, pageNo?: number, name?:string){
    return axios.get("/custom_workflows/" + workflowId + "/transition", {
        params:{
            pageSize,
            pageNo,
            name
        }
    })
}

export function addTransition(workflowId: any, request: any){
    return axios.post("/custom_workflows/" + workflowId + "/transition", request)
}

export function transitionDetail(workflowId:any, transitionId: any){
    return axios.get("/custom_workflows/" + workflowId + "/transition/" + transitionId)
}

export function updateTransition(workflowId: any, transitionId: any, request: any){
    return axios.put("/custom_workflows/" + workflowId + "/transition/" + transitionId, request)
}

export function deleteTransition(workflowId: any, transitionId: any){
    return axios.delete("/custom_workflows/" + workflowId + "/transition/" + transitionId)
}

export function getContentTypes(pageSize?:number, pageNo?: number){
    return axios.get("/custom_workflows/content_types", {
        params:{
            pageSize,
            pageNo,
        }
    })
}

export function getTickets(workflow?: any, pageSize?:number, pageNo?: number, name?:string, completed?:any, category?: string){
    return axios.get("/tickets", {
        params:{
            workflow,
            pageSize,
            pageNo,
            name,
            completed,
            category
        }
    })
}

export function addTickets(request: any){
    return axios.post("/tickets", request)
}

export function ticketsDetail(ticketsId: any){
    return axios.get("/tickets/" + ticketsId)
}

export function updateTickets(ticketsId: any, request: any){
    return axios.put("/tickets/" + ticketsId, request)
}

export function deleteTickets(ticketsId: any){
    return axios.delete("/tickets/" + ticketsId)
}

export function assignTickets(ticketsId: any, request: any){
    return axios.post("/tickets/" + ticketsId + "/assign", request)
}

export function getCurrentFields(id: any){
    return axios.get("/tickets/" + id + "/current_fields")
}

export function getTicketsLog(id: any, pageSize?:number, pageNo?: number,){
    return axios.get("/tickets/" + id + "/log", {
        params:{
            pageSize,
            pageNo,
        }
    })
}

export function addTicketsTransition(id: any, request: any){
    return axios.post("/tickets/" + id + "/transition", request)
}

export function getInitialTicketRelatedUrls(workflowId: any, fieldId: any){
    return axios.get("/custom_workflows/" + workflowId + "/field/" + fieldId + "/relate_url")
}

export function getEditTicketRelatedUrls(ticketId: any, fieldId: any){
    return axios.get("/tickets/" + ticketId + "/field/" + fieldId + "/relate_url")
}

export function addTicketRetreat(ticketId: any){
    return axios.post("/tickets/" + ticketId + "/retreat")
}
