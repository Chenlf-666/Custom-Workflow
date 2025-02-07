import {useUserStore} from '@/store/user'
import {nextTick} from "vue";

export const permissionDirective = {
    mounted(el, binding) {
        const permission = useUserStore();
        if (!permission.key.includes(String(binding.value))) {
            if(el.tagName === 'BUTTON'){
                el.disabled = true;
                el.classList.add('is-disabled');
            }else{
               // el.hidden = true;
                el.parentNode && el.parentNode.removeChild(el);
            //  el.style.display = 'none';
            }
        }
    }
}
