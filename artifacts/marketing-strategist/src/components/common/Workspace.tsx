import { useState, type ReactNode } from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
export function Workspace({ children }: { children: ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  return <div className="min-h-[100dvh] bg-[#F8F9FA] text-[#17112B]">
    <Sidebar open={menuOpen} onClose={()=>setMenuOpen(false)}/>
    <div className="min-h-[100dvh] lg:pl-[248px]"><Navbar onOpenMenu={()=>setMenuOpen(true)}/><main className="mx-auto w-full max-w-[1400px] px-4 py-7 sm:px-8 sm:py-9">{children}</main></div>
  </div>;
}
