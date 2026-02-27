import Sidebar from "../../components/Sidebar";
import BusinessSwitcher from "../../components/BusinessSwitcher";
import SeedButton from "../../components/SeedButton";

export default function SettingsPage() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <header className="header">
          <div>
            <h1>Settings</h1>
            <p className="muted">Workspace and business configuration.</p>
          </div>
          <BusinessSwitcher />
        </header>

        <div className="grid grid-2">
          <div className="panel">
            <div className="card-title">Businesses</div>
            <p className="muted">Create or edit businesses.</p>
            <button className="button">Add Business</button>
          </div>
          <div className="panel">
            <div className="card-title">Bank Accounts</div>
            <p className="muted">Manage bank connections and statement uploads.</p>
            <button className="button secondary">Add Bank Account</button>
          </div>
        </div>

        <div className="panel" style={{ marginTop: "16px" }}>
          <div className="card-title">Demo Data</div>
          <p className="muted">Seed a demo workspace, business, and sample transactions.</p>
          <SeedButton />
        </div>
      </main>
    </div>
  );
}
