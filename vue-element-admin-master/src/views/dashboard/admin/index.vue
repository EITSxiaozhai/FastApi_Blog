<template>
  <div class="dashboard-editor-container">
    <github-corner class="github-corner" />

    <panel-group @handleSetLineChartData="handleSetLineChartData" />

    <el-row style="background:#fff;padding:16px 16px 0;margin-bottom:32px;">
      <line-chart :chart-data="lineChartData" />
    </el-row>
    <h1>{{ lineChartData }}</h1>
    <el-row :gutter="32">
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <raddar-chart />
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <pie-chart />
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <bar-chart />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>

import LineChart from './components/LineChart'

const lineChartData = {
  newVisitis: {
    expectedData: [],
    actualData: [] // 添加 actualData 数组
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

        this.lineChartData.actualData.push(parsedTimestamp)
        this.lineChartData.expectedData.push(parsedNewData)

        // 可以考虑保持数组长度，例如只保留最近的 N 个数据
        if (this.lineChartData.expectedData.length > 10) {
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
