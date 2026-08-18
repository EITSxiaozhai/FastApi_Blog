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

/**
 * Toast UI Editor plugin: map ```mermaid fenced blocks to preview HTML.
 */
export function mermaidPlugin() {
  return {
    toHTMLRenderers: {
      mermaid(node) {
        const source = node.literal || ''
        return [
          {
            type: 'openTag',
            tagName: 'div',
            outerNewLine: true,
            classNames: ['toastui-mermaid'],
            attributes: {
              'data-mermaid': encodeSource(source)
            }
          },
          {
            type: 'html',
            content: '<textarea hidden class="mermaid-source">' + escapeHtml(source) + '</textarea><div class="mermaid-placeholder">Mermaid 流程图</div>'
          },
          { type: 'closeTag', tagName: 'div', outerNewLine: true }
        ]
      }
    }
  }
}

export function renderMermaidPreview(root) {
  if (!root) return

  const nodes = root.querySelectorAll('.toastui-mermaid:not([data-processed])')
  Array.prototype.forEach.call(nodes, function(element) {
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
  })
}
