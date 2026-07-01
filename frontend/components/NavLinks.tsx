"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/cn";

export function NavLinks({
  dashboard,
  create,
}: {
  dashboard: string;
  create: string;
}) {
  const pathname = usePathname();
  const items = [
    { href: "/", label: dashboard },
    { href: "/obligations/new", label: create },
  ];
  return (
    <>
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "hover:text-slate-900",
              active ? "font-medium text-slate-900" : "text-slate-600",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </>
  );
}
