import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ObligationForm } from "@/components/obligations/ObligationForm";
import type { ActionState } from "@/lib/actions/obligations";
import { dict } from "@/test/fixtures";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));

async function fillRequiredFields() {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(dict.form.title), "Delaware Annual Report");
  await user.type(screen.getByLabelText(dict.form.owner), "Jane Founder");
  fireEvent.change(screen.getByLabelText(dict.form.dueDate), {
    target: { value: "2026-03-01" },
  });
  await user.type(screen.getByLabelText(dict.form.companyTaxId), "123456789");
}

describe("ObligationForm (create flow)", () => {
  it("submits the entered values through the action", async () => {
    const user = userEvent.setup();
    const action = vi.fn(async (_p: ActionState, _f: FormData): Promise<ActionState> => ({}));
    render(
      <ObligationForm
        dict={dict}
        action={action}
        submitLabel={dict.form.create}
        includeTaxId
        cancelHref="/"
      />,
    );

    await fillRequiredFields();
    await user.click(screen.getByRole("button", { name: dict.form.create }));

    expect(action).toHaveBeenCalledTimes(1);
    const formData = action.mock.calls[0][1] as FormData;
    expect(formData.get("title")).toBe("Delaware Annual Report");
    expect(formData.get("company_tax_id")).toBe("123456789");
  });

  it("surfaces an error returned by the action", async () => {
    const user = userEvent.setup();
    const action = vi.fn(
      async (_p: ActionState, _f: FormData): Promise<ActionState> => ({ error: "Server says no" }),
    );
    render(
      <ObligationForm
        dict={dict}
        action={action}
        submitLabel={dict.form.create}
        includeTaxId
        cancelHref="/"
      />,
    );

    await fillRequiredFields();
    await user.click(screen.getByRole("button", { name: dict.form.create }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Server says no");
  });
});
