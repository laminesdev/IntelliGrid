"use client"

import { useState } from "react";
import Image from "next/image";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, Scale, Table, Loader2 } from "lucide-react";
import { SimulationConfig } from "@/types";
import { useSimulation } from "@/hooks/useSimulation";
import { Sidebar } from "./Sidebar";
import { MetricCards } from "./MetricCards";
import { EnergyChart } from "./EnergyChart";
import { BatteryChart } from "./BatteryChart";
import { BatteryComparisonChart } from "./BatteryComparisonChart";
import { HourlyDataTable } from "./HourlyDataTable";
import { Alerts } from "./Alerts";
import { ImpactAnalysis } from "./ImpactAnalysis";

const defaultConfig: SimulationConfig = {
  season: 'summer',
  weather: 'sunny',
  day_type: 'weekday',
  mode: 'rule',
  seed: 42,
  tomorrow_weather: 'sunny',
};

export function Dashboard() {
  const [config, setConfig] = useState<SimulationConfig>(defaultConfig);
  const { simulation, comparison, alerts, impact, simulate, compare, reset } = useSimulation();

  const handleSimulate = () => {
    reset();
    simulate(config);
  };

  const handleCompare = () => {
    reset();
    compare(config);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header - Logo Only, Left Aligned */}
      <header className="border-b border-[#333] bg-black px-6 py-4">
        <div className="flex items-center justify-start">
          <Image
            src="/logo.svg"
            alt="IntelliGrid"
            width={100}
            height={50}
            priority
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Sidebar
              config={config}
              onConfigChange={setConfig}
              onSimulate={handleSimulate}
              onCompare={handleCompare}
              loading={simulation.loading || comparison.loading}
            />
          </div>

          {/* Main Dashboard */}
          <div className="lg:col-span-3 space-y-6 relative">
            {/* Loading Overlay */}
            {(simulation.loading || comparison.loading) && (
              <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm rounded-xl">
                <div className="flex flex-col items-center gap-4">
                  <Loader2 className="h-12 w-12 animate-spin text-[#99E135]" />
                  <p className="text-lg font-semibold text-white">
                    {simulation.loading ? 'Running Simulation...' : 'Comparing Optimizations...'}
                  </p>
                  <p className="text-sm text-gray-400">
                    This may take a moment
                  </p>
                </div>
              </div>
            )}

            {/* Metric Cards */}
            <MetricCards data={simulation.data} />

            {/* Tabs for different views */}
            <Tabs defaultValue="charts" className="w-full">
              <TabsList className="grid w-full grid-cols-3 bg-[#0a0a0a] border border-[#333]">
                <TabsTrigger
                  value="charts"
                  className="flex items-center justify-center gap-2 data-[state=active]:bg-[#99E135] data-[state=active]:text-black"
                >
                  <BarChart3 className="h-4 w-4" />
                  <span>Charts</span>
                </TabsTrigger>
                <TabsTrigger
                  value="comparison"
                  className="flex items-center justify-center gap-2 data-[state=active]:bg-[#99E135] data-[state=active]:text-black"
                >
                  <Scale className="h-4 w-4" />
                  <span>Comparison</span>
                </TabsTrigger>
                <TabsTrigger
                  value="data"
                  className="flex items-center justify-center gap-2 data-[state=active]:bg-[#99E135] data-[state=active]:text-black"
                >
                  <Table className="h-4 w-4" />
                  <span>Data</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="charts" className="space-y-6 mt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <EnergyChart data={simulation.data} />
                  <BatteryChart data={simulation.data} />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Alerts alerts={alerts} />
                  <ImpactAnalysis metrics={impact} />
                </div>
              </TabsContent>

              <TabsContent value="comparison" className="space-y-6 mt-6">
                {comparison.ruleData && comparison.milpData ? (
                  <div className="space-y-6">
                    {/* Battery Strategy Comparison */}
                    <BatteryComparisonChart 
                      ruleData={comparison.ruleData} 
                      milpData={comparison.milpData} 
                    />
                    
                    {/* Comparison Results */}
                    <div className="glass rounded-xl p-6">
                      <h3 className="text-lg font-semibold mb-4 text-white">Comparison Results</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="text-center">
                          <p className="text-sm text-gray-400">Daily Cost Savings</p>
                          <p className="text-2xl font-bold text-[#99E135]">
                            {comparison.costSavings.toFixed(2)} DZD
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-400">Cost Improvement</p>
                          <p className="text-2xl font-bold text-[#99E135]">
                            {comparison.improvementPercent.toFixed(1)}%
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-400">Different Decisions</p>
                          <p className="text-2xl font-bold text-[#99E135]">
                            {comparison.differentDecisionsCount} hours
                          </p>
                        </div>
                      </div>
                      <div className="mt-4 p-3 bg-[#0a0a0a] rounded-lg border border-[#333]">
                        <p className="text-sm text-gray-400 text-center">
                          MILP optimized battery usage saves <span className="text-[#99E135] font-bold">{comparison.costSavings.toFixed(2)} DZD</span> per day compared to rule-based approach
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-[400px] flex items-center justify-center text-gray-500 glass rounded-xl">
                    Click "Compare Rule vs MILP" to see battery optimization comparison
                  </div>
                )}
              </TabsContent>

              <TabsContent value="data" className="mt-6">
                <HourlyDataTable 
                  data={simulation.data}
                  comparisonData={comparison.ruleData && comparison.milpData ? {
                    rule: comparison.ruleData,
                    milp: comparison.milpData
                  } : null}
                  mode={config.mode}
                />
              </TabsContent>
            </Tabs>

            {/* Error Display */}
            {simulation.error && (
              <div className="bg-red-900/20 border border-red-500/50 text-red-400 p-4 rounded-lg">
                <p className="font-semibold">Error running simulation:</p>
                <p>{simulation.error}</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
