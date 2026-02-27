import Sidebar from "../../components/Sidebar";
import BusinessSwitcher from "../../components/BusinessSwitcher";

export default function ReconciliationPage() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <header className="header">
          <div>
            <h1>Reconciliation</h1>
            <p className="muted">Close statement periods and lock cleared items.</p>
          </div>
          <BusinessSwitcher />
        </header>

        <div className="grid grid-2">
          <div className="panel">
            <div className="card-title">Active Session</div>
            <p className="muted">Start or resume a reconciliation by bank account and period.</p>
            <button className="button">Start Session</button>
          </div>
          <div className="panel">
            <div className="card-title">Summary</div>
            <p className="muted">Beginning balance, ending balance, and cleared totals.</p>
            <div className="grid" style={{ gap: "8px" }}>
              <div className="badge">Beginning: $0.00</div>
              <div className="badge">Ending: $0.00</div>
              <div className="badge">Difference: $0.00</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
