"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { SimulationConfig } from "@/types";
import { 
  Settings2, 
  Sun, 
  Snowflake, 
  CloudSun, 
  Cloud, 
  CloudRain,
  Calendar,
  CalendarDays,
  Play,
  Scale,
  Bot,
  ClipboardList
} from "lucide-react";

interface SidebarProps {
  config: SimulationConfig;
  onConfigChange: (config: SimulationConfig) => void;
  onSimulate: () => void;
  onCompare: () => void;
  loading: boolean;
}

export function Sidebar({ config, onConfigChange, onSimulate, onCompare, loading }: SidebarProps) {
  return (
    <Card className="h-full glass">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2 text-white">
          <Settings2 className="h-5 w-5 text-[#99E135]" />
          Configuration
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Season */}
        <div className="space-y-2">
          <Label className="text-gray-300">Season</Label>
          <Select
            value={config.season}
            onValueChange={(value: 'summer' | 'winter') => 
              onConfigChange({ ...config, season: value })
            }
          >
            <SelectTrigger className="bg-[#0a0a0a] border-[#333] text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#0a0a0a] border-[#333]">
              <SelectItem value="summer" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <Sun className="h-4 w-4 text-[#99E135]" />
                  <span>Summer</span>
                </div>
              </SelectItem>
              <SelectItem value="winter" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <Snowflake className="h-4 w-4 text-blue-400" />
                  <span>Winter</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Weather */}
        <div className="space-y-2">
          <Label className="text-gray-300">Today&apos;s Weather</Label>
          <Select
            value={config.weather}
            onValueChange={(value: 'sunny' | 'partly_cloudy' | 'cloudy' | 'rainy') => 
              onConfigChange({ ...config, weather: value })
            }
          >
            <SelectTrigger className="bg-[#0a0a0a] border-[#333] text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#0a0a0a] border-[#333]">
              <SelectItem value="sunny" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <Sun className="h-4 w-4 text-[#99E135]" />
                  <span>Sunny</span>
                </div>
              </SelectItem>
              <SelectItem value="partly_cloudy" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <CloudSun className="h-4 w-4 text-yellow-400" />
                  <span>Partly Cloudy</span>
                </div>
              </SelectItem>
              <SelectItem value="cloudy" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <Cloud className="h-4 w-4 text-gray-400" />
                  <span>Cloudy</span>
                </div>
              </SelectItem>
              <SelectItem value="rainy" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <CloudRain className="h-4 w-4 text-blue-400" />
                  <span>Rainy</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Tomorrow&apos;s Weather */}
        <div className="space-y-2">
          <Label className="text-gray-300">Tomorrow&apos;s Weather (Forecast)</Label>
          <Select
            value={config.tomorrow_weather || config.weather}
            onValueChange={(value: 'sunny' | 'partly_cloudy' | 'cloudy' | 'rainy') => 
              onConfigChange({ ...config, tomorrow_weather: value })
            }
          >
            <SelectTrigger className="bg-[#0a0a0a] border-[#333] text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#0a0a0a] border-[#333]">
              <SelectItem value="sunny" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <Sun className="h-4 w-4 text-[#99E135]" />
                  <span>Sunny</span>
                </div>
              </SelectItem>
              <SelectItem value="partly_cloudy" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <CloudSun className="h-4 w-4 text-yellow-400" />
                  <span>Partly Cloudy</span>
                </div>
              </SelectItem>
              <SelectItem value="cloudy" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <Cloud className="h-4 w-4 text-gray-400" />
                  <span>Cloudy</span>
                </div>
              </SelectItem>
              <SelectItem value="rainy" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <CloudRain className="h-4 w-4 text-blue-400" />
                  <span>Rainy</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Day Type */}
        <div className="space-y-2">
          <Label className="text-gray-300">Day Type</Label>
          <Select
            value={config.day_type}
            onValueChange={(value: 'weekday' | 'weekend') => 
              onConfigChange({ ...config, day_type: value })
            }
          >
            <SelectTrigger className="bg-[#0a0a0a] border-[#333] text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#0a0a0a] border-[#333]">
              <SelectItem value="weekday" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-[#99E135]" />
                  <span>Weekday</span>
                </div>
              </SelectItem>
              <SelectItem value="weekend" className="text-white focus:bg-[#1a1a1a] focus:text-white">
                <div className="flex items-center gap-2">
                  <CalendarDays className="h-4 w-4 text-purple-400" />
                  <span>Weekend</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Optimization Mode */}
        <div className="space-y-2">
          <Label className="text-gray-300">Optimization Mode</Label>
          <div className="flex items-center space-x-3">
            <Switch
              id="milp-mode"
              checked={config.mode === 'milp'}
              onCheckedChange={(checked) => 
                onConfigChange({ ...config, mode: checked ? 'milp' : 'rule' })
              }
              className="data-[state=checked]:bg-[#99E135]"
            />
            <Label htmlFor="milp-mode" className="cursor-pointer">
              {config.mode === 'milp' ? (
                <Badge className="bg-[#99E135] text-black hover:bg-[#7bc025]">
                  <Bot className="h-3 w-3 mr-1" />
                  MILP Optimization
                </Badge>
              ) : (
                <Badge variant="outline" className="border-[#333] text-gray-300">
                  <ClipboardList className="h-3 w-3 mr-1" />
                  Rule-Based
                </Badge>
              )}
            </Label>
          </div>
          <p className="text-xs text-gray-500">
            {config.mode === 'milp' 
              ? "Uses mathematical optimization for best results" 
              : "Uses simple if-then rules (faster)"}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3 pt-4">
          <Button 
            onClick={onSimulate} 
            disabled={loading}
            className="w-full bg-[#99E135] hover:bg-[#7bc025] text-black font-semibold transition-all duration-300 hover:shadow-[0_0_20px_rgba(153,225,53,0.4)]"
          >
            {loading ? (
              'Running...'
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Run Simulation
              </>
            )}
          </Button>
          
          <Button 
            onClick={onCompare} 
            disabled={loading}
            variant="outline"
            className="w-full border-[#333] text-white hover:bg-[#1a1a1a] hover:border-[#99E135] transition-all duration-300"
          >
            {loading ? (
              'Comparing...'
            ) : (
              <>
                <Scale className="h-4 w-4 mr-2" />
                Compare Rule vs MILP
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
