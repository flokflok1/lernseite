<template>
  <div class="bar-chart">
    <Bar :data="chartData" :options="chartOptions" :height="height" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

// ============================================================================
// Props
// ============================================================================

interface Dataset {
  label: string
  data: number[]
  color?: string
}

interface Props {
  labels: string[]
  datasets: Dataset[]
  height?: number
  title?: string
  horizontal?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: 300,
  horizontal: false
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
      backgroundColor: dataset.color || getDefaultColor(index),
      borderRadius: 4
    }))
  }
})

const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: props.horizontal ? ('y' as const) : ('x' as const),
    plugins: {
      legend: {
        display: props.datasets.length > 1,
        position: 'top' as const
      },
      title: {
        display: !!props.title,
        text: props.title || ''
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: !props.horizontal
        }
      },
      y: {
        display: true,
        beginAtZero: true,
        grid: {
          display: props.horizontal,
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
