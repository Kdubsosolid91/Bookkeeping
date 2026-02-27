const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function getBusinesses(): Promise<{ id: string; name: string }[]> {
  // Seeded default workspace
  const workspaceId = "00000000-0000-0000-0000-000000000000";
  return fetchJSON(`/api/businesses?workspace_id=${workspaceId}`);
}

export async function getBankFeed(businessId: string): Promise<any[]> {
  return fetchJSON(`/api/businesses/${businessId}/bank-transactions?limit=50&offset=0`);
}

export async function getRegister(businessId: string): Promise<any[]> {
  return fetchJSON(`/api/businesses/${businessId}/register?limit=50&offset=0`);
}
