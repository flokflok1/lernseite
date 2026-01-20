<template>
  <div class="line-chart">
    <Line :data="chartData" :options="chartOptions" :height="height" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// ============================================================================
// Props
// ============================================================================

interface Dataset {
  label: string
  data: number[]
  color?: string
  fill?: boolean
}

interface Props {
  labels: string[]
  datasets: Dataset[]
  height?: number
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: 300
})

// ============================================================================
// Computed
// ============================================================================

const chartData = computed(() => {
  return {
    labels: props.labels,
    datasets: props.datasets.map((dataset, index) => ({
      label: dataset.label,
      data: dataset.data,
      borderColor: dataset.color || getDefaultColor(index),
      backgroundColor: dataset.fill
        ? `${dataset.color || getDefaultColor(index)}33`
        : 'transparent',
      fill: dataset.fill || false,
      tension: 0.4,
      borderWidth: 2,
      pointRadius: 3,
      pointHoverRadius: 5
    }))
  }
})

const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: props.datasets.length > 1,
        position: 'top' as const
      },
      title: {
        display: !!props.title,
        text: props.title || ''
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false
        }
      },
      y: {
        display: true,
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      }
    }
  }
})

// ============================================================================
// Methods
// ============================================================================

const getDefaultColor = (index: number): string => {
  const colors = [
    '#3B82F6', // blue
    '#10B981', // green
    '#F59E0B', // yellow
    '#EF4444', // red
    '#8B5CF6', // purple
    '#EC4899'  // pink
  ]
  return colors[index % colors.length]
}
</script>
