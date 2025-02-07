import { ElMessage } from 'element-plus'

export function toast(message:string, type:any, dangerouslyUseHTMLString = false) {
    ElMessage({
        showClose: true,
        message,
        type,
        dangerouslyUseHTMLString,
        duration: 5000
    })
}