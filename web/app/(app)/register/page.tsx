"use client";

import { useEffect, useState } from "react";

import Sidebar from "../../components/Sidebar";
import BusinessSwitcher from "../../components/BusinessSwitcher";
import { getRegister } from "../../lib/api";

const DEFAULT_BUSINESS_ID = "11111111-1111-1111-1111-111111111111";

export default function RegisterPage() {
  const [transactions, setTransactions] = useState<any[]>([]);

  useEffect(() => {
    getRegister(DEFAULT_BUSINESS_ID)
      .then((data) => setTransactions(data))
      .catch(() => setTransactions([]));
  }, []);

  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <header className="header">
          <div>
            <h1>Register</h1>
            <p className="muted">Editable ledger with splits and classifications.</p>
          </div>
          <BusinessSwitcher />
        </header>

        <div className="panel">
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Payee</th>
                <th>Memo</th>
                <th>Lines</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((txn) => (
                <tr key={txn.id}>
                  <td>{txn.txn_date}</td>
                  <td>{txn.payee}</td>
                  <td>{txn.memo}</td>
                  <td>{txn.lines?.length ?? 0}</td>
                </tr>
              ))}
              {transactions.length === 0 && (
                <tr>
                  <td colSpan={4} className="muted">
                    No register entries yet.
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
