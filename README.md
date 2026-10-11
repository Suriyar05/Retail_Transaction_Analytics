# Retail Transaction Analytics Platform

A full-stack retail analytics application that processes online retail transaction data, stores cleaned records in MySQL, exposes analytics through a FastAPI backend, and presents business metrics through a React dashboard.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Dataset](#dataset)
- [Data Engineering Pipeline](#data-engineering-pipeline)
- [Database](#database)
- [Backend API](#backend-api)
- [Authentication and Authorization](#authentication-and-authorization)
- [Frontend](#frontend)
- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Running the Application](#running-the-application)
- [Validation and Verification](#validation-and-verification)
- [Repository Structure](#repository-structure)
- [Security Notes](#security-notes)
- [Known Considerations](#known-considerations)

## Project Overview

The Retail Transaction Analytics Platform helps explore historical online retail transactions using a data-processing pipeline, a relational database, REST APIs, and a web dashboard.

The source workbook contains two sheets:

- `Year 2009-2010`
- `Year 2010-2011`

The ETL pipeline extracts and transforms the workbook data, reports data-quality statistics, cleans the dataset, and writes the processed output to Parquet. The cleaned data is stored in a MySQL database named `retail_analytics` and served to the frontend through FastAPI endpoints.

## Key Features

- ETL processing of the two Excel worksheets.
- Data-quality reporting for duplicates, negative and zero values, invalid dates, and missing values.
- Processed dataset output in Parquet format.
- MySQL storage for transaction records.
- FastAPI endpoints for analytics, customers, products, and authentication.
- React/Vite dashboard pages:
  - Overview
  - Sales Analytics
  - Customer Analytics
  - Product Management
- JWT-based authentication.
- Role-based access control for `admin` and `analyst` users.
- Product search, sorting, and pagination.
- Product creation, updating, and deletion restricted to administrators by the backend.
- Interactive API documentation through FastAPI Swagger UI.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| Database access | SQLAlchemy, PyMySQL |
| Database | MySQL |
| Data processing | pandas, Excel input, Parquet output |
| Authentication | JWT, password hashing with `pwdlib` |
| API testing/documentation | FastAPI Swagger UI |

Confirm the exact installed versions in your environment before documenting or deploying a release.

## Architecture

```text
Excel workbook
  ├── Year 2009-2010
  └── Year 2010-2011
          |
          v
     ETL pipeline
  Extract -> Validate -> Transform -> Clean
          |
          +--------------------> cleaned_retail.parquet
          |
          v
    MySQL: retail_analytics
          |
          v
       FastAPI
  ├── Authentication
  ├── Analytics endpoints
  ├── Customer endpoints
  └── Product endpoints
          |
          v
     React / Vite
  ├── Overview
  ├── Sales Analytics
  ├── Customer Analytics
  └── Product Management
```

## Dataset

The source file used by the project is:

```text
data/raw/Online_Retail_II.xlsx
```

It contains the `Year 2009-2010` and `Year 2010-2011` worksheets.

The processed dataset includes these 12 columns:

| Column | Description |
|---|---|
| `invoice_no` | Invoice identifier |
| `stock_code` | Product/stock identifier |
| `description` | Product description |
| `quantity` | Quantity recorded in the transaction row |
| `invoice_date` | Transaction date and time |
| `unit_price` | Unit price |
| `customer_id` | Customer identifier, when available |
| `country` | Country associated with the transaction |
| `source_sheet` | Source worksheet |
| `transaction_value` | Transaction-row value derived by the ETL |
| `is_cancelled_invoice` | Flag identifying cancelled invoices |
| `is_negative_quantity` | Flag identifying negative quantities |

## Data Engineering Pipeline

Run the ETL from the repository root:

```powershell
python run_etl.py
```

The pipeline reports extraction, validation, transformation, data-quality statistics, and the final processed dataset shape.

### Verified ETL results

The most recently shared successful run reported:

| Metric | Result |
|---|---:|
| Records extracted | 1,067,371 |
| Records after cleaning | 1,055,233 |
| Columns in processed output | 12 |
| Duplicate records reported before cleaning | 12,133 |
| Negative-quantity records reported before cleaning | 22,950 |
| Zero-quantity records reported before cleaning | 0 |
| Negative-price records reported before cleaning | 5 |
| Zero-price records reported before cleaning | 6,202 |
| Invalid dates reported before cleaning | 0 |
| Missing descriptions reported before cleaning | 4,382 |
| Missing customer IDs reported before cleaning | 243,007 |

Output file:

```text
data/processed/cleaned_retail.parquet
```

The difference between the extracted and cleaned record counts is 12,138. The data-quality report separately reports 12,133 duplicate records; refer to the ETL cleaning rules to explain the full reconciliation rather than assuming every removed row was a duplicate.

Missing customer identifiers, negative quantities, and zero prices may have valid business meanings in retail data. Their handling should follow the transformation and cleaning rules implemented in the project.

## Database

The MySQL database is named:

```text
retail_analytics
```

The main transaction table is named `transactions`.

### Verified database results

The database checks shared for the project returned:

| Metric | Result |
|---|---:|
| Transaction records | 1,055,233 |
| Unique invoices | 53,623 |
| Unique products | 5,131 |
| Earliest invoice date | 2009-12-01 07:45:00 |
| Latest invoice date | 2011-12-09 12:50:00 |

To verify the transaction count and date range in MySQL:

```sql
USE retail_analytics;

SELECT COUNT(*) AS total_transactions
FROM transactions;

SELECT
    MIN(invoice_date) AS earliest_date,
    MAX(invoice_date) AS latest_date,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    COUNT(DISTINCT stock_code) AS unique_products
FROM transactions;
```

To inspect additional aggregate metrics:

```sql
SELECT
    COUNT(*) AS transaction_records,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT stock_code) AS unique_products,
    COUNT(DISTINCT country) AS unique_countries,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions;
```

## Backend API

The backend is implemented with FastAPI. It exposes routes for authentication, analytics, customers, and products.

Start the backend from the project root:

```powershell
uvicorn src.api.main:app --reload
```

By default, the development server is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### API route groups

| Route | Purpose |
|---|---|
| `/api/auth/login` | Authenticate a user and obtain an access token |
| `/api/auth/me` | Return the current authenticated user |
| `/api/products/` | List and search products |
| `/api/products/{stock_code}` | Retrieve a product |
| `/api/products/` (`POST`) | Create a product; admin access required |
| `/api/products/{stock_code}` (`PUT`) | Update a product; admin access required |
| `/api/products/{stock_code}` (`DELETE`) | Delete a product; admin access required |

Analytics and customer routes are also included by the backend. Use `/docs` to inspect their exact paths, query parameters, and response schemas in the current version.

Product listing supports search, sorting, and pagination. An example request used during development was:

```text
GET /api/products/?search=bag&sort_by=revenue&order=desc&page=1&page_size=5
```

## Authentication and Authorization

The application uses JWT access tokens and has two roles:

- `admin`: can use the application and perform product management operations.
- `analyst`: can view analytics and products but cannot create, update, or delete products.

The frontend sends the access token in the `Authorization: Bearer <token>` header. The backend validates the token and enforces permissions on protected endpoints.

### Initial setup

Authentication depends on the `users` table, a configured JWT secret, and a created user account. Follow the setup code and database configuration in the repository to create the table and provision the first administrator. Public self-registration is not part of the described login workflow.

## Frontend

The frontend is a React application built with Vite.

Start the frontend in a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite prints the local URL when the development server starts. The default is commonly `http://localhost:5173`, but use the URL shown in your terminal.

### Dashboard pages

- **Overview:** high-level business metrics.
- **Sales Analytics:** sales analysis, charts, and date filtering.
- **Customer Analytics:** customer data, pagination, and customer details.
- **Product Management:** product search, sorting, pagination, and administrator-only CRUD controls.

The backend remains responsible for enforcing permissions; hiding frontend controls alone is not a security boundary.

## Prerequisites

Install the following before running the project:

- Python and pip, using a version compatible with the project's installed dependencies.
- Node.js and npm.
- MySQL Server.
- The source workbook at `data/raw/Online_Retail_II.xlsx`.

The project uses a MySQL database called `retail_analytics`. Ensure that the database and required tables exist before starting the API.

## Project Setup

### 1. Clone or open the repository

If cloning from GitHub:

```powershell
git clone <YOUR_REPOSITORY_URL>
cd Retail_Transaction_Analytics
```

Replace `<YOUR_REPOSITORY_URL>` with the actual repository URL.

### 2. Create and activate a Python virtual environment

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use your established Python environment or follow your machine's execution-policy guidance.

### 3. Install Python dependencies

If `requirements.txt` is maintained:

```powershell
python -m pip install -r requirements.txt
```

Ensure it includes all dependencies imported by the current source code. The dependency list should be based on the actual project imports and tested environment.

### 4. Configure environment variables

The backend authentication code expects a `JWT_SECRET_KEY` in the project-root `.env` file. The database configuration currently described during development uses MySQL on `localhost:3306`, database `retail_analytics`, and a local `root` account.

Create a local `.env` file with the required configuration. Use strong local secrets and never commit `.env` to GitHub. If database settings are hardcoded in the current source, consider moving them to environment variables before deployment.

### 5. Prepare the database

Create the `retail_analytics` database if it does not already exist, then apply the schema/setup SQL and user-table setup required by the backend. The project requires the `transactions` table and the `users` table for authentication.

Use the repository's actual schema or setup scripts where available; this README does not assume an unverified schema migration command.

### 6. Place the dataset

Ensure the source workbook is located at:

```text
data/raw/Online_Retail_II.xlsx
```

### 7. Run the ETL

```powershell
python run_etl.py
```

Check that the Parquet output is created and that the reported record count matches the expected cleaning behavior.

### 8. Start the backend and frontend

Run the backend and frontend in separate terminals using the commands in the sections above.

## Validation and Verification

The following checks were performed during development and reported as successful:

- ETL extraction, validation, transformation, and Parquet output completed.
- The cleaned Parquet dataset had 1,055,233 rows and 12 columns.
- MySQL contained 1,055,233 transaction records.
- The database date range was `2009-12-01 07:45:00` through `2011-12-09 12:50:00`.
- MySQL reported 53,623 unique invoices and 5,131 unique products.
- Authentication and role-based access control were reported as working.
- The Overview, Sales Analytics, Customer Analytics, and Product Management pages were reported as working.

These are development verification results, not a claim that an automated test suite or production deployment has been completed.

## Repository Structure

The following is a simplified view of the paths referenced during development. Check the actual repository for any additional folders or files.

```text
Retail_Transaction_Analytics/
├── data/
│   ├── raw/
│   │   └── Online_Retail_II.xlsx
│   └── processed/
│       └── cleaned_retail.parquet
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Overview/
│   │   │   ├── SalesAnalytics/
│   │   │   ├── Customers/
│   │   │   └── Products.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
├── src/
│   └── api/
│       ├── main.py
│       ├── database.py
│       └── routes/
│           ├── auth.py
│           ├── analytics.py
│           ├── customers.py
│           └── products.py
├── run_etl.py
├── requirements.txt
└── README.md
```

## Security Notes

- Never commit `.env`, passwords, JWT secrets, or other credentials.
- Use a strong, unique JWT signing secret.
- Use password hashing rather than storing plaintext passwords.
- Enforce authorization on the backend, not only in React.
- Do not expose development server settings as a production deployment configuration.
- Avoid committing large generated datasets or database files unless explicitly required for the submission.
- Before deployment, configure the database connection securely through environment variables and use production-appropriate server settings.

## Known Considerations

- The dataset contains missing customer IDs, missing descriptions, negative quantities, zero prices, and duplicate records. Interpret these using the project's implemented data-quality and cleaning rules.
- The record count removed during cleaning does not exactly equal the reported duplicate count; reconcile this difference using the ETL implementation before describing every removed row as a duplicate.
- The setup commands above are development commands. No production deployment URL or cloud hosting configuration has been verified.
- Inspect `/docs` for the current API contract, because route parameters and response schemas are determined by the actual backend implementation.

---

## License

Add a license here if you choose to distribute the project under a specific open-source license.
