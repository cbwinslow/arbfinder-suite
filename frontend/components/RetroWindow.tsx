"use client";

import { ReactNode } from "react";

interface RetroWindowProps {
  title: string;
  children: ReactNode;
  icon?: string;
  className?: string;
  onClose?: () => void;
  onMinimize?: () => void;
  onMaximize?: () => void;
}

export default function RetroWindow({
  title,
  children,
  icon,
  className = "",
  onClose,
  onMinimize,
  onMaximize,
}: RetroWindowProps) {
  return (
    <div
      className={`
        bg-[#c0c0c0] 
        border-2 
        border-t-white 
        border-l-white 
        border-r-[#808080] 
        border-b-[#808080]
        shadow-[2px_2px_0_rgba(0,0,0,0.3)]
        ${className}
      `}
    >
      {/* Title Bar */}
      <div
        className="
          bg-gradient-to-r from-[#000080] to-[#1084d0]
          px-1 py-0.5
          flex items-center justify-between
          border-b-2 border-[#808080]
        "
      >
        <div className="flex items-center gap-2">
          {icon && <span className="text-sm">{icon}</span>}
          <span className="text-white text-sm font-bold tracking-wide">
            {title}
          </span>
        </div>
        <div className="flex gap-0.5">
          {onMinimize && (
            <button
              onClick={onMinimize}
              className="
                w-4 h-4 
                bg-[#c0c0c0] 
                border border-white border-b-black border-r-black
                flex items-center justify-center
                hover:bg-[#d0d0d0]
                active:border-black active:border-t-black active:border-l-black
              "
              aria-label="Minimize"
            >
              <span className="text-[10px] font-bold text-black">_</span>
            </button>
          )}
          {onMaximize && (
            <button
              onClick={onMaximize}
              className="
                w-4 h-4 
                bg-[#c0c0c0] 
                border border-white border-b-black border-r-black
                flex items-center justify-center
                hover:bg-[#d0d0d0]
                active:border-black active:border-t-black active:border-l-black
              "
              aria-label="Maximize"
            >
              <span className="text-[10px] font-bold text-black">□</span>
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="
                w-4 h-4 
                bg-[#c0c0c0] 
                border border-white border-b-black border-r-black
                flex items-center justify-center
                hover:bg-[#d0d0d0]
                active:border-black active:border-t-black active:border-l-black
              "
              aria-label="Close"
            >
              <span className="text-[10px] font-bold text-black">×</span>
            </button>
          )}
        </div>
      </div>

      {/* Window Content */}
      <div className="bg-white">{children}</div>
    </div>
  );
}
