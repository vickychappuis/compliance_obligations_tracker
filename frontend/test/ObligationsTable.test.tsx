import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ObligationsTable } from "@/components/obligations/ObligationsTable";
import { dict, makeObligation } from "@/test/fixtures";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe("ObligationsTable", () => {
  it("shows the empty-system state with a create CTA when unfiltered", () => {
    render(<ObligationsTable items={[]} dict={dict} locale="en" />);
    expect(screen.getByText(dict.list.emptyAll)).toBeInTheDocument();
    expect(screen.getByText(dict.list.createFirst)).toBeInTheDocument();
  });

  it("shows the no-match state without a CTA when filtered", () => {
    render(<ObligationsTable items={[]} dict={dict} locale="en" filtered />);
    expect(screen.getByText(dict.list.empty)).toBeInTheDocument();
    expect(screen.queryByText(dict.list.createFirst)).not.toBeInTheDocument();
  });

  it("renders rows and highlights overdue items", () => {
    const items = [
      makeObligation({ id: "a", title: "On time", overdue: false }),
      makeObligation({ id: "b", title: "Late one", overdue: true }),
    ];
    render(<ObligationsTable items={items} dict={dict} locale="en" />);

    expect(screen.getByText("On time")).toBeInTheDocument();
    const lateRow = screen.getByText("Late one").closest("tr");
    expect(lateRow).toHaveClass("bg-red-50");
    expect(screen.getByText(dict.list.overdueBadge)).toBeInTheDocument();
  });
});
