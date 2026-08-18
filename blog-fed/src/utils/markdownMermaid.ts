export function applyMermaidFence(md: any) {
  const defaultFence = md.renderer.rules.fence

  md.renderer.rules.fence = (tokens, idx, options, env, slf) => {
    const token = tokens[idx]
    const info = token.info ? String(token.info).trim().split(/\s+/)[0] : ''
    if (info === 'mermaid') {
      const code = md.utils.escapeHtml(token.content.trim())
      return `<div class="mermaid-diagram"><div class="mermaid">${code}</div></div>\n`
    }
    if (defaultFence) {
      return defaultFence(tokens, idx, options, env, slf)
    }
    return slf.renderToken(tokens, idx, options)
  }

  return md
}
