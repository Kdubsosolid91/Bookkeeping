import Link from "next/link";

import Sidebar from "./components/Sidebar";
import BusinessSwitcher from "./components/BusinessSwitcher";

export default function Home() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <header className="header">
          <div>
            <h1>Bookkeeping Command Center</h1>
            <p className="muted">Multi-business ledger with bank feed, register, and reconciliation.</p>
          </div>
          <BusinessSwitcher />
        </header>

        <section className="grid grid-3">
          <div className="panel">
            <div className="card-title">Bank Feed Inbox</div>
            <p className="muted">Review new statements, match and post to the register.</p>
            <Link className="button" href="/bank-feed">
              Open Bank Feed
            </Link>
          </div>
          <div className="panel">
            <div className="card-title">Register</div>
            <p className="muted">Edit transactions, splits, and bookkeeping lines.</p>
            <Link className="button" href="/register">
              Open Register
            </Link>
          </div>
          <div className="panel">
            <div className="card-title">Reconciliation</div>
            <p className="muted">Close statement periods and lock cleared activity.</p>
            <Link className="button" href="/reconciliation">
              Reconcile
            </Link>
          </div>
        </section>

        <section className="grid grid-2" style={{ marginTop: "22px" }}>
          <div className="panel">
            <div className="card-title">Reports</div>
            <p className="muted">P&L, balance sheet, and drilldowns for any period.</p>
            <Link className="button secondary" href="/reports">
              View Reports
            </Link>
          </div>
          <div className="panel">
            <div className="card-title">Rules &amp; Suggestions</div>
            <p className="muted">Create rules and manage merchant normalization.</p>
            <Link className="button secondary" href="/rules">
              Manage Rules
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
