
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  ChartNoAxesCombined,
  Users,
  Package,
  Menu,
  X,
  Store,
  LogOut,
  LockKeyhole,
} from "lucide-react";

import Overview from "./pages/Overview";
import SalesAnalytics from "./pages/SalesAnalytics";
import Customers from "./pages/Customers";
import Products from "./pages/Products";
import {
  login,
  logout,
  getAccessToken,
  getCurrentUser,
} from "./services/api";

import "./App.css";

const navigationItems = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "sales", label: "Sales Analytics", icon: ChartNoAxesCombined },
  { id: "customers", label: "Customer Analytics", icon: Users },
  { id: "products", label: "Product Management", icon: Package },
];

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const user = await onLogin(username.trim(), password);
      if (!user) {
        setError("Unable to sign in. Please try again.");
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Login failed. Check your username, password, and API connection."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={styles.loginPage}>
      <form onSubmit={handleSubmit} style={styles.loginCard}>
        <div style={styles.loginIcon}>
          <Store size={30} />
        </div>

        <h1 style={styles.loginTitle}>Retail Analytics</h1>
        <p style={styles.loginSubtitle}>
          Sign in to access your business intelligence dashboard.
        </p>

        <label htmlFor="username" style={styles.label}>
          Username
        </label>
        <input
          id="username"
          type="text"
          autoComplete="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="Enter your username"
          required
          style={styles.input}
        />

        <label htmlFor="password" style={styles.label}>
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter your password"
          required
          style={styles.input}
        />

        {error && (
          <div role="alert" style={styles.error}>
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          style={{
            ...styles.loginButton,
            opacity: submitting ? 0.7 : 1,
          }}
        >
          <LockKeyhole size={18} />
          {submitting ? "Signing in..." : "Sign in"}
        </button>

        <p style={styles.loginFooter}>
          Authorized users only
        </p>
      </form>
    </div>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState("overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  // Validate any existing token when the app opens or reloads.
  useEffect(() => {
    let active = true;

    const handleUnauthorized = () => {
      setUser(null);
      setSidebarOpen(false);
    };

    window.addEventListener(
      "auth:unauthorized",
      handleUnauthorized
    );

    async function checkSession() {
      if (!getAccessToken()) {
        if (active) setCheckingSession(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();

        if (active) {
          setUser(currentUser);
        }
      } catch {
        logout();

        if (active) {
          setUser(null);
        }
      } finally {
        if (active) {
          setCheckingSession(false);
        }
      }
    }

    checkSession();

    return () => {
      active = false;
      window.removeEventListener(
        "auth:unauthorized",
        handleUnauthorized
      );
    };
  }, []);

  async function handleLogin(username, password) {
    const loggedInUser = await login(username, password);

    // Confirm the token works before showing the dashboard.
    const currentUser = await getCurrentUser();

    setUser(currentUser || loggedInUser);
    setActivePage("overview");

    return currentUser || loggedInUser;
  }

  function handleLogout() {
    logout();
    setUser(null);
    setSidebarOpen(false);
    setActivePage("overview");
  }

  function navigateTo(page) {
    setActivePage(page);
    setSidebarOpen(false);
  }

  function renderPage() {
    switch (activePage) {
      case "overview":
        return <Overview />;
      case "sales":
        return <SalesAnalytics />;
      case "customers":
        return <Customers />;
      case "products":
        return <Products />;
      default:
        return <Overview />;
    }
  }

  const activeLabel =
    navigationItems.find((item) => item.id === activePage)?.label ||
    "Overview";

  if (checkingSession) {
    return (
      <div style={styles.loadingPage}>
        Checking your session...
      </div>
    );
  }

  if (!user) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="app-layout">
      {sidebarOpen && (
        <button
          type="button"
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`app-sidebar ${
          sidebarOpen ? "sidebar-open" : ""
        }`}
      >
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Store size={25} />
          </div>

          <div className="brand-text">
            <h2>Retail Analytics</h2>
            <p>Business Intelligence</p>
          </div>

          <button
            type="button"
            className="sidebar-close"
            aria-label="Close sidebar"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-section-label">WORKSPACE</div>

        <nav className="sidebar-navigation">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;

            return (
              <button
                key={item.id}
                type="button"
                className={`nav-item ${isActive ? "active" : ""}`}
                onClick={() => navigateTo(item.id)}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon size={20} strokeWidth={1.8} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>Retail Analytics Platform</span>
        </div>
      </aside>

      <main className="app-main">
        <header className="app-topbar">
          <button
            type="button"
            className="mobile-menu-button"
            aria-label="Open navigation"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={23} />
          </button>

          <div className="breadcrumb">
            <span>Retail Analytics</span>
            <span className="breadcrumb-separator">/</span>
            <strong>{activeLabel}</strong>
          </div>

          <div style={styles.userArea}>
            <div style={styles.userInfo}>
              <span style={styles.username}>
                {user.username}
              </span>
              <span style={styles.role}>
                {user.role}
              </span>
            </div>

            <button
              type="button"
              onClick={handleLogout}
              style={styles.logoutButton}
              title="Sign out"
              aria-label="Sign out"
            >
              <LogOut size={17} />
              <span>Logout</span>
            </button>
          </div>
        </header>

        <div className="app-content" key={activePage}>
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

const styles = {
  loginPage: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "24px",
    background: "#f3f6fb",
    fontFamily: "Inter, system-ui, sans-serif",
  },
  loginCard: {
    width: "100%",
    maxWidth: "420px",
    boxSizing: "border-box",
    padding: "36px",
    background: "#ffffff",
    border: "1px solid #e3e8ef",
    borderRadius: "16px",
    boxShadow: "0 16px 48px rgba(15, 23, 42, 0.08)",
    display: "flex",
    flexDirection: "column",
  },
  loginIcon: {
    width: "56px",
    height: "56px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: "14px",
    background: "#eaf1ff",
    color: "#2855b7",
    marginBottom: "20px",
  },
  loginTitle: {
    margin: "0 0 8px",
    fontSize: "26px",
    color: "#172033",
  },
  loginSubtitle: {
    margin: "0 0 26px",
    color: "#64748b",
    lineHeight: 1.5,
  },
  label: {
    marginBottom: "8px",
    fontSize: "14px",
    fontWeight: 600,
    color: "#334155",
  },
  input: {
    width: "100%",
    boxSizing: "border-box",
    padding: "12px 14px",
    marginBottom: "18px",
    border: "1px solid #cbd5e1",
    borderRadius: "8px",
    fontSize: "15px",
    outlineOffset: "2px",
  },
  error: {
    padding: "10px 12px",
    marginBottom: "16px",
    background: "#fef2f2",
    border: "1px solid #fecaca",
    borderRadius: "8px",
    color: "#b91c1c",
    fontSize: "14px",
  },
  loginButton: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    gap: "10px",
    width: "100%",
    padding: "13px",
    border: "none",
    borderRadius: "8px",
    background: "#2855b7",
    color: "#ffffff",
    fontWeight: 600,
    fontSize: "15px",
    cursor: "pointer",
  },
  loginFooter: {
    margin: "20px 0 0",
    textAlign: "center",
    color: "#64748b",
    fontSize: "12px",
  },
  loadingPage: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "Inter, system-ui, sans-serif",
    color: "#475569",
  },
  userArea: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
    marginLeft: "auto",
  },
  userInfo: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-end",
    gap: "3px",
  },
  username: {
    color: "#1e293b",
    fontSize: "13px",
    fontWeight: 600,
  },
  role: {
    color: "#64748b",
    fontSize: "11px",
    textTransform: "capitalize",
  },
  logoutButton: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    padding: "8px 10px",
    border: "1px solid #dbe2ea",
    borderRadius: "8px",
    background: "#ffffff",
    color: "#334155",
    cursor: "pointer",
  },
};
