import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { TransitionControls } from "@/components/obligations/TransitionControls";
import { dict } from "@/test/fixtures";

vi.mock("@/lib/actions/obligations", () => ({
  transitionAction: vi.fn(async () => ({})),
}));

describe("TransitionControls (document gate)", () => {
  it("disables submit and shows the hint when the backend gate is not satisfied", () => {
    render(
      <TransitionControls
        id="ob-1"
        status="in_progress"
        version={2}
        allowed={["submitted", "pending"]}
        canSubmit={false}
        dict={dict}
      />,
    );

    const submitButton = screen.getByRole("button", {
      name: dict.transition.to_submitted,
    });
    expect(submitButton).toBeDisabled();
    expect(screen.getByText(dict.detail.submitBlocked)).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: dict.transition.back_to_pending }),
    ).toBeEnabled();
  });

  it("enables submit when the backend reports the gate satisfied", () => {
    render(
      <TransitionControls
        id="ob-1"
        status="in_progress"
        version={2}
        allowed={["submitted"]}
        canSubmit
        dict={dict}
      />,
    );

    expect(
      screen.getByRole("button", { name: dict.transition.to_submitted }),
    ).toBeEnabled();
    expect(screen.queryByText(dict.detail.submitBlocked)).not.toBeInTheDocument();
  });
});
