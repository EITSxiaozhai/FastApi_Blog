import mermaidLib from 'mermaid/dist/mermaid.min.js'

const mermaid = mermaidLib && mermaidLib.initialize ? mermaidLib : (mermaidLib && mermaidLib.default) || mermaidLib

mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  theme: 'default',
  fontFamily: 'inherit',
  flowchart: {
    htmlLabels: false,
    useMaxWidth: true
  }
})

function encodeSource(source) {
  return encodeURIComponent(source || '')
}

function decodeSource(encoded) {
  try {
    return decodeURIComponent(encoded || '')
  } catch (e) {
    return encoded || ''
  }
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function uniqueId() {
  return 'toast-mermaid-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8)
}

function isMermaidLang(info) {
  return String(info || '').trim().split(/\s+/)[0].toLowerCase() === 'mermaid'
}

function createMermaidTokens(source) {
  return [
    {
      type: 'openTag',
      tagName: 'div',
      outerNewLine: true,
      classNames: ['toastui-mermaid'],
      attributes: {
        'data-mermaid': encodeSource(source || '')
      }
    },
    {
      type: 'html',
      content: '<textarea hidden class="mermaid-source">' + escapeHtml(source || '') + '</textarea><div class="mermaid-placeholder">Mermaid 渲染中...</div>'
    },
    { type: 'closeTag', tagName: 'div', outerNewLine: true }
  ]
}

function applySvg(element, svg) {
  element.innerHTML = svg
  element.setAttribute('data-processed', 'true')
}

function applyError(element, error, source) {
  const message = (error && (error.str || error.message)) || 'Mermaid 渲染失败'
  element.setAttribute('data-processed', 'true')
  element.classList.add('mermaid-error')
  element.innerHTML = '<pre>' + escapeHtml(message) + '\n' + escapeHtml(source) + '</pre>'
}

function wrapMermaidCodeBlocks(root) {
  const blocks = root.querySelectorAll(
    'pre code.language-mermaid, pre.lang-mermaid code, pre code[data-language="mermaid"]'
  )
  Array.prototype.forEach.call(blocks, function(code) {
    const pre = code.closest ? code.closest('pre') : code.parentElement
    if (!pre || (pre.parentElement && pre.parentElement.classList.contains('toastui-mermaid'))) {
      return
    }
    const source = (code.textContent || '').trim()
    const wrapper = document.createElement('div')
    wrapper.className = 'toastui-mermaid'
    wrapper.setAttribute('data-mermaid', encodeSource(source))
    const textarea = document.createElement('textarea')
    textarea.hidden = true
    textarea.className = 'mermaid-source'
    textarea.value = source
    wrapper.appendChild(textarea)
    const placeholder = document.createElement('div')
    placeholder.className = 'mermaid-placeholder'
    placeholder.textContent = 'Mermaid 渲染中...'
    wrapper.appendChild(placeholder)
    pre.parentNode.replaceChild(wrapper, pre)
  })
}

function renderOne(element) {
  const encoded = element.getAttribute('data-mermaid')
  const textarea = element.querySelector('.mermaid-source')
  const source = (encoded ? decodeSource(encoded) : (textarea && textarea.value) || '').trim()
  if (!source) {
    element.setAttribute('data-processed', 'true')
    return
  }

  const id = uniqueId()
  try {
    const result = mermaid.render(id, source, function(svgCode) {
      applySvg(element, svgCode)
    })
    if (result && typeof result.then === 'function') {
      result.then(function(output) {
        const svg = typeof output === 'string' ? output : (output && output.svg)
        if (svg) {
          applySvg(element, svg)
        }
      }).catch(function(error) {
        applyError(element, error, source)
      })
    } else if (typeof result === 'string') {
      applySvg(element, result)
    }
  } catch (error) {
    applyError(element, error, source)
  }
}

/**
 * Toast UI plugin:
 * - $$mermaid custom blocks
 * - ```mermaid fenced code blocks (standard Mermaid / GitHub syntax)
 */
export function mermaidPlugin() {
  return {
    toHTMLRenderers: {
      mermaid: function(node) {
        return createMermaidTokens(node.literal)
      },
      codeBlock: function(node, context) {
        if (isMermaidLang(node.info)) {
          return createMermaidTokens(node.literal)
        }
        return context.origin()
      }
    }
  }
}

export function renderMermaidPreview(root) {
  if (!root) return

  wrapMermaidCodeBlocks(root)

  const nodes = root.querySelectorAll('.toastui-mermaid:not([data-processed])')
  Array.prototype.forEach.call(nodes, renderOne)
}
