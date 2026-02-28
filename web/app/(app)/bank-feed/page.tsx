"use client";

import { useEffect, useState } from "react";

import Sidebar from "../../components/Sidebar";
import BusinessSwitcher from "../../components/BusinessSwitcher";
import PdfUpload from "../../components/PdfUpload";
import { getBankFeed } from "../../lib/api";

const DEFAULT_BUSINESS_ID = "11111111-1111-1111-1111-111111111111";

export default function BankFeedPage() {
  const [transactions, setTransactions] = useState<any[]>([]);

  useEffect(() => {
    getBankFeed(DEFAULT_BUSINESS_ID)
      .then((data) => setTransactions(data))
      .catch(() => setTransactions([]));
  }, []);

  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <header className="header">
          <div>
            <h1>Bank Feed</h1>
            <p className="muted">New and suggested transactions from statements.</p>
          </div>
          <BusinessSwitcher />
        </header>

        <PdfUpload />

        <div className="panel">
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((txn) => (
                <tr key={txn.id}>
                  <td>{txn.txn_date}</td>
                  <td>{txn.description_clean}</td>
                  <td>{txn.amount}</td>
                  <td>
                    <span className="badge">{txn.status}</span>
                  </td>
                </tr>
              ))}
              {transactions.length === 0 && (
                <tr>
                  <td colSpan={4} className="muted">
                    No transactions loaded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
