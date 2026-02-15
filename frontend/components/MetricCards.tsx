"use client"

import { Card, CardContent } from "@/components/ui/card";
import { Sun, Zap, Battery, Wallet } from "lucide-react";
import { SimulationResponse } from "@/types";

interface MetricCardsProps {
  data: SimulationResponse | null;
}

export function MetricCards({ data }: MetricCardsProps) {
  if (!data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="glass animate-pulse">
            <CardContent className="p-6">
              <div className="h-4 bg-[#1a1a1a] rounded w-24 mb-2"></div>
              <div className="h-8 bg-[#1a1a1a] rounded w-32"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const lastHour = data.hourly_data[data.hourly_data.length - 1];

  const metrics = [
    {
      title: "Total Solar Production",
      value: `${data.total_solar.toFixed(1)} kWh`,
      icon: Sun,
      color: "text-[#99E135]",
      bgColor: "bg-[#99E135]/10",
      borderColor: "border-[#99E135]/30",
    },
    {
      title: "Total Consumption",
      value: `${data.total_consumption.toFixed(1)} kWh`,
      icon: Zap,
      color: "text-white",
      bgColor: "bg-white/10",
      borderColor: "border-white/30",
    },
    {
      title: "Final Battery Level",
      value: `${(lastHour.battery_soc * 100).toFixed(1)}%`,
      icon: Battery,
      color: "text-[#99E135]",
      bgColor: "bg-[#99E135]/10",
      borderColor: "border-[#99E135]/30",
    },
    {
      title: "Total Cost",
      value: `${data.total_cost.toFixed(2)} DZD`,
      icon: Wallet,
      color: "text-white",
      bgColor: "bg-white/10",
      borderColor: "border-white/30",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric) => (
        <Card 
          key={metric.title} 
          className={`glass glass-hover border-l-4 ${metric.borderColor} transition-all duration-300`}
        >
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">
                  {metric.title}
                </p>
                <h3 className={`text-2xl font-bold mt-1 ${metric.color}`}>
                  {metric.value}
                </h3>
              </div>
              <div className={`p-3 rounded-full ${metric.bgColor}`}>
                <metric.icon className={`h-6 w-6 ${metric.color}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
