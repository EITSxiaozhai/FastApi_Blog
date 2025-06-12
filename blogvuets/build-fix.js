const fs = require('fs')
const path = require('path')

console.log('🔧 开始修复构建后的依赖导入问题...')

// 需要修复的文件列表
const filesToFix = [
  'dist/assets/_Page.js',
  'dist/assets/_Page2.js', 
  'dist/assets/server.js'
]

// 修复函数
function fixImports(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️ 文件不存在: ${filePath}`)
    return
  }

  let content = fs.readFileSync(filePath, 'utf8')
  let modified = false

  // 移除裸导入语句
  const bareImports = [
    'import "axios";',
    'import "vue-router";', 
    'import "vuex";'
  ]

  bareImports.forEach(importStatement => {
    if (content.includes(importStatement)) {
      console.log(`🔧 修复 ${filePath} 中的: ${importStatement}`)
      content = content.replace(new RegExp(importStatement.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), '')
      modified = true
    }
  })

  // 如果文件被修改，写回文件
  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8')
    console.log(`✅ 已修复: ${filePath}`)
  } else {
    console.log(`✓ 无需修复: ${filePath}`)
  }
}

// 执行修复
filesToFix.forEach(fixImports)

console.log('🎉 构建修复完成！') 