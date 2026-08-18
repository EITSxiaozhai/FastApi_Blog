let mermaidModule: Promise<typeof import('mermaid')> | null = null

function isBrowser() {
  return typeof window !== 'undefined' && typeof document !== 'undefined'
}

async function getMermaid() {
  if (!isBrowser()) return null
  if (!mermaidModule) {
    mermaidModule = import('mermaid').then((mod) => {
      const mermaid = mod.default
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        theme: 'neutral',
        fontFamily: 'inherit',
        flowchart: {
          htmlLabels: false,
          useMaxWidth: true
        }
      })
      return mod
    })
  }
  return mermaidModule
}

function uniqueId() {
  return `mermaid-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}

function convertLegacyMermaidCodeBlocks(root: ParentNode) {
  const blocks = root.querySelectorAll('pre code.language-mermaid, pre code.lang-mermaid')
  blocks.forEach((code) => {
    const pre = code.parentElement
    if (!pre) return
    const wrapper = document.createElement('div')
    wrapper.className = 'mermaid-diagram'
    const diagram = document.createElement('div')
    diagram.className = 'mermaid'
    diagram.textContent = code.textContent || ''
    wrapper.appendChild(diagram)
    pre.replaceWith(wrapper)
  })
}

export async function renderMermaidDiagrams(root?: ParentNode | null) {
  if (!isBrowser()) return

  const scope = root || document
  convertLegacyMermaidCodeBlocks(scope)

  const mermaidImport = await getMermaid()
  if (!mermaidImport) return
  const mermaid = mermaidImport.default

  const nodes = Array.from(scope.querySelectorAll<HTMLElement>('.mermaid:not([data-processed])'))
  for (const node of nodes) {
    const source = (node.textContent || '').trim()
    if (!source) {
      node.setAttribute('data-processed', 'true')
      continue
    }

    const id = uniqueId()
    try {
      const { svg, bindFunctions } = await mermaid.render(id, source)
      node.innerHTML = svg
      node.setAttribute('data-processed', 'true')
      bindFunctions?.(node)
    } catch (error: any) {
      node.setAttribute('data-processed', 'true')
      node.classList.add('mermaid-error')
      node.textContent = error?.message || error?.str || 'Mermaid 渲染失败'
    }
  }
}
