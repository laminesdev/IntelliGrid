"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Battery } from "lucide-react";
import { SimulationResponse } from "@/types";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
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
  Filler
);

interface BatteryChartProps {
  data: SimulationResponse | null;
}

export function BatteryChart({ data }: BatteryChartProps) {
  if (!data) {
    return (
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Battery className="h-5 w-5 text-[#99E135]" />
            Battery State of Charge
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[400px] flex items-center justify-center text-gray-400">
          Run a simulation to see the battery chart
        </CardContent>
      </Card>
    );
  }

  const chartData = {
    labels: data.hourly_data.map((h) => `H${h.hour}`),
    datasets: [
      {
        label: 'State of Charge',
        data: data.hourly_data.map((h) => h.battery_soc * 100),
        borderColor: '#99E135',
        backgroundColor: (context: any) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 400);
          gradient.addColorStop(0, 'rgba(153, 225, 53, 0.4)');
          gradient.addColorStop(1, 'rgba(153, 225, 53, 0.05)');
          return gradient;
        },
        borderWidth: 3,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#99E135',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
        fill: true,
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
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(10, 10, 10, 0.95)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(153, 225, 53, 0.3)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: function(context: any) {
            return `Battery SOC: ${context.parsed.y.toFixed(1)}%`;
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
        min: 0,
        max: 100,
        grid: {
          display: false,
        },
        ticks: {
          color: '#666',
          font: {
            size: 11,
          },
          callback: function(value: any) {
            return value + '%';
          },
        },
      },
    },
  };

  const minSOC = Math.min(...data.hourly_data.map(d => d.battery_soc));
  const maxSOC = Math.max(...data.hourly_data.map(d => d.battery_soc));

  return (
    <Card className="glass glass-hover transition-all duration-300">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Battery className="h-5 w-5 text-[#99E135]" />
          Battery State of Charge
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[400px] w-full">
          <Line data={chartData} options={options} />
        </div>
        <div className="mt-4 flex justify-between text-sm text-gray-400">
          <span>Min: {(minSOC * 100).toFixed(1)}%</span>
          <span>Max: {(maxSOC * 100).toFixed(1)}%</span>
        </div>
      </CardContent>
    </Card>
  );
}
