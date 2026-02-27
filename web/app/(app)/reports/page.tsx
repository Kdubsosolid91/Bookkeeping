import Sidebar from "../../components/Sidebar";
import BusinessSwitcher from "../../components/BusinessSwitcher";

export default function ReportsPage() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <header className="header">
          <div>
            <h1>Reports</h1>
            <p className="muted">Profit & Loss and Balance Sheet.</p>
          </div>
          <BusinessSwitcher />
        </header>

        <div className="grid grid-2">
          <div className="panel">
            <div className="card-title">P&amp;L</div>
            <p className="muted">Select a period to view performance.</p>
            <button className="button secondary">Run P&amp;L</button>
          </div>
          <div className="panel">
            <div className="card-title">Balance Sheet</div>
            <p className="muted">View assets, liabilities, and equity as of a date.</p>
            <button className="button secondary">Run Balance Sheet</button>
          </div>
        </div>
      </main>
    </div>
  );
}
