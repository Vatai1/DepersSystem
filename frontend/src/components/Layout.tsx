import { NavLink, Outlet } from "react-router-dom";
import { FileText, Upload, History, Shield } from "lucide-react";
import "./Layout.css";

const links = [
  { to: "/", label: "Текст", icon: FileText },
  { to: "/files", label: "Файлы", icon: Upload },
  { to: "/history", label: "История", icon: History },
];

export default function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <Shield size={24} />
          <span>DepersSys</span>
        </div>
        <nav className="sidebar-nav">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
