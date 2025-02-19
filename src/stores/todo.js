import { defineStore } from "pinia";
import { ref } from "vue";

export const useTodoStore  = defineStore('todo',()=>{
    let todos = localStorage.getItem('todos')
    if(todos === null){
        todos = []
    }else{
        todos = JSON.parse(todos)
    }

    //未完成的工作數量
    const activeTodos = todos.filter(todo=>!todo.completed)  
    //qty 屬性會回傳未完成的工作數量
    const qty = ref(activeTodos.length)

    //qtyChange() 方法，修改 qty 屬性
    const qtyChange = count => {
        qty.value = count
    }

    return {qty, qtyChange}

})