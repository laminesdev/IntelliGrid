"use client"

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { SimulationResponse, HourlyData } from "@/types";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { 
  Download, 
  Database, 
  ChevronDown, 
  ChevronUp,
  Eye,
  EyeOff
} from "lucide-react";
import { cn } from "@/lib/utils";

interface HourlyDataTableProps {
  data: SimulationResponse | null;
  comparisonData?: {
    rule: SimulationResponse;
    milp: SimulationResponse;
  } | null;
  mode: 'rule' | 'milp';
}

type ViewMode = 'current' | 'comparison';
type ComparisonView = 'rule' | 'milp';
type DisplayMode = 'simplified' | 'full';

export function HourlyDataTable({ 
  data, 
  comparisonData, 
  mode 
}: HourlyDataTableProps) {
  const [viewMode, setViewMode] = useState<ViewMode>(
    comparisonData ? 'comparison' : 'current'
  );
  const [comparisonView, setComparisonView] = useState<ComparisonView>('rule');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [displayMode, setDisplayMode] = useState<DisplayMode>('full');
  const [isExpanded, setIsExpanded] = useState(true);

  // Determine which data to display
  const displayData = useMemo(() => {
    if (viewMode === 'comparison' && comparisonData) {
      return comparisonView === 'rule' 
        ? comparisonData.rule 
        : comparisonData.milp;
    }
    return data;
  }, [viewMode, comparisonView, comparisonData, data]);

  // Helper functions
  const getActionColor = (action: string) => {
    switch(action) {
      case 'charge_battery': return 'bg-green-500 hover:bg-green-600';
      case 'discharge_battery': return 'bg-red-500 hover:bg-red-600';
      case 'sell_to_grid': return 'bg-yellow-500 hover:bg-yellow-600';
      case 'use_grid': return 'bg-blue-500 hover:bg-blue-600';
      default: return 'bg-gray-500 hover:bg-gray-600';
    }
  };

  const getActionLabel = (action: string) => {
    switch(action) {
      case 'charge_battery': return 'Charge';
      case 'discharge_battery': return 'Discharge';
      case 'sell_to_grid': return 'Sell';
      case 'use_grid': return 'Grid';
      default: return 'Idle';
    }
  };

  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toFixed(decimals);
  };

  const isPeakHour = (hour: number) => hour >= 18 && hour <= 22;

  // Calculate totals
  const totals = useMemo(() => {
    if (!displayData?.hourly_data) return null;
    
    return displayData.hourly_data.reduce((acc, hour) => ({
      solar: acc.solar + hour.solar_production,
      consumption: acc.consumption + hour.consumption,
      gridUsage: acc.gridUsage + hour.grid_usage,
      gridExport: acc.gridExport + hour.grid_export,
      cost: acc.cost + hour.cost,
      savings: acc.savings + hour.savings,
    }), { solar: 0, consumption: 0, gridUsage: 0, gridExport: 0, cost: 0, savings: 0 });
  }, [displayData]);

  // CSV Export
  const exportToCSV = () => {
    if (!data?.hourly_data) return;

    let csvContent = '';
    const timestamp = new Date().toISOString().split('T')[0];

    if (comparisonData && viewMode === 'comparison') {
      // Comparison mode: side-by-side columns
      const headers = [
        'Hour',
        'Solar (Rule)', 'Solar (MILP)',
        'Consumption (Rule)', 'Consumption (MILP)',
        'Battery Level (Rule)', 'Battery Level (MILP)',
        'Battery SOC % (Rule)', 'Battery SOC % (MILP)',
        'Grid Usage (Rule)', 'Grid Usage (MILP)',
        'Grid Export (Rule)', 'Grid Export (MILP)',
        'Net Energy (Rule)', 'Net Energy (MILP)',
        'Action (Rule)', 'Action (MILP)',
        'Grid Price (Rule)', 'Grid Price (MILP)',
        'Cost (Rule)', 'Cost (MILP)',
        'Savings (Rule)', 'Savings (MILP)',
      ];
      csvContent = headers.join(',') + '\n';

      for (let i = 0; i < 24; i++) {
        const rule = comparisonData.rule.hourly_data[i];
        const milp = comparisonData.milp.hourly_data[i];
        const row = [
          i,
          rule.solar_production, milp.solar_production,
          rule.consumption, milp.consumption,
          rule.battery_level, milp.battery_level,
          (rule.battery_soc * 100).toFixed(1), (milp.battery_soc * 100).toFixed(1),
          rule.grid_usage, milp.grid_usage,
          rule.grid_export, milp.grid_export,
          rule.net_energy, milp.net_energy,
          rule.action, milp.action,
          rule.grid_price, milp.grid_price,
          rule.cost, milp.cost,
          rule.savings, milp.savings,
        ];
        csvContent += row.join(',') + '\n';
      }
    } else {
      // Single mode
      const headers = [
        'Hour',
        'Solar Production (kWh)',
        'Consumption (kWh)',
        'Battery Level (kWh)',
        'Battery SOC (%)',
        'Grid Usage (kWh)',
        'Grid Export (kWh)',
        'Net Energy (kWh)',
        'Action',
        'Grid Price (DZD/kWh)',
        'Cost (DZD)',
        'Savings (DZD)',
      ];
      csvContent = headers.join(',') + '\n';

      data.hourly_data.forEach(hour => {
        const row = [
          hour.hour,
          hour.solar_production,
          hour.consumption,
          hour.battery_level,
          (hour.battery_soc * 100).toFixed(1),
          hour.grid_usage,
          hour.grid_export,
          hour.net_energy,
          hour.action,
          hour.grid_price,
          hour.cost,
          hour.savings,
        ];
        csvContent += row.join(',') + '\n';
      });
    }

    // Create and trigger download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `intelligrid_data_${timestamp}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Render functions
  const renderSOCBar = (soc: number) => {
    const percentage = Math.round(soc * 100);
    return (
      <div className="flex items-center gap-2 min-w-[80px]">
        <div className="w-12 h-2 bg-gray-700 rounded-full overflow-hidden">
          <div 
            className={cn(
              "h-full rounded-full transition-all",
              percentage > 80 ? "bg-green-500" : 
              percentage > 40 ? "bg-[#99E135]" : "bg-red-500"
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className="text-xs whitespace-nowrap">{percentage}%</span>
      </div>
    );
  };

  const renderRow = (hour: HourlyData, index: number) => {
    const peakHour = isPeakHour(hour.hour);
    const isEven = index % 2 === 0;
    
    if (displayMode === 'simplified') {
      // Mobile simplified view - 6 columns
      return (
        <TableRow 
          key={hour.hour}
          className={cn(
            "transition-colors hover:bg-[#252525]",
            isEven ? "bg-[#0f0f0f]" : "bg-transparent",
            peakHour && "bg-red-500/10"
          )}
        >
          <TableCell className="font-medium text-white sticky left-0 bg-inherit z-10">
            H{hour.hour.toString().padStart(2, '0')}
            {peakHour && <span className="ml-1 text-xs text-red-400">●</span>}
          </TableCell>
          <TableCell className="text-right text-[#99E135]">
            {formatNumber(hour.solar_production)}
          </TableCell>
          <TableCell className="text-right text-white">
            {formatNumber(hour.consumption)}
          </TableCell>
          <TableCell className="text-right">
            {renderSOCBar(hour.battery_soc)}
          </TableCell>
          <TableCell>
            <Badge className={cn("text-xs", getActionColor(hour.action))}>
              {getActionLabel(hour.action)}
            </Badge>
          </TableCell>
          <TableCell className={cn(
            "text-right font-medium",
            hour.cost > 0 ? "text-red-400" : "text-green-400"
          )}>
            {formatNumber(hour.cost)}
          </TableCell>
        </TableRow>
      );
    }

    // Full desktop view - 12 columns
    return (
      <TableRow 
        key={hour.hour}
        className={cn(
          "transition-colors hover:bg-[#252525]",
          isEven ? "bg-[#0f0f0f]" : "bg-transparent",
          peakHour && "bg-red-500/10"
        )}
      >
        <TableCell className="font-medium text-white sticky left-0 bg-inherit z-10">
          H{hour.hour.toString().padStart(2, '0')}
          {peakHour && <span className="ml-1 text-xs text-red-400">●</span>}
        </TableCell>
        <TableCell className="text-right text-[#99E135]">
          {formatNumber(hour.solar_production)}
        </TableCell>
        <TableCell className="text-right text-white">
          {formatNumber(hour.consumption)}
        </TableCell>
        <TableCell className="text-right text-white">
          {formatNumber(hour.battery_level)}
        </TableCell>
        <TableCell className="text-right">
          {renderSOCBar(hour.battery_soc)}
        </TableCell>
        <TableCell className={cn(
          "text-right",
          hour.grid_usage > 0 ? "text-red-400" : "text-gray-400"
        )}>
          {formatNumber(hour.grid_usage)}
        </TableCell>
        {showAdvanced && (
          <TableCell className="text-right text-yellow-400">
            {formatNumber(hour.grid_export)}
          </TableCell>
        )}
        <TableCell className={cn(
          "text-right font-medium",
          hour.net_energy > 0 ? "text-[#99E135]" : "text-red-400"
        )}>
          {hour.net_energy > 0 ? '+' : ''}{formatNumber(hour.net_energy)}
        </TableCell>
        <TableCell>
          <Badge className={cn("text-xs", getActionColor(hour.action))}>
            {getActionLabel(hour.action)}
          </Badge>
        </TableCell>
        <TableCell className="text-right text-gray-400">
          {formatNumber(hour.grid_price)}
        </TableCell>
        <TableCell className={cn(
          "text-right font-medium",
          hour.cost > 0 ? "text-red-400" : "text-green-400"
        )}>
          {formatNumber(hour.cost)}
        </TableCell>
        <TableCell className="text-right font-bold text-[#99E135]">
          +{formatNumber(hour.savings)}
        </TableCell>
      </TableRow>
    );
  };

  const renderTotals = () => {
    if (!totals) return null;

    if (displayMode === 'simplified') {
      return (
        <TableRow className="bg-[#1a1a1a] font-bold border-t-2 border-[#333]">
          <TableCell className="text-white sticky left-0 bg-[#1a1a1a] z-10">TOTAL</TableCell>
          <TableCell className="text-right text-[#99E135]">{formatNumber(totals.solar)}</TableCell>
          <TableCell className="text-right text-white">{formatNumber(totals.consumption)}</TableCell>
          <TableCell className="text-right">-</TableCell>
          <TableCell>-</TableCell>
          <TableCell className={cn(
            "text-right",
            totals.cost > 0 ? "text-red-400" : "text-green-400"
          )}>
            {formatNumber(totals.cost)}
          </TableCell>
        </TableRow>
      );
    }

    return (
      <TableRow className="bg-[#1a1a1a] font-bold border-t-2 border-[#333]">
        <TableCell className="text-white sticky left-0 bg-[#1a1a1a] z-10">TOTAL</TableCell>
        <TableCell className="text-right text-[#99E135]">{formatNumber(totals.solar)}</TableCell>
        <TableCell className="text-right text-white">{formatNumber(totals.consumption)}</TableCell>
        <TableCell className="text-right">-</TableCell>
        <TableCell className="text-right">-</TableCell>
        <TableCell className="text-right text-red-400">{formatNumber(totals.gridUsage)}</TableCell>
        {showAdvanced && (
          <TableCell className="text-right text-yellow-400">{formatNumber(totals.gridExport)}</TableCell>
        )}
        <TableCell className="text-right">-</TableCell>
        <TableCell>-</TableCell>
        <TableCell className="text-right text-gray-400">-</TableCell>
        <TableCell className="text-right text-red-400">{formatNumber(totals.cost)}</TableCell>
        <TableCell className="text-right text-[#99E135]">+{formatNumber(totals.savings)}</TableCell>
      </TableRow>
    );
  };

  // Empty state
  if (!displayData?.hourly_data?.length) {
    return (
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Database className="h-5 w-5 text-[#99E135]" />
            Hourly Data
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[400px] flex items-center justify-center text-gray-400">
          Run a simulation to view detailed hourly data
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass">
      <CardHeader className="pb-4">
        <div className="flex flex-col gap-4">
          {/* Title Row */}
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-white">
              <Database className="h-5 w-5 text-[#99E135]" />
              Hourly Simulation Data
              {viewMode === 'comparison' && (
                <Badge className="ml-2 bg-blue-500">Comparison Mode</Badge>
              )}
            </CardTitle>
            
            <div className="flex items-center gap-2">
              {/* CSV Export */}
              <Button
                onClick={exportToCSV}
                size="sm"
                className="bg-[#99E135] text-black hover:bg-[#7bc929]"
              >
                <Download className="h-4 w-4 mr-1" />
                Export CSV
              </Button>
              
              {/* Expand/Collapse */}
              <Button
                onClick={() => setIsExpanded(!isExpanded)}
                size="sm"
                variant="outline"
                className="border-[#333]"
              >
                {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          {/* Controls Row */}
          <div className="flex flex-wrap items-center gap-4 text-sm">
            {/* Comparison Toggle */}
            {comparisonData && (
              <div className="flex items-center gap-2 bg-[#0a0a0a] p-2 rounded-lg border border-[#333]">
                <span className="text-gray-400 text-xs">View:</span>
                <div className="flex gap-1">
                  <Button
                    onClick={() => { setViewMode('comparison'); setComparisonView('rule'); }}
                    size="sm"
                    className={cn(
                      "text-xs",
                      viewMode === 'comparison' && comparisonView === 'rule'
                        ? "bg-[#99E135] text-black"
                        : "bg-transparent text-gray-400 hover:text-white"
                    )}
                  >
                    Rule Mode
                  </Button>
                  <Button
                    onClick={() => { setViewMode('comparison'); setComparisonView('milp'); }}
                    size="sm"
                    className={cn(
                      "text-xs",
                      viewMode === 'comparison' && comparisonView === 'milp'
                        ? "bg-blue-500 text-white"
                        : "bg-transparent text-gray-400 hover:text-white"
                    )}
                  >
                    MILP Mode
                  </Button>
                </div>
              </div>
            )}

            {/* Display Mode Toggle */}
            <div className="flex items-center gap-2">
              <Switch
                id="display-mode"
                checked={displayMode === 'simplified'}
                onCheckedChange={(checked) => setDisplayMode(checked ? 'simplified' : 'full')}
              />
              <Label htmlFor="display-mode" className="text-gray-400 text-xs cursor-pointer">
                {displayMode === 'simplified' ? (
                  <span className="flex items-center gap-1"><EyeOff className="h-3 w-3" /> Simple View</span>
                ) : (
                  <span className="flex items-center gap-1"><Eye className="h-3 w-3" /> Full View</span>
                )}
              </Label>
            </div>

            {/* Advanced Toggle */}
            {displayMode === 'full' && (
              <div className="flex items-center gap-2">
                <Switch
                  id="advanced"
                  checked={showAdvanced}
                  onCheckedChange={setShowAdvanced}
                />
                <Label htmlFor="advanced" className="text-gray-400 text-xs cursor-pointer">
                  Show Advanced (Grid Export)
                </Label>
              </div>
            )}
          </div>

          {/* Legend */}
          {isExpanded && (
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="text-gray-500">Peak Hours (18-22):</span>
              <span className="px-2 py-1 bg-red-500/10 border border-red-500/30 rounded text-red-400">
                ● Red tint
              </span>
              <span className="text-gray-500 ml-4">Actions:</span>
              <Badge className="bg-green-500 text-xs">Charge</Badge>
              <Badge className="bg-red-500 text-xs">Discharge</Badge>
              <Badge className="bg-yellow-500 text-xs">Sell</Badge>
              <Badge className="bg-blue-500 text-xs">Grid</Badge>
              <Badge className="bg-gray-500 text-xs">Idle</Badge>
            </div>
          )}
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-[#1a1a1a] hover:bg-[#1a1a1a] border-b border-[#333]">
                  <TableHead className="text-white font-semibold sticky left-0 bg-[#1a1a1a] z-10 min-w-[60px]">
                    Hour
                  </TableHead>
                  <TableHead className="text-right text-[#99E135] min-w-[100px]">Solar (kWh)</TableHead>
                  <TableHead className="text-right text-white min-w-[100px]">Consumption (kWh)</TableHead>
                  <TableHead className="text-right text-white min-w-[100px]">Battery (kWh)</TableHead>
                  <TableHead className="text-right text-white min-w-[100px]">SOC</TableHead>
                  <TableHead className="text-right text-white min-w-[100px]">Grid In (kWh)</TableHead>
                  {showAdvanced && (
                    <TableHead className="text-right text-yellow-400 min-w-[100px]">Grid Out (kWh)</TableHead>
                  )}
                  {displayMode === 'full' && (
                    <>
                      <TableHead className="text-right text-white min-w-[100px]">Net (kWh)</TableHead>
                      <TableHead className="text-white min-w-[100px]">Action</TableHead>
                      <TableHead className="text-right text-gray-400 min-w-[90px]">Price (DZD)</TableHead>
                    </>
                  )}
                  <TableHead className="text-right text-red-400 min-w-[90px]">Cost (DZD)</TableHead>
                  {displayMode === 'full' && (
                    <TableHead className="text-right text-[#99E135] min-w-[100px]">Savings (DZD)</TableHead>
                  )}
                </TableRow>
              </TableHeader>
              <TableBody>
                {displayData.hourly_data.map((hour, index) => renderRow(hour, index))}
                {renderTotals()}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
