<script setup lang="ts">
import { RouterView } from 'vue-router'
import MainNav from './components/MainNav.vue';
</script>

<template>
<MainNav/>
  <div class="md:container mx-auto prose p-4">
    <RouterView />
  </div>
</template>
