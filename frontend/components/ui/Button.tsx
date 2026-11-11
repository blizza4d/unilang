"use client";

import React, { forwardRef } from "react";
import { Loader2 } from "lucide-react";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const VARIANT_STYLES: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--text-bright)] text-[var(--bg-app)] hover:bg-[#eae6dd] active:scale-[0.98] shadow-sm font-semibold border border-transparent",
  secondary:
    "bg-[var(--bg-elevated)] text-[var(--text-bright)] hover:bg-[var(--bg-hover)] active:scale-[0.98] border border-[var(--border-subtle)] hover:border-[var(--border-strong)]",
  ghost:
    "bg-transparent text-[var(--text-muted)] hover:text-[var(--text-bright)] hover:bg-[var(--bg-hover)] active:scale-[0.98] border border-transparent",
  danger:
    "bg-[var(--accent-red)]/10 text-[var(--accent-red)] hover:bg-[var(--accent-red)]/20 active:scale-[0.98] border border-[var(--accent-red)]/30",
};

const SIZE_STYLES: Record<ButtonSize, string> = {
  sm: "h-7 px-2.5 text-xs rounded-sm gap-1.5",
  md: "h-9 px-3.5 text-xs font-medium rounded-md gap-2",
  lg: "h-11 px-5 text-sm font-medium rounded-lg gap-2.5",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "secondary",
      size = "md",
      isLoading = false,
      leftIcon,
      rightIcon,
      children,
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
        disabled={isDisabled}
        className={`inline-flex items-center justify-center select-none transition-all duration-150 outline-none focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] disabled:opacity-40 disabled:pointer-events-none ${VARIANT_STYLES[variant]} ${SIZE_STYLES[size]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin shrink-0 text-current" />
        ) : (
          leftIcon
        )}
        <span>{children}</span>
        {!isLoading && rightIcon}
      </button>
    );
  }
);

Button.displayName = "Button";
