<template>
  <div :id="id" />
</template>

<script>
import 'codemirror/lib/codemirror.css' // codemirror
import '@toast-ui/editor/dist/toastui-editor.css'

import Editor from '@toast-ui/editor'
import defaultOptions from './default-options'
import { uploadImg } from '@/api/admin/upload'

import uml from '@toast-ui/editor-plugin-uml'
import chart from '@toast-ui/editor-plugin-chart'

export default {
  name: 'MarkdownEditor',
  props: {
    value: {
      type: String,
      default: ''
    },
    id: {
      type: String,
      required: false,
      default() {
        return 'markdown-editor-' + +new Date() + ((Math.random() * 1000).toFixed(0) + '')
      }
    },
    options: {
      type: Object,
      default() {
        return defaultOptions
      }
    },
    mode: {
      type: String,
      default: 'markdown'
    },
    height: {
      type: String,
      required: false,
      default: '75vh'
    },
    language: {
      type: String,
      required: false,
      default: 'en_US' // https://github.com/nhnent/tui.editor/tree/master/src/js/langs
    }
  },
  data() {
    return {
      editor: null
    }
  },
  computed: {
    editorOptions() {
      const options = Object.assign({}, defaultOptions, this.options)
      options.initialEditType = this.mode
      options.height = this.height
      options.language = this.language
      return options
    }
  },
  watch: {
    value(newValue, preValue) {
      if (newValue !== preValue && newValue !== this.editor.getMarkdown()) {
        this.editor.setMarkdown(newValue)
      }
    },
    language(val) {
      this.destroyEditor()
      this.initEditor()
    },
    height(newValue) {
      this.editor.height(newValue)
    },
    mode(newValue) {
      this.editor.changeMode(newValue)
    }
  },
  mounted() {
    this.initEditor()
  },
  destroyed() {
    this.destroyEditor()
  },
  methods: {
    initEditor() {
      this.editor = new Editor({
        el: document.getElementById(this.id),
        plugins: [uml, chart],
        ...this.editorOptions
      })
      if (this.value) {
        this.editor.setMarkdown(this.value)
      }
      this.editor.on('change', () => {
        this.$emit('input', this.editor.getMarkdown())
      })
      this.uploadImg()
    },
    destroyEditor() {
      if (!this.editor) return
      this.editor.off('change')
      this.editor.destroy()
    },
    setValue(value) {
      this.editor.setMarkdown(value)
    },
    getValue() {
      return this.editor.getMarkdown()
    },
    setHtml(value) {
      this.editor.setHtml(value)
    },
    getHtml() {
      return this.editor.getHTML()
    },
    uploadImg() {
      this.editor.removeHook('addImageBlobHook')
      this.editor.on('addImageBlobHook', (_file, cb) => {
        const file = new FormData()
        file.append('file', _file)
        const result = uploadImg(file)
        result.then(({ code, msg, url }) => {
          if (code === 20000) {
            this.$message.success(msg)
            cb(url, file.name)
          }
        })
      })
    }
  }
}
</script>
