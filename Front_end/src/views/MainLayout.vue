<template>
  <div class="h-screen flex flex-col">
    <AppHeader />
    <div class="flex-1 overflow-hidden">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
</script>