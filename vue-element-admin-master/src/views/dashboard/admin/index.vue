<template>
  <div class="dashboard-editor-container">
    <github-corner class="github-corner" />

    <panel-group @handleSetLineChartData="handleSetLineChartData" />

    <el-row style="background:#fff;padding:16px 16px 0;margin-bottom:32px;">
      <line-chart :chart-data="chartData" />
    </el-row>
    <h1>{{ chartData }}</h1>
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
import PanelGroup from './components/PanelGroup'
import LineChart from './components/LineChart'
import RaddarChart from './components/RaddarChart'
import PieChart from './components/PieChart'
import BarChart from './components/BarChart'

const lineChartData = {
  newVisitis: {
    expectedData: [],
    timeStamps: []
  }
  // 其他数据...
}

export default {
  name: 'DashboardAdmin',
  components: {
    PanelGroup,
    LineChart,
    RaddarChart,
    PieChart,
    BarChart
  },
  data() {
    return {
      lineChartData: lineChartData.newVisitis
    }
  },
  computed: {
    chartData() {
      return {
        xAxis: {
          data: this.lineChartData.timeStamps.map(timestamp => timestamp), // 使用原始时间戳数据
          boundaryGap: false,
          axisTick: {
            show: false
          }
        },
        series: [
          {
            name: 'Expected Data',
            type: 'line',
            data: this.lineChartData.expectedData
          }
        ]
      }
    }
  },
  created() {
    this.setupWebSocket()
  },
  methods: {
    handleSetLineChartData(type) {
      this.lineChartData = this.lineChartData[type]
    },
    setupWebSocket() {
      const socket = new WebSocket('ws://127.0.0.1:8000/api/monitoring/ws')
      socket.onmessage = (event) => {
        const [timestamp, newData] = event.data.split(',')
        const parsedTimestamp = timestamp // 存储原始时间戳字符串
        const parsedNewData = parseInt(newData)

        this.lineChartData.timeStamps.push(parsedTimestamp)
        this.lineChartData.expectedData.push(parsedNewData)

        // 可以考虑保持数组长度，例如只保留最近的 N 个数据
        if (this.lineChartData.timeStamps.length > 10) {
          this.lineChartData.timeStamps.shift()
          this.lineChartData.expectedData.shift()
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-editor-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;

  .github-corner {
    position: absolute;
    top: 0px;
    border: 0;
    right: 0;
  }

  .chart-wrapper {
    background: #fff;
    padding: 16px 16px 0;
    margin-bottom: 32px;
  }
}

@media (max-width: 1024px) {
  .chart-wrapper {
    padding: 8px;
  }
}
</style>
