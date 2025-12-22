"use client";

import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import {
  Calculator,
  TrendingDown,
  AlertCircle,
  DollarSign,
} from "lucide-react";

interface PriceAdjustment {
  type: string;
  factor: number;
  amount: number;
  description: string;
}

interface PriceAnalysisResult {
  base_price: number;
  final_price: number;
  total_adjustment: number;
  total_adjustment_pct: number;
  adjustments: PriceAdjustment[];
}

export default function PriceAnalysisDashboard() {
  const [basePrice, setBasePrice] = useState<number>(100);
  const [age, setAge] = useState<number>(0);
  const [condition, setCondition] = useState<string>("good");
  const [completeness, setCompleteness] = useState<number>(100);
  const [result, setResult] = useState<PriceAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  const calculatePrice = async () => {
    setLoading(true);
    try {
      // Simulate API call - replace with actual API
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Mock calculation
      const conditionMultipliers: Record<string, number> = {
        new: 1.0,
        like_new: 0.95,
        excellent: 0.85,
        very_good: 0.75,
        good: 0.65,
        fair: 0.5,
        poor: 0.3,
      };

      const depreciationFactor = Math.pow(0.5, age / 2.5); // Exponential decay
      const conditionFactor = conditionMultipliers[condition] || 0.75;
      const completenessFactor = completeness / 100;

      const afterDepreciation = basePrice * depreciationFactor;
      const afterCondition = afterDepreciation * conditionFactor;
      const finalPrice = afterCondition * completenessFactor;

      const mockResult: PriceAnalysisResult = {
        base_price: basePrice,
        final_price: finalPrice,
        total_adjustment: basePrice - finalPrice,
        total_adjustment_pct: ((basePrice - finalPrice) / basePrice) * 100,
        adjustments: [
          {
            type: "age_depreciation",
            factor: depreciationFactor,
            amount: basePrice - afterDepreciation,
            description: `${age} years old (exponential decay)`,
          },
          {
            type: "condition",
            factor: conditionFactor,
            amount: afterDepreciation - afterCondition,
            description: `Condition: ${condition}`,
          },
          {
            type: "completeness",
            factor: completenessFactor,
            amount: afterCondition - finalPrice,
            description: `${completeness}% complete`,
          },
        ],
      };

      setResult(mockResult);
    } catch (error) {
      console.error("Error calculating price:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(value);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Price Analysis Dashboard</h1>
          <p className="text-muted-foreground">
            Calculate adjusted prices based on age, condition, and market
            factors
          </p>
        </div>
        <Calculator className="h-12 w-12 text-primary" />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Item Details</CardTitle>
            <CardDescription>
              Enter item information to calculate adjusted price
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="basePrice">Base Price ($)</Label>
              <Input
                id="basePrice"
                type="number"
                value={basePrice}
                onChange={(e) => setBasePrice(parseFloat(e.target.value) || 0)}
                placeholder="100.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="age">Age (years)</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="age"
                  min={0}
                  max={10}
                  step={0.5}
                  value={[age]}
                  onValueChange={(value) => setAge(value[0])}
                  className="flex-1"
                />
                <span className="w-12 text-right">{age}</span>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="condition">Condition</Label>
              <Select value={condition} onValueChange={setCondition}>
                <SelectTrigger id="condition">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">New/Sealed</SelectItem>
                  <SelectItem value="like_new">Like New</SelectItem>
                  <SelectItem value="excellent">Excellent</SelectItem>
                  <SelectItem value="very_good">Very Good</SelectItem>
                  <SelectItem value="good">Good</SelectItem>
                  <SelectItem value="fair">Fair</SelectItem>
                  <SelectItem value="poor">Poor</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="completeness">Completeness (%)</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="completeness"
                  min={0}
                  max={100}
                  step={5}
                  value={[completeness]}
                  onValueChange={(value) => setCompleteness(value[0])}
                  className="flex-1"
                />
                <span className="w-12 text-right">{completeness}%</span>
              </div>
            </div>

            <Button
              onClick={calculatePrice}
              className="w-full"
              disabled={loading}
            >
              {loading ? "Calculating..." : "Calculate Price"}
            </Button>
          </CardContent>
        </Card>

        {/* Results */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle>Price Analysis Results</CardTitle>
              <CardDescription>Adjusted price breakdown</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Summary */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Base Price</p>
                  <p className="text-2xl font-bold">
                    {formatCurrency(result.base_price)}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Final Price</p>
                  <p className="text-2xl font-bold text-green-600">
                    {formatCurrency(result.final_price)}
                  </p>
                </div>
              </div>

              {/* Total Adjustment */}
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingDown className="h-5 w-5 text-red-500" />
                    <span className="font-semibold">Total Adjustment</span>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-red-600">
                      -{formatCurrency(result.total_adjustment)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      ({result.total_adjustment_pct.toFixed(1)}%)
                    </p>
                  </div>
                </div>
              </div>

              {/* Adjustments Breakdown */}
              <div className="space-y-3">
                <h4 className="font-semibold flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Adjustment Breakdown
                </h4>
                {result.adjustments.map((adj, index) => (
                  <div key={index} className="p-3 border rounded-lg space-y-1">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <Badge variant="outline">
                          {adj.type.replace("_", " ").toUpperCase()}
                        </Badge>
                        <p className="text-sm text-muted-foreground">
                          {adj.description}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-red-600">
                          -{formatCurrency(adj.amount)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          ×{adj.factor.toFixed(3)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Price Range Indicator */}
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    Fair Market Range
                  </span>
                  <span className="font-semibold">
                    {formatCurrency(result.final_price * 0.9)} -{" "}
                    {formatCurrency(result.final_price * 1.1)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle>How It Works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-blue-500" />
                <h4 className="font-semibold">Age Depreciation</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Exponential decay model with 2.5 year half-life for technology
                items. Older items lose value at an accelerating rate.
              </p>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-500" />
                <h4 className="font-semibold">Condition Factor</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Multiplier based on physical condition: New (100%), Good (65%),
                Fair (50%). Reflects wear and functionality.
              </p>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-green-500" />
                <h4 className="font-semibold">Completeness</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Percentage of original accessories and parts present. Missing
                items reduce overall value proportionally.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
