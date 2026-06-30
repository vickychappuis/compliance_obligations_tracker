"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import {
  ApiError,
  attachDocument,
  createObligation,
  deleteDocument,
  patchObligation,
  transitionObligation,
  type ObligationInput,
} from "@/lib/api";
import type { ObligationType, Status } from "@/lib/types";

export interface ActionState {
  error?: string;
}

function message(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return "Something went wrong.";
}

function parseInput(formData: FormData): ObligationInput | { error: string } {
  const title = String(formData.get("title") ?? "").trim();
  const owner = String(formData.get("owner") ?? "").trim();
  const company_tax_id = String(formData.get("company_tax_id") ?? "").trim();
  const due_date = String(formData.get("due_date") ?? "").trim();
  const type = String(formData.get("type") ?? "").trim() as ObligationType;

  if (!title || !owner || !company_tax_id || !due_date || !type) {
    return { error: "Please complete all required fields." };
  }

  return {
    type,
    title,
    description: String(formData.get("description") ?? "").trim(),
    due_date,
    owner,
    requires_document: formData.get("requires_document") === "on",
    company_tax_id,
  };
}

export async function createObligationAction(
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const parsed = parseInput(formData);
  if ("error" in parsed) return parsed;

  let id: string;
  try {
    const created = await createObligation(parsed);
    id = created.id;
  } catch (error) {
    return { error: message(error) };
  }

  revalidatePath("/");
  redirect(`/obligations/${id}`);
}

function parseUpdate(
  formData: FormData,
): Omit<ObligationInput, "company_tax_id"> | { error: string } {
  const title = String(formData.get("title") ?? "").trim();
  const owner = String(formData.get("owner") ?? "").trim();
  const due_date = String(formData.get("due_date") ?? "").trim();
  const type = String(formData.get("type") ?? "").trim() as ObligationType;

  if (!title || !owner || !due_date || !type) {
    return { error: "Please complete all required fields." };
  }

  return {
    type,
    title,
    description: String(formData.get("description") ?? "").trim(),
    due_date,
    owner,
    requires_document: formData.get("requires_document") === "on",
  };
}

export async function updateObligationAction(
  id: string,
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const parsed = parseUpdate(formData);
  if ("error" in parsed) return parsed;

  try {
    await patchObligation(id, parsed);
  } catch (error) {
    return { error: message(error) };
  }

  revalidatePath("/");
  revalidatePath(`/obligations/${id}`);
  redirect(`/obligations/${id}`);
}

export async function transitionAction(
  id: string,
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const targetStatus = String(formData.get("target_status") ?? "") as Status;
  const expectedVersion = Number(formData.get("expected_version"));

  if (!targetStatus || Number.isNaN(expectedVersion)) {
    return { error: "Invalid transition request." };
  }

  try {
    await transitionObligation(id, targetStatus, expectedVersion);
  } catch (error) {
    return { error: message(error) };
  }

  revalidatePath("/");
  revalidatePath(`/obligations/${id}`);
  return {};
}

export async function attachDocumentAction(
  id: string,
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const file = formData.get("file");
  if (!(file instanceof File) || file.size === 0) {
    return { error: "Please choose a file to upload." };
  }

  try {
    await attachDocument(id, file);
  } catch (error) {
    return { error: message(error) };
  }

  revalidatePath(`/obligations/${id}`);
  return {};
}

export async function removeDocumentAction(
  id: string,
  documentId: string,
  _prev: ActionState,
  _formData: FormData,
): Promise<ActionState> {
  try {
    await deleteDocument(id, documentId);
  } catch (error) {
    return { error: message(error) };
  }

  revalidatePath(`/obligations/${id}`);
  return {};
}
