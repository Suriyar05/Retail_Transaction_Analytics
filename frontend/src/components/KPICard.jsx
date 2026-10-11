import "./KPICard.css";

export default function KPICard({ title, value, subtitle }) {
  return (
    <div className="kpi-card">
      <p className="kpi-title">{title}</p>
      <h2 className="kpi-value">{value}</h2>
      {subtitle && <p className="kpi-subtitle">{subtitle}</p>}
    </div>
  );
}