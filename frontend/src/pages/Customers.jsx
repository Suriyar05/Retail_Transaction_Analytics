
import { useEffect, useState } from "react";
import {
  getCustomers,
  getCustomer,
} from "../services/api";

import "./Customers.css";

const formatNumber = (value) =>
  Number(value || 0).toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  });

const formatRevenue = (value) => formatNumber(value);

function getError(error) {
  return (
    error.response?.data?.detail ||
    error.message ||
    "Something went wrong."
  );
}

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalCustomers, setTotalCustomers] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");

  async function loadCustomers() {
    setLoading(true);
    setError("");

    try {
      const result = await getCustomers(page, pageSize);
      setCustomers(result.data || []);
      setTotalCustomers(Number(result.total_customers || 0));
    } catch (err) {
      setError(getError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCustomers();
  }, [page, pageSize]);

  async function openCustomer(customerId) {
    setSelectedCustomer(null);
    setDetailError("");
    setDetailLoading(true);

    try {
      const result = await getCustomer(customerId);
      setSelectedCustomer(result);
    } catch (err) {
      setDetailError(getError(err));
    } finally {
      setDetailLoading(false);
    }
  }

  const totalPages = Math.max(
    1,
    Math.ceil(totalCustomers / pageSize)
  );

  return (
    <section className="customers-page">
      <header className="customers-heading">
        <div>
          <h1>Customer Analytics</h1>
          <p>
            Explore customer orders, purchase quantities, and revenue.
          </p>
        </div>
      </header>

      <div className="customer-summary-grid">
        <article className="customer-summary-card">
          <span>Total Identified Customers</span>
          <strong>{formatNumber(totalCustomers)}</strong>
          <small>Customers with a recorded customer ID</small>
        </article>

        <article className="customer-summary-card">
          <span>Current Page</span>
          <strong>
            {page} / {totalPages}
          </strong>
          <small>Use pagination to view more customers</small>
        </article>
      </div>

      <article className="customers-panel">
        <div className="customers-panel-heading">
          <div>
            <h2>Customer Details</h2>
            <p>Sorted by total revenue, highest first.</p>
          </div>

          <label className="page-size-control">
            Rows
            <select
              value={pageSize}
              onChange={(event) => {
                setPageSize(Number(event.target.value));
                setPage(1);
              }}
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </label>
        </div>

        {loading ? (
          <p className="customer-status">Loading customers...</p>
        ) : error ? (
          <div className="customer-error" role="alert">
            <p>{error}</p>
            <button type="button" onClick={loadCustomers}>
              Retry
            </button>
          </div>
        ) : (
          <>
            <div className="customer-table-wrapper">
              <table className="customer-table">
                <thead>
                  <tr>
                    <th>Customer ID</th>
                    <th>Total Orders</th>
                    <th>Total Quantity</th>
                    <th>Total Revenue</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {customers.map((customer) => (
                    <tr key={customer.customer_id}>
                      <td>{customer.customer_id}</td>
                      <td>{formatNumber(customer.total_orders)}</td>
                      <td>{formatNumber(customer.total_quantity)}</td>
                      <td>{formatRevenue(customer.total_revenue)}</td>
                      <td>
                        <button
                          type="button"
                          className="customer-view-button"
                          onClick={() =>
                            openCustomer(customer.customer_id)
                          }
                        >
                          View details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {!customers.length && (
              <p className="customer-status">
                No customer records found.
              </p>
            )}

            <div className="customer-pagination">
              <span>
                Showing {customers.length ? (page - 1) * pageSize + 1 : 0}
                {"–"}
                {(page - 1) * pageSize + customers.length} of{" "}
                {formatNumber(totalCustomers)}
              </span>

              <div>
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage((current) => current - 1)}
                >
                  Previous
                </button>
                <button
                  type="button"
                  disabled={page >= totalPages}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </article>

      {(detailLoading || detailError || selectedCustomer) && (
        <article className="customer-detail-panel">
          <div className="customer-detail-heading">
            <h2>Customer Purchase Summary</h2>
            <button
              type="button"
              onClick={() => {
                setSelectedCustomer(null);
                setDetailError("");
              }}
            >
              Close
            </button>
          </div>

          {detailLoading && <p>Loading customer details...</p>}

          {detailError && (
            <p className="customer-detail-error">{detailError}</p>
          )}

          {selectedCustomer && (
            <div className="customer-detail-grid">
              <div>
                <span>Customer ID</span>
                <strong>{selectedCustomer.customer_id}</strong>
              </div>
              <div>
                <span>Total Orders</span>
                <strong>{formatNumber(selectedCustomer.total_orders)}</strong>
              </div>
              <div>
                <span>Total Quantity</span>
                <strong>
                  {formatNumber(selectedCustomer.total_quantity)}
                </strong>
              </div>
              <div>
                <span>Total Revenue</span>
                <strong>
                  {formatRevenue(selectedCustomer.total_revenue)}
                </strong>
              </div>
              <div>
                <span>First Purchase</span>
                <strong>
                  {selectedCustomer.first_purchase
                    ? String(selectedCustomer.first_purchase).slice(0, 10)
                    : "—"}
                </strong>
              </div>
              <div>
                <span>Last Purchase</span>
                <strong>
                  {selectedCustomer.last_purchase
                    ? String(selectedCustomer.last_purchase).slice(0, 10)
                    : "—"}
                </strong>
              </div>
            </div>
          )}
        </article>
      )}
    </section>
  );
}
