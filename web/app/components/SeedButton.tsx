"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function SeedButton() {
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function runSeed() {
    setLoading(true);
    setStatus("");
    try {
      const res = await fetch(`${API_BASE}/api/seed`, { method: "POST" });
      if (!res.ok) {
        throw new Error(`Seed failed: ${res.status}`);
      }
      const data = await res.json();
      setStatus(`Seeded business ${data.business_id}`);
    } catch (err: any) {
      setStatus(err.message ?? "Seed failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid" style={{ gap: "10px" }}>
      <button className="button" onClick={runSeed} disabled={loading}>
        {loading ? "Seeding..." : "Seed Demo Data"}
      </button>
      {status ? <span className="muted">{status}</span> : null}
    </div>
  );
}
