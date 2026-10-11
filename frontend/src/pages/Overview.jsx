import { useEffect, useState } from "react";
import { getSummary } from "../services/api";
import KPICard from "../components/KPICard";

export default function Overview() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getSummary()
      .then(setSummary)
      .catch(() => {
        setError(
          "Unable to load analytics. Check that FastAPI is running."
        );
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading analytics...</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!summary) return <p>No analytics data available.</p>;

  const money = (value) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }).format(value);

  return (
    <section>
      <div className="page-heading">
        <div>
          <h1>Business Overview</h1>
          <p>Retail transaction performance at a glance</p>
        </div>
      </div>

      <div className="kpi-grid">
        <KPICard
          title="Total Revenue"
          value={money(summary.total_revenue)}
        />
        <KPICard
          title="Total Orders"
          value={summary.unique_invoices.toLocaleString("en-IN")}
        />
        <KPICard
          title="Average Order Value"
          value={money(summary.average_order_value)}
        />
        <KPICard
          title="Total Quantity"
          value={summary.total_quantity.toLocaleString("en-IN")}
        />
        <KPICard
          title="Customers"
          value={summary.unique_customers.toLocaleString("en-IN")}
        />
        <KPICard
          title="Products"
          value={summary.unique_products.toLocaleString("en-IN")}
        />
      </div>
    </section>
  );
}