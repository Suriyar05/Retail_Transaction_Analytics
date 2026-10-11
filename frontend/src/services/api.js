
import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000",
  timeout: 120000,
});

// ============================================================
// AUTHENTICATION HELPERS
// ============================================================

const TOKEN_KEY = "retail_access_token";

export const getAccessToken = () =>
  sessionStorage.getItem(TOKEN_KEY);

export const saveAccessToken = (token) =>
  sessionStorage.setItem(TOKEN_KEY, token);

export const clearAccessToken = () =>
  sessionStorage.removeItem(TOKEN_KEY);

// Automatically attach the JWT to protected API requests.
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// If a protected request returns 401, end the local session.
// Do not log out when the login endpoint itself returns 401.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestUrl = error.config?.url || "";
    const isLoginRequest = requestUrl.includes("/api/auth/login");

    if (error.response?.status === 401 && !isLoginRequest) {
      clearAccessToken();
      window.dispatchEvent(new Event("auth:unauthorized"));
    }

    return Promise.reject(error);
  }
);

// ============================================================
// AUTHENTICATION API
// ============================================================

export const login = async (username, password) => {
  const response = await api.post("/api/auth/login", {
    username,
    password,
  });

  const { access_token, username: loggedInUsername, role } =
    response.data;

  saveAccessToken(access_token);

  return {
    username: loggedInUsername,
    role,
  };
};

export const getCurrentUser = async () => {
  const response = await api.get("/api/auth/me");
  return response.data;
};

export const logout = () => {
  clearAccessToken();
};

// ============================================================
// ANALYTICS
// ============================================================

export const getSummary = async () => {
  const response = await api.get("/api/analytics/summary");
  return response.data;
};

export const getMonthlySales = async () => {
  const response = await api.get("/api/analytics/monthly-sales");
  return response.data;
};

export const getCountrySales = async () => {
  const response = await api.get("/api/analytics/country-sales");
  return response.data;
};

export const getTopProducts = async (limit = 10) => {
  const response = await api.get("/api/analytics/top-products", {
    params: { limit },
  });
  return response.data;
};

export const getDateRangeSales = async (startDate, endDate) => {
  const response = await api.get("/api/analytics/date-range", {
    params: {
      start_date: startDate,
      end_date: endDate,
    },
  });

  return response.data;
};

// ============================================================
// CUSTOMERS
// ============================================================

export const getCustomers = async (page = 1, pageSize = 10) => {
  const response = await api.get("/api/customers", {
    params: { page, page_size: pageSize },
  });
  return response.data;
};

export const getTopCustomers = async (limit = 10) => {
  const response = await api.get("/api/customers/top", {
    params: { limit },
  });
  return response.data;
};

export const getCustomer = async (customerId) => {
  const response = await api.get(
    `/api/customers/${encodeURIComponent(customerId)}`
  );
  return response.data;
};

// ============================================================
// PRODUCTS
// ============================================================

export const getProducts = async ({
  search = "",
  sortBy = "revenue",
  order = "desc",
  page = 1,
  pageSize = 10,
} = {}) => {
  const response = await api.get("/api/products", {
    params: {
      search: search.trim() || undefined,
      sort_by: sortBy,
      order,
      page,
      page_size: pageSize,
    },
  });

  return response.data;
};

export const getProduct = async (stockCode) => {
  const response = await api.get(
    `/api/products/${encodeURIComponent(stockCode)}`
  );
  return response.data;
};

// Existing FastAPI route accepts query parameters.
export const createProduct = async ({ stock_code, description }) => {
  const response = await api.post("/api/products", null, {
    params: {
      stock_code,
      description: description || undefined,
    },
  });

  return response.data;
};

export const updateProduct = async (
  stockCode,
  { description, is_active }
) => {
  const response = await api.put(
    `/api/products/${encodeURIComponent(stockCode)}`,
    null,
    {
      params: {
        description,
        is_active,
      },
    }
  );

  return response.data;
};

export const deleteProduct = async (stockCode) => {
  const response = await api.delete(
    `/api/products/${encodeURIComponent(stockCode)}`
  );

  return response.data;
};

export default api;
