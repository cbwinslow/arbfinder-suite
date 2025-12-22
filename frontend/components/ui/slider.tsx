import React from "react";

export function Slider({
  value,
  onValueChange,
  min = 0,
  max = 100,
  step = 1,
  className = "",
  id,
}: {
  value?: number[];
  onValueChange?: (value: number[]) => void;
  min?: number;
  max?: number;
  step?: number;
  className?: string;
  id?: string;
}) {
  return (
    <input
      id={id}
      type="range"
      min={min}
      max={max}
      step={step}
      value={value?.[0] || 0}
      onChange={(e) => onValueChange?.([parseFloat(e.target.value)])}
      className={`w-full ${className}`}
    />
  );
}
