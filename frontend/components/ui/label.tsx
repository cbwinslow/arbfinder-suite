import React from 'react';

export function Label({ children, className = '', htmlFor }: { 
  children: React.ReactNode; 
  className?: string;
  htmlFor?: string;
}) {
  return (
    <label htmlFor={htmlFor} className={`block text-sm font-medium mb-1 ${className}`}>
      {children}
    </label>
  );
}
