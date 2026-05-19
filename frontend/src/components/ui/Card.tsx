import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className = "" }: CardProps) {
  return <div className={`glass rounded-2xl p-5 shadow-lg ${className}`}>{children}</div>;
}
