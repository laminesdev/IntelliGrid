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
  Legend,
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
  Legend
);

interface BatteryComparisonChartProps {
  ruleData: SimulationResponse;
  milpData: SimulationResponse;
}

export function BatteryComparisonChart({ ruleData, milpData }: BatteryComparisonChartProps) {
  const chartData = {
    labels: ruleData.hourly_data.map((h) => `H${h.hour}`),
    datasets: [
      {
        label: 'Rule-Based (Greedy)',
        data: ruleData.hourly_data.map((h) => h.battery_soc * 100),
        borderColor: '#99E135',
        backgroundColor: 'rgba(153, 225, 53, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#99E135',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
        fill: false,
      },
      {
        label: 'MILP Optimization',
        data: milpData.hourly_data.map((h) => h.battery_soc * 100),
        borderColor: '#4169E1',
        backgroundColor: 'rgba(65, 105, 225, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#4169E1',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
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
            size: 13,
            weight: 'bold',
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
            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
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
        title: {
          display: true,
          text: 'Hour of Day',
          color: '#999',
          font: {
            size: 12,
          },
        },
      },
      y: {
        min: 0,
        max: 100,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
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
        title: {
          display: true,
          text: 'Battery State of Charge (%)',
          color: '#999',
          font: {
            size: 12,
          },
        },
      },
    },
    annotation: {
      annotations: {
        peakHours: {
          type: 'box',
          xMin: 18,
          xMax: 22,
          backgroundColor: 'rgba(255, 99, 71, 0.1)',
          borderColor: 'rgba(255, 99, 71, 0.3)',
          borderWidth: 1,
          label: {
            content: 'Peak Hours',
            enabled: true,
            position: 'start',
            color: 'rgba(255, 99, 71, 0.8)',
          },
        },
      },
    },
  };

  return (
    <Card className="glass">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Battery className="h-5 w-5 text-[#99E135]" />
          Battery Strategy Comparison
        </CardTitle>
        <p className="text-sm text-gray-400">
          Compare how Rule-Based vs MILP optimization manages battery charge levels throughout the day
        </p>
      </CardHeader>
      <CardContent>
        <div className="h-[400px] w-full">
          <Line data={chartData} options={options} />
        </div>
        
        {/* Legend Explanation */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          <div className="p-3 bg-[#0a0a0a] rounded-lg border border-[#333]">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded-full bg-[#99E135]"></div>
              <span className="text-white font-medium">Rule-Based</span>
            </div>
            <p className="text-gray-400 text-xs">Greedy hour-by-hour decisions. Fast but may not optimize for future prices.</p>
          </div>
          
          <div className="p-3 bg-[#0a0a0a] rounded-lg border border-[#333]">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded-full bg-[#4169E1]"></div>
              <span className="text-white font-medium">MILP Optimization</span>
            </div>
            <p className="text-gray-400 text-xs">Global 24-hour optimization. Plans ahead for price arbitrage and peak hours.</p>
          </div>
          
          <div className="p-3 bg-[#0a0a0a] rounded-lg border border-red-900/30">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 bg-red-500/50"></div>
              <span className="text-white font-medium">Peak Hours</span>
            </div>
            <p className="text-gray-400 text-xs">18:00-22:00 - Most expensive electricity. MILP typically discharges more here.</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
