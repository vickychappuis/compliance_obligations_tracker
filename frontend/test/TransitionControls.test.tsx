import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { TransitionControls } from "@/components/obligations/TransitionControls";
import { dict } from "@/test/fixtures";

vi.mock("@/lib/actions/obligations", () => ({
  transitionAction: vi.fn(async () => ({})),
}));

describe("TransitionControls (document gate)", () => {
  it("disables submit and shows the hint when a required document is missing", () => {
    render(
      <TransitionControls
        id="ob-1"
        version={2}
        allowed={["submitted", "pending"]}
        requiresDocument
        hasDocument={false}
        dict={dict}
      />,
    );

    const submitButton = screen.getByRole("button", { name: dict.status.submitted });
    expect(submitButton).toBeDisabled();
    expect(screen.getByText(dict.detail.submitBlocked)).toBeInTheDocument();

    expect(screen.getByRole("button", { name: dict.status.pending })).toBeEnabled();
  });

  it("enables submit once a document is attached", () => {
    render(
      <TransitionControls
        id="ob-1"
        version={2}
        allowed={["submitted"]}
        requiresDocument
        hasDocument
        dict={dict}
      />,
    );

    expect(
      screen.getByRole("button", { name: dict.status.submitted }),
    ).toBeEnabled();
    expect(screen.queryByText(dict.detail.submitBlocked)).not.toBeInTheDocument();
  });
});
