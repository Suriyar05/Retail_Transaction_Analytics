
import { useCallback, useEffect, useState } from "react";
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  getCurrentUser,
} from "../services/api";

import "./Products.css";

const formatNumber = (value) =>
  Number(value || 0).toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  });

const emptyForm = {
  stock_code: "",
  description: "",
  is_active: true,
};

function getError(error) {
  return (
    error.response?.data?.detail ||
    error.response?.data?.message ||
    error.message ||
    "Something went wrong."
  );
}

export default function Products() {
  // Authentication and role
  const [userRole, setUserRole] = useState(null);
  const isAdmin = userRole === "admin";

  // Product data
  const [products, setProducts] = useState([]);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("revenue");
  const [order, setOrder] = useState("desc");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalProducts, setTotalProducts] = useState(0);

  // Loading and messages
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Create/edit form
  const [formOpen, setFormOpen] = useState(false);
  const [editingCode, setEditingCode] = useState(null);
  const [form, setForm] = useState({ ...emptyForm });
  const [saving, setSaving] = useState(false);

  const totalPages = Math.max(
    1,
    Math.ceil(totalProducts / pageSize)
  );

  // Fetch the authenticated user's role.
  useEffect(() => {
    let active = true;

    async function loadUserRole() {
      try {
        const user = await getCurrentUser();

        if (active) {
          setUserRole(user.role);
        }
      } catch {
        if (active) {
          setUserRole(null);
        }
      }
    }

    loadUserRole();

    return () => {
      active = false;
    };
  }, []);

  // Load products using the current filters and pagination.
  const loadProducts = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const result = await getProducts({
        search,
        sort_by: sortBy,
        order,
        page,
        page_size: pageSize,
      });

      setProducts(result.data || []);
      setTotalProducts(Number(result.total_products || 0));
    } catch (err) {
      setError(getError(err));
    } finally {
      setLoading(false);
    }
  }, [search, sortBy, order, page, pageSize]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  // Open the create form.
  function startCreate() {
    if (!isAdmin) return;

    setEditingCode(null);
    setForm({ ...emptyForm });
    setActionError("");
    setSuccessMessage("");
    setFormOpen(true);
  }

  // Open the edit form.
  function startEdit(product) {
    if (!isAdmin) return;

    setEditingCode(product.stock_code);
    setForm({
      stock_code: product.stock_code,
      description: product.description || "",
      is_active: Boolean(product.is_active),
    });

    setActionError("");
    setSuccessMessage("");
    setFormOpen(true);
  }

  // Close and reset the form.
  function closeForm() {
    setFormOpen(false);
    setEditingCode(null);
    setForm({ ...emptyForm });
    setActionError("");
  }

  // Handle form input changes.
  function handleFormChange(event) {
    const { name, value, type, checked } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  // Create or update a product.
  async function handleSubmit(event) {
    event.preventDefault();

    if (!isAdmin) {
      setActionError("Only administrators can modify products.");
      return;
    }

    const stockCode = form.stock_code.trim();
    const description = form.description.trim();

    if (editingCode === null && !stockCode) {
      setActionError("Stock code is required.");
      return;
    }

    if (!description) {
      setActionError("Product description is required.");
      return;
    }

    setSaving(true);
    setActionError("");
    setSuccessMessage("");

    try {
      if (editingCode !== null) {
        // Existing API signature: updateProduct(code, description, isActive)
        await updateProduct(
          editingCode,
          description,
          form.is_active
        );

        setSuccessMessage("Product updated successfully.");
      } else {
        // Existing API signature: createProduct(code, description)
        await createProduct(stockCode, description);

        setSuccessMessage("Product created successfully.");
      }

      closeForm();
      await loadProducts();
    } catch (err) {
      setActionError(getError(err));
    } finally {
      setSaving(false);
    }
  }

  // Delete a product.
  async function handleDelete(product) {
    if (!isAdmin) return;

    const confirmed = window.confirm(
      `Delete product ${product.stock_code}? This action cannot be undone.`
    );

    if (!confirmed) return;

    setActionError("");
    setSuccessMessage("");

    try {
      await deleteProduct(product.stock_code);

      setSuccessMessage(
        `Product ${product.stock_code} deleted successfully.`
      );

      if (products.length === 1 && page > 1) {
        setPage((current) => current - 1);
      } else {
        await loadProducts();
      }
    } catch (err) {
      setActionError(getError(err));
    }
  }

  // Apply search.
  function applySearch(event) {
    event.preventDefault();
    setPage(1);
    setSearch(searchInput.trim());
  }

  return (
    <section className="products-page">
      <header className="products-heading">
        <div>
          <h1>Product Management</h1>
          <p>
            Search, review, create, edit, and delete product records.
          </p>
        </div>

        {isAdmin && (
          <button
            type="button"
            className="product-primary-button"
            onClick={startCreate}
          >
            + Add Product
          </button>
        )}
      </header>

      <div className="product-summary-card">
        <span>Products matching current search</span>
        <strong>{formatNumber(totalProducts)}</strong>
      </div>

      {successMessage && (
        <div className="product-success" role="status">
          {successMessage}
        </div>
      )}

      {actionError && (
        <div className="product-error" role="alert">
          {actionError}
        </div>
      )}

      {isAdmin && formOpen && (
        <article className="product-form-panel">
          <div className="product-form-heading">
            <h2>
              {editingCode !== null ? "Edit Product" : "Add Product"}
            </h2>

            <button
              type="button"
              className="product-secondary-button"
              onClick={closeForm}
              disabled={saving}
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="product-form-grid">
              <label>
                Stock Code
                <input
                  name="stock_code"
                  value={form.stock_code}
                  onChange={handleFormChange}
                  disabled={editingCode !== null || saving}
                  required
                  maxLength={100}
                  placeholder="Enter unique stock code"
                />
              </label>

              <label>
                Description
                <input
                  name="description"
                  value={form.description}
                  onChange={handleFormChange}
                  disabled={saving}
                  maxLength={500}
                  placeholder="Enter product description"
                  required
                />
              </label>

              {editingCode !== null && (
                <label>
                  Status
                  <select
                    name="is_active"
                    value={String(form.is_active)}
                    onChange={handleFormChange}
                    disabled={saving}
                  >
                    <option value="true">Active</option>
                    <option value="false">Inactive</option>
                  </select>
                </label>
              )}
            </div>

            <button
              type="submit"
              className="product-primary-button"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingCode !== null
                  ? "Save Changes"
                  : "Create Product"}
            </button>
          </form>
        </article>
      )}

      <article className="products-panel">
        <form className="products-toolbar" onSubmit={applySearch}>
          <input
            type="search"
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            placeholder="Search stock code or description..."
            aria-label="Search products"
          />

          <button
            type="submit"
            className="product-secondary-button"
          >
            Search
          </button>

          <label>
            Sort by
            <select
              value={sortBy}
              onChange={(event) => {
                setSortBy(event.target.value);
                setPage(1);
              }}
            >
              <option value="revenue">Revenue</option>
              <option value="quantity">Quantity</option>
            </select>
          </label>

          <label>
            Order
            <select
              value={order}
              onChange={(event) => {
                setOrder(event.target.value);
                setPage(1);
              }}
            >
              <option value="desc">Highest first</option>
              <option value="asc">Lowest first</option>
            </select>
          </label>

          <label>
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
        </form>

        {loading ? (
          <p className="product-status">Loading products...</p>
        ) : error ? (
          <div className="product-error" role="alert">
            <p>{error}</p>
            <button
              type="button"
              className="product-secondary-button"
              onClick={loadProducts}
            >
              Retry
            </button>
          </div>
        ) : (
          <>
            <div className="products-table-wrapper">
              <table className="products-table">
                <thead>
                  <tr>
                    <th>Stock Code</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Total Quantity</th>
                    <th>Total Revenue</th>
                    {isAdmin && <th>Actions</th>}
                  </tr>
                </thead>

                <tbody>
                  {products.map((product) => (
                    <tr key={product.stock_code}>
                      <td>{product.stock_code}</td>
                      <td>
                        {product.description || "No description"}
                      </td>
                      <td>
                        <span
                          className={`product-status-badge ${
                            product.is_active
                              ? "is-active"
                              : "is-inactive"
                          }`}
                        >
                          {product.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td>
                        {formatNumber(product.total_quantity)}
                      </td>
                      <td>
                        {formatNumber(product.total_revenue)}
                      </td>

                      {isAdmin && (
                        <td>
                          <div className="product-row-actions">
                            <button
                              type="button"
                              className="product-edit-button"
                              onClick={() => startEdit(product)}
                            >
                              Edit
                            </button>

                            <button
                              type="button"
                              className="product-delete-button"
                              onClick={() => handleDelete(product)}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {!products.length && (
              <p className="product-status">No products found.</p>
            )}

            <div className="product-pagination">
              <span>
                Page {page} of {totalPages} ·{" "}
                {formatNumber(totalProducts)} products
              </span>

              <div>
                <button
                  type="button"
                  className="product-secondary-button"
                  disabled={page <= 1 || loading}
                  onClick={() =>
                    setPage((current) => current - 1)
                  }
                >
                  Previous
                </button>

                <button
                  type="button"
                  className="product-secondary-button"
                  disabled={page >= totalPages || loading}
                  onClick={() =>
                    setPage((current) => current + 1)
                  }
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </article>
    </section>
  );
}
