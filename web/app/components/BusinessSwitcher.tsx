"use client";

import { useEffect, useState } from "react";

import { getBusinesses } from "../lib/api";

export default function BusinessSwitcher() {
  const [businesses, setBusinesses] = useState<{ id: string; name: string }[]>([]);
  const [selected, setSelected] = useState<string>("all");

  useEffect(() => {
    getBusinesses()
      .then((data) => setBusinesses(data))
      .catch(() => setBusinesses([]));
  }, []);

  return (
    <label className="grid" style={{ gap: "6px" }}>
      <span className="muted">Business</span>
      <select
        className="input"
        value={selected}
        onChange={(event) => setSelected(event.target.value)}
      >
        <option value="all">All</option>
        {businesses.map((biz) => (
          <option key={biz.id} value={biz.id}>
            {biz.name}
          </option>
        ))}
      </select>
    </label>
  );
}
