<script setup lang="ts">
import { ref, onMounted } from 'vue'
import FileUpload from 'primevue/fileupload'
import { type FileUploadUploadEvent, type FileUploadErrorEvent } from 'primevue/fileupload'
import Accordion from 'primevue/accordion'
import Message from 'primevue/message'
import AccordionTab from 'primevue/accordiontab'
import Button from 'primevue/button'
import SplitButton from 'primevue/splitbutton';
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

import VocabTree from '@/components/VocabTree.vue'

const toast = useToast()
const rdfTurtle = ref('')
const serverError = ref(false)
const copyButtonTextDefault = 'Copy result'
const copyButtonTextCopied = 'Copied!'
const ONE_SECOND_IN_MS = 1000
const copyButtonText = ref(copyButtonTextDefault)
const previewWidth = ref(0)
const version = ref('...')
const templateVersion = "0.6.2"
const templateLink = ref(`https://github.com/Kurrawong/VocExcel/raw/main/templates/VocExcel-template-${templateVersion.replace(/\./g, '')}.xlsx`)
onMounted(() => {
  fetch('/api/v1/version')
    .then(resp => resp.text())
    .then(v => {
      version.value = v
    })
    .then(v => {
      serverError.value = version.value === '' ?? true
    })
    .catch(() => {
      serverError.value = true
    })
})

const onUploadComplete = (event: FileUploadUploadEvent) => {
  rdfTurtle.value = event.xhr.response
}

const onError = (event: FileUploadErrorEvent) => {
  const errorMsg = JSON.parse(event.xhr.response).detail
  console.error(errorMsg)
  toast.add({
    severity: 'error',
    summary: 'Error',
    detail: errorMsg
  })
}

const handleCopyRdfTurtle = () => {
  navigator.clipboard.writeText(rdfTurtle.value).then(
    () => {
      copyButtonText.value = copyButtonTextCopied
      setTimeout(() => {
        copyButtonText.value = copyButtonTextDefault
      }, ONE_SECOND_IN_MS)
    },
    () => {
      const errorMsg = 'Error copying result to clipboard'
      console.error(errorMsg)
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: errorMsg,
        life: 5000
      })
    }
  )
}
const handleDownloadRdfTurtle = () => {
  const blob = new Blob([rdfTurtle.value], { type: 'text/ttl' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  const name = rdfTurtle.value.split("\n")[0].match(/\<(.)*\>/g)[0]
    .replace("<", '')
    .replace('>', '')
    .replace(/(http|https):\/\//g, '')
    .replace(/\//g, '_')
  link.download = `${name}.ttl`
  link.click()
  URL.revokeObjectURL(link.href)
}
const handleDownloadRdfTemplate = () => {
  const link = document.createElement('a')
  link.href = templateLink.value
  link.download = `VocExcel-template-${templateVersion.replace(/\./g, '')}.xlsx`
  console.log(templateLink.value)
  link.click()
}
const items = [
  {
    label: "All versions",
    href: "https://github.com/Kurrawong/VocExcel/tree/main/templates"
  }
]
</script>

<template>
  <main>
      <SplitButton class="float-right" :label="`Get Template ${templateVersion}`" :model="items" icon="pi pi-download" outlined
        @click="handleDownloadRdfTemplate">
        <template #item="{ item }">
          <a target="_blank" rel="nofollow" :href="item.href">{{ item.label }}</a>
        </template>
      </SplitButton>
    <h1>Convert</h1>
    <Message v-if="serverError" severity="error" :closable="false">Error: could not contact server</Message>
    <p>VocExcel version {{ version?version:'unknown' }}</p>
    <p>This page allows for the conversion of supported VocExcel files to a SKOS vocabulary in turtle                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  (.ttl) format.</p>
    <p>The currently supported VocExcel template file is {{ templateVersion }}. Download the vocexcel template file by
      clicking the button above.
    </p>
    <p>Select a VocExcel file and upload it to convert it to a SKOS vocabulary.</p>
    
    <template v-if="!serverError">
      <Toast />
      <div v-if="rdfTurtle" class="flex justify-between">
        <Button  label="Reset form" @click="rdfTurtle = ''" />
        <Button  class="p-button" icon="pi pi-download" label="Download Vocab (ttl)" @click="handleDownloadRdfTurtle"/>
      </div>
      <FileUpload v-if="!rdfTurtle" name="upload_file" url="/api/v1/convert" :multiple="false" :auto="true" accept=".xlsx"
        :maxFileSize="100000000" :preview-width="previewWidth" :showUploadButton="false" :showCancelButton="false"
        @upload="onUploadComplete" @error="onError" :fileLimit="1">
        <template #empty>
          <p>Drag and drop files to here to upload.</p>
        </template>
      </FileUpload>

      <div v-else>
        <VocabTree :rdf-turtle="rdfTurtle" />

        <Accordion class="mt-4">
          <AccordionTab header="Total RDF Turtle result">
            <div class="flex flex-row-reverse gap-4">
              <Button  icon="pi pi-copy" :label="copyButtonText" @click="handleCopyRdfTurtle"/>
              <Button  icon="pi pi-download" label="Download Vocab (ttl)" @click="handleDownloadRdfTurtle"/>
            </div>

            <pre>{{ rdfTurtle }}</pre>
          </AccordionTab>
        </Accordion>
      </div>
    </template>
  </main>
  </template>
