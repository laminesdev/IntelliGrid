"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { WeatherAlertResponse } from "@/types";
import { Bell, AlertCircle, Info, AlertTriangle } from "lucide-react";

interface AlertsProps {
  alerts: WeatherAlertResponse | null;
}

export function Alerts({ alerts }: AlertsProps) {
  if (!alerts || alerts.alerts.length === 0) {
    return (
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Bell className="h-5 w-5 text-[#99E135]" />
            Weather Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert className="bg-[#0a0a0a] border-[#333]">
            <Info className="h-4 w-4 text-[#99E135]" />
            <AlertTitle className="text-white">No Alerts</AlertTitle>
            <AlertDescription className="text-gray-400">
              Run a simulation to see weather-based recommendations
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-[#99E135]" />;
      default:
        return <Info className="h-4 w-4 text-blue-400" />;
    }
  };

  const getSeverityVariant = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'destructive';
      case 'warning':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Card className="glass">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Bell className="h-5 w-5 text-[#99E135]" />
          Weather Alerts & Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2 mb-4">
          <Badge variant="outline" className="border-[#333] text-gray-300">
            Status: {alerts.status}
          </Badge>
        </div>
        
        {alerts.alerts.map((alert, index) => (
          <Alert 
            key={index} 
            variant={getSeverityVariant(alert.severity)}
            className="bg-[#0a0a0a] border-[#333]"
          >
            {getSeverityIcon(alert.severity)}
            <AlertTitle className="flex items-center gap-2 text-white">
              {alert.title}
              <Badge 
                variant={alert.severity === 'critical' ? 'destructive' : 'secondary'}
                className={alert.severity === 'warning' ? 'bg-[#99E135] text-black' : ''}
              >
                {alert.severity}
              </Badge>
            </AlertTitle>
            <AlertDescription className="mt-2 text-gray-300">
              <p>{alert.message}</p>
              <p className="mt-1 font-medium text-[#99E135]">
                {alert.recommendation}
              </p>
            </AlertDescription>
          </Alert>
        ))}
      </CardContent>
    </Card>
  );
}
