
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

import {
  getMonthlySales,
  getCountrySales,
  getTopProducts,
  getDateRangeSales,
} from "../services/api";

import "./SalesAnalytics.css";

const DEFAULT_START = "2009-12-01";
const DEFAULT_END = "2011-12-09";

const number = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const formatNumber = (value) =>
  number(value).toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  });

const formatRevenue = (value) => formatNumber(value);

const getErrorMessage = (error) =>
  error.response?.data?.detail ||
  error.message ||
  "Unable to load data.";

function SectionStatus({ loading, error, onRetry, children }) {
  if (loading) {
    return <p className="analytics-status">Loading data...</p>;
  }

  if (error) {
    return (
      <div className="analytics-error" role="alert">
        <p>{error}</p>
        <button type="button" onClick={onRetry}>
          Retry
        </button>
      </div>
    );
  }

  return children;
}

function DateMetric({ label, value }) {
  return (
    <article className="date-metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

export default function SalesAnalytics() {
  const [monthly, setMonthly] = useState([]);
  const [countries, setCountries] = useState([]);
  const [products, setProducts] = useState([]);

  const [monthlyState, setMonthlyState] = useState({
    loading: true,
    error: "",
  });

  const [countryState, setCountryState] = useState({
    loading: true,
    error: "",
  });

  const [productState, setProductState] = useState({
    loading: true,
    error: "",
  });

  const [startDate, setStartDate] = useState(DEFAULT_START);
  const [endDate, setEndDate] = useState(DEFAULT_END);

  const [appliedRange, setAppliedRange] = useState({
    startDate: DEFAULT_START,
    endDate: DEFAULT_END,
  });

  const [rangeSummary, setRangeSummary] = useState(null);
  const [rangeLoading, setRangeLoading] = useState(false);
  const [rangeError, setRangeError] = useState("");
  const [dateValidationError, setDateValidationError] = useState("");

  async function loadMonthly() {
    setMonthlyState({ loading: true, error: "" });

    try {
      const result = await getMonthlySales();

      setMonthly(
        (result.data || []).map((row) => ({
          ...row,
          month: String(row.month ?? ""),
          unique_invoices: number(row.unique_invoices),
          total_quantity: number(row.total_quantity),
          total_revenue: number(row.total_revenue),
        }))
      );

      setMonthlyState({ loading: false, error: "" });
    } catch (error) {
      setMonthlyState({
        loading: false,
        error: getErrorMessage(error),
      });
    }
  }

  async function loadCountries() {
    setCountryState({ loading: true, error: "" });

    try {
      const result = await getCountrySales();

      setCountries(
        (result.data || []).map((row) => ({
          ...row,
          country: String(row.country ?? "Unknown"),
          unique_invoices: number(row.unique_invoices),
          total_quantity: number(row.total_quantity),
          total_revenue: number(row.total_revenue),
        }))
      );

      setCountryState({ loading: false, error: "" });
    } catch (error) {
      setCountryState({
        loading: false,
        error: getErrorMessage(error),
      });
    }
  }

  async function loadProducts() {
    setProductState({ loading: true, error: "" });

    try {
      const result = await getTopProducts(10);

      setProducts(
        (result.data || []).map((row) => ({
          ...row,
          total_quantity: number(row.total_quantity),
          total_revenue: number(row.total_revenue),
        }))
      );

      setProductState({ loading: false, error: "" });
    } catch (error) {
      setProductState({
        loading: false,
        error: getErrorMessage(error),
      });
    }
  }

  async function loadDateRange(start, end) {
    setRangeLoading(true);
    setRangeError("");
    setDateValidationError("");

    try {
      const result = await getDateRangeSales(start, end);

      // Your API currently returns an "error" field for reversed dates.
      if (result.error) {
        setRangeSummary(null);
        setRangeError(result.error);
        return;
      }

      setRangeSummary(result);
      setAppliedRange({
        startDate: start,
        endDate: end,
      });
    } catch (error) {
      setRangeSummary(null);
      setRangeError(getErrorMessage(error));
    } finally {
      setRangeLoading(false);
    }
  }

  useEffect(() => {
    loadMonthly();
    loadCountries();
    loadProducts();
    loadDateRange(DEFAULT_START, DEFAULT_END);
  }, []);

  function handleApplyDateRange(event) {
    event.preventDefault();

    if (!startDate || !endDate) {
      setDateValidationError("Please select both dates.");
      return;
    }

    if (startDate > endDate) {
      setDateValidationError(
        "Start date must be on or before the end date."
      );
      return;
    }

    setDateValidationError("");
    loadDateRange(startDate, endDate);
  }

  function handleResetDateRange() {
    setStartDate(DEFAULT_START);
    setEndDate(DEFAULT_END);
    setDateValidationError("");
    loadDateRange(DEFAULT_START, DEFAULT_END);
  }

  return (
    <section className="sales-page">
      <header className="sales-heading">
        <div>
          <h1>Sales Analytics</h1>
          <p>
            Analyze revenue, country performance, and product sales.
          </p>
        </div>
      </header>

      {/* Date range controls and range-specific summary */}
      <article className="sales-panel date-filter-panel">
        <div className="date-filter-heading">
          <div>
            <h2>Date Range Analysis</h2>
            <p className="sales-panel-description">
              Select a period to calculate summary metrics from transactions.
            </p>
          </div>
        </div>

        <form
          className="date-filter-form"
          onSubmit={handleApplyDateRange}
        >
          <label>
            Start Date
            <input
              type="date"
              value={startDate}
              max={endDate || undefined}
              onChange={(event) => setStartDate(event.target.value)}
              required
            />
          </label>

          <label>
            End Date
            <input
              type="date"
              value={endDate}
              min={startDate || undefined}
              onChange={(event) => setEndDate(event.target.value)}
              required
            />
          </label>

          <button
            type="submit"
            className="date-apply-button"
            disabled={rangeLoading}
          >
            {rangeLoading ? "Applying..." : "Apply Filter"}
          </button>

          <button
            type="button"
            className="date-reset-button"
            onClick={handleResetDateRange}
            disabled={rangeLoading}
          >
            Reset
          </button>
        </form>

        {dateValidationError && (
          <p className="date-error" role="alert">
            {dateValidationError}
          </p>
        )}

        {rangeError && (
          <div className="analytics-error" role="alert">
            <p>{rangeError}</p>
            <button
              type="button"
              onClick={() =>
                loadDateRange(
                  appliedRange.startDate,
                  appliedRange.endDate
                )
              }
              disabled={rangeLoading}
            >
              Retry
            </button>
          </div>
        )}

        {rangeLoading && (
          <p className="analytics-status">
            Calculating metrics for the selected dates...
          </p>
        )}

        {!rangeLoading && rangeSummary && !rangeError && (
          <>
            <p className="date-range-caption">
              Summary for {rangeSummary.start_date} to{" "}
              {rangeSummary.end_date}, inclusive.
            </p>

            <div className="date-metrics-grid">
              <DateMetric
                label="Revenue"
                value={formatRevenue(rangeSummary.total_revenue)}
              />
              <DateMetric
                label="Orders"
                value={formatNumber(rangeSummary.unique_invoices)}
              />
              <DateMetric
                label="Average Order Value"
                value={formatRevenue(
                  rangeSummary.average_order_value
                )}
              />
              <DateMetric
                label="Quantity"
                value={formatNumber(rangeSummary.total_quantity)}
              />
              <DateMetric
                label="Customers"
                value={formatNumber(rangeSummary.unique_customers)}
              />
              <DateMetric
                label="Products"
                value={formatNumber(rangeSummary.unique_products)}
              />
            </div>
          </>
        )}
      </article>

      <p className="all-time-note">
        The charts and detailed tables below show all-time data.
        The date filter above applies to the summary metrics only.
      </p>

      {/* Monthly sales chart and table */}
      <article className="sales-panel">
        <h2>Monthly Revenue Trend</h2>
        <p className="sales-panel-description">
          Monthly orders, quantities, and revenue across all dates.
        </p>

        <SectionStatus {...monthlyState} onRetry={loadMonthly}>
          {monthly.length ? (
            <>
              <div className="sales-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={monthly}
                    margin={{ top: 12, right: 20, left: 12, bottom: 8 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />
                    <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                    <YAxis
                      tick={{ fontSize: 11 }}
                      tickFormatter={formatRevenue}
                      width={85}
                    />
                    <Tooltip
                      formatter={(value) => formatNumber(value)}
                      labelFormatter={(label) => `Month: ${label}`}
                    />
                    <Line
                      type="monotone"
                      dataKey="total_revenue"
                      name="Revenue"
                      stroke="#4f46e5"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="sales-table-wrapper">
                <table className="sales-table">
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>Orders</th>
                      <th>Quantity</th>
                      <th>Revenue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monthly.map((row) => (
                      <tr key={row.month}>
                        <td>{row.month}</td>
                        <td>{formatNumber(row.unique_invoices)}</td>
                        <td>{formatNumber(row.total_quantity)}</td>
                        <td>{formatRevenue(row.total_revenue)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <p className="sales-empty">No monthly sales data found.</p>
          )}
        </SectionStatus>
      </article>

      {/* Country chart and table */}
      <article className="sales-panel">
        <h2>Country Performance</h2>
        <p className="sales-panel-description">
          Revenue generated by each country across all dates.
        </p>

        <SectionStatus {...countryState} onRetry={loadCountries}>
          {countries.length ? (
            <>
              <div className="sales-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={countries.slice(0, 10)}
                    layout="vertical"
                    margin={{ top: 8, right: 20, left: 12, bottom: 8 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      horizontal={false}
                    />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 10 }}
                      tickFormatter={formatRevenue}
                    />
                    <YAxis
                      type="category"
                      dataKey="country"
                      width={120}
                      tick={{ fontSize: 10 }}
                    />
                    <Tooltip
                      formatter={(value) => formatNumber(value)}
                    />
                    <Bar
                      dataKey="total_revenue"
                      name="Revenue"
                      fill="#0d9488"
                      radius={[0, 4, 4, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="sales-table-wrapper">
                <table className="sales-table">
                  <thead>
                    <tr>
                      <th>Country</th>
                      <th>Orders</th>
                      <th>Quantity</th>
                      <th>Revenue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {countries.map((row) => (
                      <tr key={row.country}>
                        <td>{row.country}</td>
                        <td>{formatNumber(row.unique_invoices)}</td>
                        <td>{formatNumber(row.total_quantity)}</td>
                        <td>{formatRevenue(row.total_revenue)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <p className="sales-empty">No country data found.</p>
          )}
        </SectionStatus>
      </article>

      {/* Top products table */}
      <article className="sales-panel">
        <h2>Top 10 Products by Revenue</h2>
        <p className="sales-panel-description">
          Product revenue and quantity across all dates.
        </p>

        <SectionStatus {...productState} onRetry={loadProducts}>
          <div className="sales-table-wrapper">
            <table className="sales-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Stock Code</th>
                  <th>Description</th>
                  <th>Quantity</th>
                  <th>Revenue</th>
                </tr>
              </thead>
              <tbody>
                {products.map((row, index) => (
                  <tr key={row.stock_code}>
                    <td>{index + 1}</td>
                    <td>{row.stock_code}</td>
                    <td>{row.description || "No description"}</td>
                    <td>{formatNumber(row.total_quantity)}</td>
                    <td>{formatRevenue(row.total_revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {!products.length && (
            <p className="sales-empty">No product data found.</p>
          )}
        </SectionStatus>
      </article>
    </section>
  );
}
