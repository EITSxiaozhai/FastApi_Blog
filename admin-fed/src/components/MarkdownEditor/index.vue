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
import { mermaidPlugin, renderMermaidPreview } from './mermaid-plugin'

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
      editor: null,
      mermaidTimer: null
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
        ...this.editorOptions,
        plugins: [uml, chart, mermaidPlugin]
      })
      if (this.value) {
        this.editor.setMarkdown(this.value)
      }
      this.editor.on('change', () => {
        this.$emit('input', this.editor.getMarkdown())
        this.scheduleMermaidRender()
      })
      this.editor.on('load', this.scheduleMermaidRender)
      this.editor.on('afterPreviewRender', this.scheduleMermaidRender)
      this.uploadImg()
      this.scheduleMermaidRender()
    },
    destroyEditor() {
      if (this.mermaidTimer) {
        clearTimeout(this.mermaidTimer)
        this.mermaidTimer = null
      }
      if (!this.editor) return
      this.editor.off('change')
      this.editor.off('load')
      this.editor.off('afterPreviewRender')
      this.editor.destroy()
    },
    scheduleMermaidRender() {
      if (this.mermaidTimer) {
        clearTimeout(this.mermaidTimer)
      }
      this.mermaidTimer = setTimeout(() => {
        this.renderMermaidPreview()
      }, 120)
    },
    renderMermaidPreview() {
      const root = this.$el || document.getElementById(this.id)
      if (!root) return
      renderMermaidPreview(root)
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

<style>
.toastui-editor-contents .toastui-mermaid,
.toastui-editor-contents .mermaid {
  margin: 16px 0;
  text-align: center;
  overflow-x: auto;
}

.toastui-editor-contents .toastui-mermaid svg,
.toastui-editor-contents .mermaid svg {
  max-width: 100%;
  height: auto;
}

.toastui-editor-contents .mermaid-source {
  display: none !important;
}

.toastui-editor-contents .mermaid-error,
.toastui-editor-contents .mermaid-error pre {
  color: #f56c6c;
  background: #fef0f0;
  text-align: left;
  white-space: pre-wrap;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
}
</style>
