"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ImpactMetrics } from "@/types";
import { 
  Leaf, 
  TrendingDown, 
  DollarSign, 
  TreePine, 
  Droplets,
  Wind,
  Car,
  Bus,
  Zap,
  TrendingUp,
  Clock,
  Coins,
  Calendar,
  Timer,
  Percent,
  Download,
  TrendingUp as TrendingUpIcon
} from "lucide-react";

interface ImpactAnalysisProps {
  metrics: ImpactMetrics | null;
}

export function ImpactAnalysis({ metrics }: ImpactAnalysisProps) {
  if (!metrics) {
    return (
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Leaf className="h-5 w-5 text-[#99E135]" />
            Impact Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[200px] flex items-center justify-center text-gray-400">
          Run a simulation to see impact metrics
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-white">
          <Leaf className="h-5 w-5 text-[#99E135]" />
          Environmental & Financial Impact
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-0 pt-2">
        {/* Energy Independence - Top Banner */}
        <div className="p-4 bg-[#99E135]/10 border border-[#99E135]/30 rounded-lg mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#99E135] rounded-lg">
                <Zap className="h-6 w-6 text-black" />
              </div>
              <div>
                <p className="text-sm text-gray-400">Grid Independence</p>
                <p className="text-2xl font-bold text-white">{metrics.grid_independence}</p>
              </div>
            </div>
            <Badge className="bg-[#99E135] text-black text-lg">
              Energy Freedom
            </Badge>
          </div>
          <Progress 
            value={parseFloat(metrics.grid_independence)} 
            className="h-2 bg-[#1a1a1a] mt-3"
          />
        </div>

        {/* Financial Impact - List Format */}
        <div className="border-t border-[#333] pt-4 mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-3">
            <Coins className="h-5 w-5 text-[#99E135]" />
            Financial Impact
          </h3>
          
          <div className="space-y-1">
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <TrendingUpIcon className="h-5 w-5 text-[#99E135]" />
                <span className="text-gray-300">Daily Savings</span>
              </div>
              <span className="font-mono font-medium text-[#99E135]">{metrics.daily_savings}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-[#99E135]" />
                <span className="text-gray-300">Yearly Savings</span>
              </div>
              <span className="font-mono font-medium text-[#99E135]">{metrics.yearly_savings}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Clock className="h-5 w-5 text-[#99E135]" />
                <span className="text-gray-300">10-Year Savings</span>
              </div>
              <span className="font-mono font-medium text-[#99E135]">{metrics.ten_year_savings}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Percent className="h-5 w-5 text-[#99E135]" />
                <span className="text-gray-300">ROI</span>
              </div>
              <span className="font-mono font-medium text-[#99E135]">{metrics.roi_percent}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Timer className="h-5 w-5 text-[#99E135]" />
                <span className="text-gray-300">Payback Period</span>
              </div>
              <span className="font-mono font-medium text-white">{metrics.payback_years}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Download className="h-5 w-5 text-[#99E135]" />
                <span className="text-gray-300">Export Revenue</span>
              </div>
              <span className="font-mono font-medium text-[#99E135]">{metrics.export_revenue_yearly}</span>
            </div>
          </div>
        </div>

        {/* Environmental Impact - List Format */}
        <div className="border-t border-[#333] pt-4 mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-3">
            <TreePine className="h-5 w-5 text-[#99E135]" />
            Environmental Impact
          </h3>
          
          <div className="space-y-1">
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <TreePine className="h-5 w-5 text-green-500" />
                <span className="text-gray-300">Trees Equivalent</span>
              </div>
              <span className="font-mono font-medium text-green-400">{metrics.trees_equivalent}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Leaf className="h-5 w-5 text-[#99E135]" />
                <span className="text-gray-300">CO₂ Reduced</span>
              </div>
              <span className="font-mono font-medium text-[#99E135]">{metrics.co2_reduced}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Droplets className="h-5 w-5 text-blue-400" />
                <span className="text-gray-300">Water Saved</span>
              </div>
              <span className="font-mono font-medium text-blue-400">{metrics.water_saved}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Wind className="h-5 w-5 text-yellow-400" />
                <span className="text-gray-300">NOx Reduced</span>
              </div>
              <span className="font-mono font-medium text-yellow-400">{metrics.nox_reduced}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Wind className="h-5 w-5 text-orange-400" />
                <span className="text-gray-300">SO₂ Reduced</span>
              </div>
              <span className="font-mono font-medium text-orange-400">{metrics.so2_reduced}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 hover:bg-white/5 transition-colors rounded px-2">
              <div className="flex items-center gap-3">
                <Wind className="h-5 w-5 text-red-400" />
                <span className="text-gray-300">PM10 Reduced</span>
              </div>
              <span className="font-mono font-medium text-red-400">{metrics.pm10_reduced}</span>
            </div>
          </div>
        </div>

        {/* Transport Equivalence - Inline Format */}
        <div className="border-t border-[#333] pt-4 mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-3">
            <Car className="h-5 w-5 text-[#99E135]" />
            Transport Impact
          </h3>
          
          <div className="flex flex-col sm:flex-row gap-4 bg-[#0a0a0a] rounded-lg p-3 border border-[#333]">
            <div className="flex items-center gap-3 flex-1">
              <Car className="h-5 w-5 text-gray-400" />
              <div className="flex-1 flex items-center justify-between">
                <span className="text-gray-400 text-sm">Car Distance</span>
                <span className="font-mono font-medium text-white">{metrics.car_km_equivalent}</span>
              </div>
            </div>
            
            <div className="hidden sm:block w-px bg-[#333]" />
            
            <div className="flex items-center gap-3 flex-1">
              <Bus className="h-5 w-5 text-gray-400" />
              <div className="flex-1 flex items-center justify-between">
                <span className="text-gray-400 text-sm">Bus Distance</span>
                <span className="font-mono font-medium text-white">{metrics.bus_km_equivalent}</span>
              </div>
            </div>
          </div>
          
          <p className="text-xs text-gray-500 mt-2 text-center">
            Distance you could drive with the CO₂ emissions saved
          </p>
        </div>

        {/* Waste Reduction - Cleaner Design (Always Visible) */}
        <div className="border-t border-[#333] pt-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-[#99E135]" />
              <span className="font-semibold text-white">Solar Energy Waste Reduction</span>
            </div>
            <Badge className="bg-[#99E135] text-black font-mono">
              {metrics.waste_reduction_percent}
            </Badge>
          </div>
          
          <Progress 
            value={parseFloat(metrics.waste_reduction_percent)} 
            className="h-2 bg-[#1a1a1a] mb-3"
          />
          
          <div className="flex items-center justify-between bg-[#0a0a0a] rounded-lg p-3 border border-[#333]">
            <div className="text-center flex-1">
              <p className="text-xs text-gray-500 mb-1">Without Battery</p>
              <p className="font-mono text-red-400">{metrics.wasted_without}</p>
            </div>
            
            <div className="px-4">
              <TrendingDown className="h-5 w-5 text-[#99E135]" />
            </div>
            
            <div className="text-center flex-1">
              <p className="text-xs text-gray-500 mb-1">With Battery</p>
              <p className="font-mono text-[#99E135]">{metrics.wasted_with}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
