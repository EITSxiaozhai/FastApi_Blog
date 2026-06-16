import 'dotenv/config'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const SITE_URL = normalizeBaseUrl(process.env.BLOG_SITE_URL || 'https://blog.exploit-db.xyz')
const API_BASE_URL = normalizeBaseUrl(process.env.BLOG_API_BASE_URL || 'https://blogapi-traefik.exploit-db.xyz/api')
const PAGE_SIZE = Number(process.env.SITEMAP_PAGE_SIZE || 20)
const API_SECRET_HEADER_NAME = process.env.SITEMAP_API_SECRET_HEADER_NAME
const API_SECRET_HEADER_VALUE = process.env.SITEMAP_API_SECRET_HEADER_VALUE

const staticPages = [
  { path: '/', changefreq: 'daily', priority: '1.0' },
  { path: '/about-me', changefreq: 'monthly', priority: '0.7' },
  { path: '/api/bing-wallpaper', changefreq: 'weekly', priority: '0.5' }
]

const outputDir = path.resolve('public')

function normalizeBaseUrl(url) {
  return url.replace(/\/+$/, '')
}

function escapeXml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;')
}

function formatLastmod(value) {
  if (!value) return new Date().toISOString().slice(0, 10)
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value).slice(0, 10) : date.toISOString().slice(0, 10)
}

async function fetchJson(url) {
  const headers = {
    accept: 'application/json',
  }

  if (API_SECRET_HEADER_NAME && API_SECRET_HEADER_VALUE) {
    headers[API_SECRET_HEADER_NAME] = API_SECRET_HEADER_VALUE
  }

  const response = await fetch(url, {
    headers
  })

  if (!response.ok) {
    throw new Error(`GET ${url} failed with ${response.status}`)
  }

  return response.json()
}

async function fetchAllPosts() {
  const posts = []
  let currentPage = 1
  let totalPages = 1

  do {
    const url = `${API_BASE_URL}/views/blog/BlogIndex?page=${currentPage}&pageSize=${PAGE_SIZE}&initialLoad=true`
    const result = await fetchJson(url)
    const pagePosts = Array.isArray(result.data) ? result.data : []
    posts.push(...pagePosts)

    totalPages = Number(result.total_pages || 1)
    currentPage += 1
  } while (currentPage <= totalPages)

  return posts
}

function buildSitemapXml(posts) {
  const urls = [
    ...staticPages.map((page) => ({
      loc: `${SITE_URL}${page.path}`,
      lastmod: new Date().toISOString().slice(0, 10),
      changefreq: page.changefreq,
      priority: page.priority
    })),
    ...posts
      .filter((post) => post.BlogId)
      .map((post) => ({
        loc: `${SITE_URL}/blog/${post.BlogId}`,
        lastmod: formatLastmod(post.updated_at || post.created_at),
        changefreq: 'weekly',
        priority: '0.8'
      }))
  ]

  const urlEntries = urls.map((url) => `  <url>
    <loc>${escapeXml(url.loc)}</loc>
    <lastmod>${escapeXml(url.lastmod)}</lastmod>
    <changefreq>${url.changefreq}</changefreq>
    <priority>${url.priority}</priority>
  </url>`).join('\n')

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlEntries}
</urlset>
`
}

async function main() {
  let posts = []

  try {
    posts = await fetchAllPosts()
    console.log(`Generated sitemap with ${posts.length} blog posts.`)
  } catch (error) {
    console.warn(`Could not fetch blog posts for sitemap: ${error.message}`)
    console.warn('Continuing with static pages only so the build can finish.')
  }

  await mkdir(outputDir, { recursive: true })
  await writeFile(path.join(outputDir, 'sitemap.xml'), buildSitemapXml(posts), 'utf8')
  await writeFile(path.join(outputDir, 'robots.txt'), `User-agent: *
Allow: /

Sitemap: ${SITE_URL}/sitemap.xml
`, 'utf8')
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
