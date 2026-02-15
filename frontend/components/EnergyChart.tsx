"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sun } from "lucide-react";
import { SimulationResponse } from "@/types";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

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
);

interface EnergyChartProps {
  data: SimulationResponse | null;
}

export function EnergyChart({ data }: EnergyChartProps) {
  if (!data) {
    return (
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Sun className="h-5 w-5 text-[#99E135]" />
            Energy Production vs Consumption
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[400px] flex items-center justify-center text-gray-400">
          Run a simulation to see the energy chart
        </CardContent>
      </Card>
    );
  }

  const chartData = {
    labels: data.hourly_data.map((h) => `H${h.hour}`),
    datasets: [
      {
        label: 'Solar Production',
        data: data.hourly_data.map((h) => h.solar_production),
        borderColor: '#99E135',
        backgroundColor: 'rgba(153, 225, 53, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#99E135',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
        fill: false,
      },
      {
        label: 'Consumption',
        data: data.hourly_data.map((h) => h.consumption),
        borderColor: '#ffffff',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 2,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#99E135',
        pointHoverBorderWidth: 2,
        fill: false,
      },
      {
        label: 'Net Energy',
        data: data.hourly_data.map((h) => h.net_energy),
        borderColor: '#666666',
        borderWidth: 2,
        borderDash: [5, 5],
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#666',
        fill: false,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#fff',
          font: {
            size: 12,
          },
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
      tooltip: {
        backgroundColor: 'rgba(10, 10, 10, 0.95)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(153, 225, 53, 0.3)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} kWh`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#666',
          font: {
            size: 11,
          },
        },
      },
      y: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#666',
          font: {
            size: 11,
          },
          callback: function(value: any) {
            return value + ' kWh';
          },
        },
      },
    },
  };

  return (
    <Card className="glass glass-hover transition-all duration-300">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Sun className="h-5 w-5 text-[#99E135]" />
          Energy Production vs Consumption
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[400px] w-full">
          <Line data={chartData} options={options} />
        </div>
      </CardContent>
    </Card>
  );
}
