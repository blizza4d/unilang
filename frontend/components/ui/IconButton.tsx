"use client";

import React, { forwardRef } from "react";
import { Loader2 } from "lucide-react";
import { ButtonVariant, ButtonSize } from "./Button";

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  "aria-label": string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  icon: React.ReactNode;
}

const SIZE_STYLES: Record<ButtonSize, string> = {
  sm: "w-7 h-7 text-xs rounded-sm p-1",
  md: "w-9 h-9 text-sm rounded-md p-2",
  lg: "w-11 h-11 text-base rounded-lg p-2.5",
};

const VARIANT_STYLES: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--text-bright)] text-[var(--bg-app)] hover:bg-[#eae6dd] active:scale-[0.96] shadow-sm",
  secondary:
    "bg-[var(--bg-elevated)] text-[var(--text-muted)] hover:text-[var(--text-bright)] hover:bg-[var(--bg-hover)] active:scale-[0.96] border border-[var(--border-subtle)] hover:border-[var(--border-strong)]",
  ghost:
    "bg-transparent text-[var(--text-muted)] hover:text-[var(--text-bright)] hover:bg-[var(--bg-hover)] active:scale-[0.96]",
  danger:
    "bg-[var(--accent-red)]/10 text-[var(--accent-red)] hover:bg-[var(--accent-red)]/20 active:scale-[0.96] border border-[var(--accent-red)]/30",
};

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      "aria-label": ariaLabel,
      variant = "ghost",
      size = "md",
      isLoading = false,
      icon,
      className = "",
      disabled,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || isLoading;

    return (
      <button
        ref={ref}
        aria-label={ariaLabel}
        title={ariaLabel}
        disabled={isDisabled}
        className={`inline-flex items-center justify-center select-none transition-all duration-150 outline-none focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] disabled:opacity-40 disabled:pointer-events-none ${VARIANT_STYLES[variant]} ${SIZE_STYLES[size]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin text-current" />
        ) : (
          icon
        )}
      </button>
    );
  }
);

IconButton.displayName = "IconButton";
