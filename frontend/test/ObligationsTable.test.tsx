import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ObligationsTable } from "@/components/obligations/ObligationsTable";
import { dict, makeObligation } from "@/test/fixtures";

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
  it("shows the empty state when there are no items", () => {
    render(<ObligationsTable items={[]} dict={dict} locale="en" />);
    expect(screen.getByText(dict.list.empty)).toBeInTheDocument();
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
