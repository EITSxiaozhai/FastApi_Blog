export { data }

async function data(pageContext) {
  if (import.meta.env?.DEV) {
    console.log('服务器端数据获取开始...')
  }
  
  // 模拟从API获取数据
  try {
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟API数据
    const mockData = {
      userId: 1,
      id: 1,
      title: 'Vike-Vue SSR 数据获取测试',
      body: '这是从服务器端获取的数据，在页面渲染之前就已经准备好了。这证明了SSR数据获取正在正常工作。',
      fetchTime: new Date().toLocaleString(),
      isSSR: typeof window === 'undefined'
    }
    
    if (import.meta.env?.DEV) {
      console.log('服务器端数据获取完成:', mockData)
    }
    
    return {
      // 这些数据会被传递到页面组件
      props: {
        data: mockData
      }
    }
  } catch (error) {
    if (import.meta.env?.DEV) {
      console.error('数据获取失败:', error)
    }
    
    return {
      props: {
        data: {
          error: '数据获取失败',
          fetchTime: new Date().toLocaleString()
        }
      }
    }
  }
} 