import type { ReactNode } from 'react';
export function Card({ children, className = '', as: Element = 'section' }: { children: ReactNode; className?: string; as?: 'section' | 'article' | 'div' }) {
  return <Element className={`surface rounded-2xl p-5 sm:p-6 ${className}`}>{children}</Element>;
}
