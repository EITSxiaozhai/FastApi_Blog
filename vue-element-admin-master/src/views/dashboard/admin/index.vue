<template>
  <div class="dashboard-editor-container">

    <el-row style="background:#fff;padding:16px 16px 0;margin-bottom:32px;">
      <h1>基于websocket的实时图形监控</h1>
      <line-chart :chart-data="lineChartData" :expected-legend="'CPU 利用率'" :actual-legend="'内存利用率'" />
    </el-row>
  </div>
</template>

<script>

import LineChart from './components/LineChart'

const lineChartData = {
  newVisitis: {
    expectedData: [],
    actualData: [],
    timestampData: []
  }
  // 其他数据...
}

export default {
  name: 'DashboardAdmin',
  components: {
    LineChart
  },
  data() {
    return {
      lineChartData: lineChartData.newVisitis
    }
  },
  computed: {},
  created() {
    this.setupWebSocket()
  },
  methods: {
    // 动态刷新添加信息到图标
    handleSetLineChartData(type) {
      this.lineChartData = this.lineChartData[type]
    },
    setupWebSocket() {
      const socket = new WebSocket('ws://127.0.0.1:8000/api/monitoring/ws')
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        const parsedTimestamp = data.cpu_info
        const parsedNewData = parseInt(data.memory_percent)
        const timestampString = data.current_time

        this.lineChartData.timestampData.push(timestampString)
        this.lineChartData.actualData.push(parsedTimestamp)
        this.lineChartData.expectedData.push(parsedNewData)
        // 可以考虑保持数组长度，例如只保留最近的 N 个数据
        if (this.lineChartData.expectedData.length > 10) {
          this.lineChartData.timestampData.shift()
          this.lineChartData.actualData.shift()
          this.lineChartData.expectedData.shift()
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
