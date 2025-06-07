import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import React from 'react';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export interface RewardsBarChartProps {
  data: { [month: number]: number };
}

export function RewardsBarChart({ data }: RewardsBarChartProps) {
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];
  const values = months.map((_, i) => data[i + 1] || 0);
  return (
    <Bar
      data={{
        labels: months,
        datasets: [
          {
            label: 'Staking Rewards (EUR)',
            data: values,
            backgroundColor: '#6366f1',
            borderRadius: 6,
          },
        ],
      }}
      options={{
        responsive: true,
        plugins: {
          legend: { display: false },
          title: { display: false },
        },
        scales: {
          x: {
            grid: { color: '#312e81' },
            ticks: { color: '#a5b4fc' },
          },
          y: {
            grid: { color: '#312e81' },
            ticks: { color: '#a5b4fc' },
          },
        },
      }}
    />
  );
}
