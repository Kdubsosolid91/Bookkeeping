import Link from "next/link";

const navItems = [
  { href: "/bank-feed", label: "Bank Feed" },
  { href: "/register", label: "Register" },
  { href: "/reconciliation", label: "Reconciliation" },
  { href: "/reports", label: "Reports" },
  { href: "/rules", label: "Rules" },
  { href: "/settings", label: "Settings" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="logo">Ledgerlane</div>
      <div className="muted">Workspace</div>
      <nav className="nav">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href}>
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
