<script setup lang="ts">
import Button from 'primevue/button'
</script>

<template>
  <main>
    <h1>VocExcel</h1>

    <p>Another Excel-to-RDF converter for SKOS vocabs, but one that:</p>
    <ul>
      <li>uses fixed templates to keep it simple</li>
      <li>
        meets particular SKOS profile outcomes such as
        <a target="_blank" href="https://w3id.org/profile/vocpub">VocPub</a>
      </li>
      <li>is under active development, production use, and is commercially supported</li>
    </ul>
    <router-link to="/convert" class="p-button no-underline text-white">
      Start here
    </router-link>
  </main>
</template>
