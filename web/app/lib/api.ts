const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function getBusinesses(): Promise<{ id: string; name: string }[]> {
  const workspaceId = "00000000-0000-0000-0000-000000000000";
  return fetchJSON(`/api/businesses?workspace_id=${workspaceId}`);
}

export async function getBankAccounts(businessId: string): Promise<{ id: string; name: string }[]> {
  return fetchJSON(`/api/businesses/${businessId}/bank-accounts`);
}

export async function getBankFeed(businessId: string): Promise<any[]> {
  return fetchJSON(`/api/businesses/${businessId}/bank-transactions?limit=50&offset=0`);
}

export async function getRegister(businessId: string): Promise<any[]> {
  return fetchJSON(`/api/businesses/${businessId}/register?limit=50&offset=0`);
}

export async function uploadPdf(
  bankAccountId: string,
  businessId: string,
  file: File
): Promise<{ id: string }> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(
    `${API_BASE}/api/bank-accounts/${bankAccountId}/uploads?business_id=${businessId}`,
    {
      method: "POST",
      body: form,
    }
  );

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.status}`);
  }

  return res.json();
}

export async function parseUpload(uploadId: string): Promise<void> {
  await fetchJSON(`/api/uploads/${uploadId}/parse`, { method: "POST" });
}
