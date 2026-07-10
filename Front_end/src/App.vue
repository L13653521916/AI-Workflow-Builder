<template>
  <router-view v-slot="{ Component, route }">
    <transition :name="transitionName(route)" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>
</template>

<script setup lang="ts">
import type { RouteLocationNormalizedLoaded } from 'vue-router'

function transitionName(route: RouteLocationNormalizedLoaded) {
  if (route.path === '/login' || route.path === '/register') {
    return 'fade'
  }
  return 'slide-fade'
}
</script>

<style>
#app {
  width: 100%;
  height: 100%;
}

html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Poppins', 'Segoe UI', system-ui, -apple-system, sans-serif;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.22s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.18s ease-in;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
