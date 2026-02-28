"use client";

import { useEffect, useState } from "react";

import { getBankAccounts, uploadPdf, parseUpload } from "../lib/api";

const DEFAULT_BUSINESS_ID = "11111111-1111-1111-1111-111111111111";

export default function PdfUpload() {
  const [bankAccounts, setBankAccounts] = useState<{ id: string; name: string }[]>([]);
  const [bankAccountId, setBankAccountId] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getBankAccounts(DEFAULT_BUSINESS_ID)
      .then((data) => {
        setBankAccounts(data);
        if (data.length) setBankAccountId(data[0].id);
      })
      .catch(() => setBankAccounts([]));
  }, []);

  async function handleUpload() {
    if (!bankAccountId || !file) {
      setStatus("Select a bank account and a PDF.");
      return;
    }

    setLoading(true);
    setStatus("");
    try {
      const upload = await uploadPdf(bankAccountId, DEFAULT_BUSINESS_ID, file);
      setStatus("Uploaded. Parsing...");
      await parseUpload(upload.id);
      setStatus("Parsed successfully. Refresh Bank Feed.");
    } catch (err: any) {
      setStatus(err.message ?? "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel" style={{ marginBottom: "16px" }}>
      <div className="card-title">Upload Statement PDF</div>
      <p className="muted">Upload bank statements to populate the bank feed.</p>
      <div className="grid" style={{ gap: "10px", maxWidth: "420px" }}>
        <select
          className="input"
          value={bankAccountId}
          onChange={(event) => setBankAccountId(event.target.value)}
        >
          <option value="">Select bank account</option>
          {bankAccounts.map((acct) => (
            <option key={acct.id} value={acct.id}>
              {acct.name}
            </option>
          ))}
        </select>
        <input
          className="input"
          type="file"
          accept="application/pdf"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <button className="button" onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload & Parse"}
        </button>
        {status ? <span className="muted">{status}</span> : null}
      </div>
    </div>
  );
}
