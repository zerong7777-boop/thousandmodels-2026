import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "./utils";

const badgeVariants = cva("inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium", {
  variants: {
    variant: {
      neutral: "bg-slate-100 text-slate-700",
      success: "bg-teal-50 text-harbor",
      warning: "bg-amber-50 text-amber-700",
      danger: "bg-red-50 text-signal",
      lotus: "bg-violet-50 text-lotus"
    }
  },
  defaultVariants: {
    variant: "neutral"
  }
});

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
