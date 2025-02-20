<script setup >
import { ref } from 'vue'
const ordering = ref("travel_id")
const emit = defineEmits(["sortChange"])
const changeHandler = () => {
    emit("sortChange", ordering.value)
}
</script>

<template>

    <select class="form-select" @change="changeHandler" v-model="ordering">
        <option value="travel_id">景點編號升冪</option>
        <option value="-travel_id">景點編號降冪</option>
        <option value="region">縣市排序</option>
        <option value="-class1">分類編號</option>
    </select>


</template>

<style lang="css" scoped></style>