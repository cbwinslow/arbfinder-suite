import React from "react";

export function Badge({
  children,
  className = "",
  variant = "default",
}: {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "secondary" | "destructive" | "outline";
}) {
  const variantStyles = {
    default: "bg-blue-600 text-white",
    secondary: "bg-gray-200 text-gray-800",
    destructive: "bg-red-600 text-white",
    outline: "border border-gray-300 text-gray-800",
  };

  return (
    <span
      className={`inline-block px-2 py-1 text-xs rounded ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
