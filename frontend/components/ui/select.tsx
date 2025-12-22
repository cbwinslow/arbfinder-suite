import React from "react";

export function Select({
  children,
  value,
  onValueChange,
}: {
  children: React.ReactNode;
  value?: string;
  onValueChange?: (value: string) => void;
}) {
  return <div className="relative">{children}</div>;
}

export function SelectTrigger({
  children,
  className = "",
  id,
}: {
  children: React.ReactNode;
  className?: string;
  id?: string;
}) {
  return (
    <button
      id={id}
      className={`w-full px-3 py-2 border rounded text-left ${className}`}
    >
      {children}
    </button>
  );
}

export function SelectValue({ placeholder }: { placeholder?: string }) {
  return <span>{placeholder}</span>;
}

export function SelectContent({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`absolute z-10 w-full mt-1 bg-white border rounded shadow-lg ${className}`}
    >
      {children}
    </div>
  );
}

export function SelectItem({
  children,
  value,
  className = "",
}: {
  children: React.ReactNode;
  value: string;
  className?: string;
}) {
  return (
    <div className={`px-3 py-2 hover:bg-gray-100 cursor-pointer ${className}`}>
      {children}
    </div>
  );
}
