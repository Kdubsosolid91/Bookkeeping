import Sidebar from "../../components/Sidebar";
import BusinessSwitcher from "../../components/BusinessSwitcher";

export default function RulesPage() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <header className="header">
          <div>
            <h1>Rules</h1>
            <p className="muted">Automate merchant normalization and categorization.</p>
          </div>
          <BusinessSwitcher />
        </header>

        <div className="panel">
          <div className="card-title">Rules List</div>
          <p className="muted">Create rules from bank feed selections.</p>
          <button className="button">Create Rule</button>
        </div>
      </main>
    </div>
  );
}
