<script setup lang="ts">
import Menubar from 'primevue/menubar'
// import {type MenuItem} from 'primevue'
import Button from 'primevue/button'
import { ref, type Ref } from "vue";
const items = ref([
    {
        label: 'Convert',
        route: "/convert"
    },
    {
        label: 'About',
        route: "/about"
    }
])
</script>
<template>
    <Menubar :model="items">
        <template #start>
            <router-link to="/" class="no-underline flex">
                <img src="/img/bird.svg" style="height:4rem" id="kurrawong-bird" />
                <img src="/img/wordmark.svg" style="height:4rem" id="kurrawong-wordmark" />
                <h1 class="text-3xl me-3 text-black" style="line-height:4rem;">VocExcel</h1>
            </router-link>
        </template>
        <template #item="{ item, props, root, }">
            <router-link :to="item.route!" class="mx-2">{{ item.label }}</router-link>
        </template>
        <template #end>
            <a href="https://github.com/Kurrawong/VocExcel" target="_blank" rel="noopener noreferrer"
                class="p-button p-button-outlined font-bold">
                <span class="pi pi-github me-1"></span> Github</a>
        </template>
    </Menubar>
</template>

<style>
@media (max-width: 500px) {
    #kurrawong-wordmark {
        display: none;
    }
}
</style>