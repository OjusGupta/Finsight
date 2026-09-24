-- ============================================================
-- FinSight - Initial Database Schema
-- PostgreSQL
-- ============================================================

-- ------------------------------------------------------------
-- 1. COMPANIES
-- ------------------------------------------------------------

CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 2. STORES
-- ------------------------------------------------------------

CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,

    company_id INT NOT NULL,

    store_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    address TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_store_company
        FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- 3. USERS
-- ------------------------------------------------------------

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,

    store_id INT NOT NULL,

    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,

    role VARCHAR(50) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- 4. CATEGORIES
-- ------------------------------------------------------------

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,

    category_name VARCHAR(100) UNIQUE NOT NULL,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 5. PRODUCTS
-- ------------------------------------------------------------

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,

    category_id INT NOT NULL,

    product_name VARCHAR(200) NOT NULL,

    sku VARCHAR(100) UNIQUE NOT NULL,

    unit_price NUMERIC(12,2) NOT NULL,

    cost_price NUMERIC(12,2) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_product_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_product_cost
        CHECK (cost_price >= 0)
);


-- ============================================================
-- END OF INITIAL SCHEMA
-- ============================================================
-- ------------------------------------------------------------
-- 6. SUPPLIERS
-- ------------------------------------------------------------

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,

    supplier_name VARCHAR(150) NOT NULL,

    contact_person VARCHAR(150),

    email VARCHAR(150),

    phone VARCHAR(30),

    address TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ------------------------------------------------------------
-- 7. SUPPLIER PRODUCTS
-- ------------------------------------------------------------

CREATE TABLE supplier_products (
    supplier_product_id SERIAL PRIMARY KEY,

    supplier_id INT NOT NULL,
    product_id INT NOT NULL,

    supplier_price NUMERIC(12,2),

    lead_time_days INT,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_supplier_product_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_supplier_product_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_supplier_product
        UNIQUE (supplier_id, product_id),

    CONSTRAINT chk_supplier_price
        CHECK (supplier_price >= 0),

    CONSTRAINT chk_lead_time
        CHECK (lead_time_days >= 0)
);
-- ------------------------------------------------------------
-- 8. CUSTOMERS
-- ------------------------------------------------------------

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,

    full_name VARCHAR(150) NOT NULL,

    email VARCHAR(150) UNIQUE,

    phone VARCHAR(30),

    city VARCHAR(100),
    state VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ------------------------------------------------------------
-- 9. INVENTORY
-- ------------------------------------------------------------

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,

    store_id INT NOT NULL,
    product_id INT NOT NULL,

    quantity INT NOT NULL DEFAULT 0,

    reorder_level INT NOT NULL DEFAULT 10,

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_inventory_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_inventory_store_product
        UNIQUE (store_id, product_id),

    CONSTRAINT chk_inventory_quantity
        CHECK (quantity >= 0),

    CONSTRAINT chk_inventory_reorder_level
        CHECK (reorder_level >= 0)
);
-- ------------------------------------------------------------
-- 10. INVENTORY MOVEMENTS
-- ------------------------------------------------------------

CREATE TABLE inventory_movements (
    movement_id SERIAL PRIMARY KEY,

    inventory_id INT NOT NULL,

    movement_type VARCHAR(50) NOT NULL,

    quantity_change INT NOT NULL,

    reference_type VARCHAR(50),

    reference_id INT,

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_movement_inventory
        FOREIGN KEY (inventory_id)
        REFERENCES inventory(inventory_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_movement_type
        CHECK (
            movement_type IN (
                'PURCHASE',
                'SALE',
                'RETURN',
                'ADJUSTMENT',
                'DAMAGE',
                'TRANSFER'
            )
        ),

    CONSTRAINT chk_quantity_change
        CHECK (quantity_change <> 0)
);
-- ------------------------------------------------------------
-- 11. SALES
-- ------------------------------------------------------------

CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,

    store_id INT NOT NULL,
    customer_id INT,
    user_id INT,

    invoice_number VARCHAR(100) UNIQUE NOT NULL,

    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    subtotal NUMERIC(12,2) NOT NULL DEFAULT 0,
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',

    CONSTRAINT fk_sale_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_sale_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_sale_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_sale_subtotal
        CHECK (subtotal >= 0),

    CONSTRAINT chk_sale_discount
        CHECK (discount_amount >= 0),

    CONSTRAINT chk_sale_tax
        CHECK (tax_amount >= 0),

    CONSTRAINT chk_sale_total
        CHECK (total_amount >= 0),

    CONSTRAINT chk_sale_status
        CHECK (
            status IN (
                'COMPLETED',
                'CANCELLED',
                'REFUNDED',
                'PARTIALLY_REFUNDED'
            )
        )
);
-- ------------------------------------------------------------
-- 12. SALE ITEMS
-- ------------------------------------------------------------

CREATE TABLE sale_items (
    sale_item_id SERIAL PRIMARY KEY,

    sale_id INT NOT NULL,
    product_id INT NOT NULL,

    quantity INT NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,

    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    line_total NUMERIC(12,2) NOT NULL,

    CONSTRAINT fk_sale_item_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_sale_item_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_sale_item_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_sale_item_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_sale_item_discount
        CHECK (discount_amount >= 0),

    CONSTRAINT chk_sale_item_total
        CHECK (line_total >= 0)
);
-- ------------------------------------------------------------
-- 13. PAYMENTS
-- ------------------------------------------------------------

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,

    sale_id INT NOT NULL,

    payment_method VARCHAR(30) NOT NULL,

    amount NUMERIC(12,2) NOT NULL,

    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    transaction_reference VARCHAR(150),

    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',

    CONSTRAINT fk_payment_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_payment_amount
        CHECK (amount > 0),

    CONSTRAINT chk_payment_method
        CHECK (
            payment_method IN (
                'CASH',
                'CARD',
                'UPI',
                'NET_BANKING',
                'WALLET'
            )
        ),

    CONSTRAINT chk_payment_status
        CHECK (
            status IN (
                'PENDING',
                'COMPLETED',
                'FAILED',
                'REFUNDED'
            )
        )
);
-- ------------------------------------------------------------
-- 14. RETURNS
-- ------------------------------------------------------------

CREATE TABLE returns (
    return_id SERIAL PRIMARY KEY,

    sale_id INT NOT NULL,
    customer_id INT,

    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    reason VARCHAR(255),

    status VARCHAR(30) NOT NULL DEFAULT 'REQUESTED',

    total_refund_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    CONSTRAINT fk_return_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_return_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_return_status
        CHECK (
            status IN (
                'REQUESTED',
                'APPROVED',
                'REJECTED',
                'COMPLETED'
            )
        ),

    CONSTRAINT chk_return_amount
        CHECK (total_refund_amount >= 0)
);
-- ------------------------------------------------------------
-- 15. RETURN ITEMS
-- ------------------------------------------------------------

CREATE TABLE return_items (
    return_item_id SERIAL PRIMARY KEY,

    return_id INT NOT NULL,
    sale_item_id INT NOT NULL,

    quantity INT NOT NULL,

    refund_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    CONSTRAINT fk_return_item_return
        FOREIGN KEY (return_id)
        REFERENCES returns(return_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_return_item_sale_item
        FOREIGN KEY (sale_item_id)
        REFERENCES sale_items(sale_item_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_return_item_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_return_item_refund
        CHECK (refund_amount >= 0)
);
-- ------------------------------------------------------------
-- 16. REFUNDS
-- ------------------------------------------------------------

CREATE TABLE refunds (
    refund_id SERIAL PRIMARY KEY,

    return_id INT NOT NULL,

    refund_amount NUMERIC(12,2) NOT NULL,

    refund_method VARCHAR(30) NOT NULL,

    refund_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    transaction_reference VARCHAR(150),

    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',

    CONSTRAINT fk_refund_return
        FOREIGN KEY (return_id)
        REFERENCES returns(return_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_refund_amount
        CHECK (refund_amount > 0),

    CONSTRAINT chk_refund_method
        CHECK (
            refund_method IN (
                'CASH',
                'CARD',
                'UPI',
                'NET_BANKING',
                'WALLET'
            )
        ),

    CONSTRAINT chk_refund_status
        CHECK (
            status IN (
                'PENDING',
                'COMPLETED',
                'FAILED'
            )
        )
);
-- ============================================================
-- FinSight - Initial Database Schema
-- PostgreSQL
-- ============================================================

-- ------------------------------------------------------------
-- 1. COMPANIES
-- ------------------------------------------------------------

CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 2. STORES
-- ------------------------------------------------------------

CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,

    company_id INT NOT NULL,

    store_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    address TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_store_company
        FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- 3. USERS
-- ------------------------------------------------------------

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,

    store_id INT NOT NULL,

    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,

    role VARCHAR(50) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- 4. CATEGORIES
-- ------------------------------------------------------------

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,

    category_name VARCHAR(100) UNIQUE NOT NULL,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 5. PRODUCTS
-- ------------------------------------------------------------

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,

    category_id INT NOT NULL,

    product_name VARCHAR(200) NOT NULL,

    sku VARCHAR(100) UNIQUE NOT NULL,

    unit_price NUMERIC(12,2) NOT NULL,

    cost_price NUMERIC(12,2) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_product_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_product_cost
        CHECK (cost_price >= 0)
);


-- ============================================================
-- END OF INITIAL SCHEMA
-- ============================================================
-- ------------------------------------------------------------
-- 6. SUPPLIERS
-- ------------------------------------------------------------

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,

    supplier_name VARCHAR(150) NOT NULL,

    contact_person VARCHAR(150),

    email VARCHAR(150),

    phone VARCHAR(30),

    address TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ------------------------------------------------------------
-- 7. SUPPLIER PRODUCTS
-- ------------------------------------------------------------

CREATE TABLE supplier_products (
    supplier_product_id SERIAL PRIMARY KEY,

    supplier_id INT NOT NULL,
    product_id INT NOT NULL,

    supplier_price NUMERIC(12,2),

    lead_time_days INT,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_supplier_product_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_supplier_product_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_supplier_product
        UNIQUE (supplier_id, product_id),

    CONSTRAINT chk_supplier_price
        CHECK (supplier_price >= 0),

    CONSTRAINT chk_lead_time
        CHECK (lead_time_days >= 0)
);
-- ------------------------------------------------------------
-- 8. CUSTOMERS
-- ------------------------------------------------------------

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,

    full_name VARCHAR(150) NOT NULL,

    email VARCHAR(150) UNIQUE,

    phone VARCHAR(30),

    city VARCHAR(100),
    state VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ------------------------------------------------------------
-- 9. INVENTORY
-- ------------------------------------------------------------

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,

    store_id INT NOT NULL,
    product_id INT NOT NULL,

    quantity INT NOT NULL DEFAULT 0,

    reorder_level INT NOT NULL DEFAULT 10,

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_inventory_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_inventory_store_product
        UNIQUE (store_id, product_id),

    CONSTRAINT chk_inventory_quantity
        CHECK (quantity >= 0),

    CONSTRAINT chk_inventory_reorder_level
        CHECK (reorder_level >= 0)
);
-- ------------------------------------------------------------
-- 10. INVENTORY MOVEMENTS
-- ------------------------------------------------------------

CREATE TABLE inventory_movements (
    movement_id SERIAL PRIMARY KEY,

    inventory_id INT NOT NULL,

    movement_type VARCHAR(50) NOT NULL,

    quantity_change INT NOT NULL,

    reference_type VARCHAR(50),

    reference_id INT,

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_movement_inventory
        FOREIGN KEY (inventory_id)
        REFERENCES inventory(inventory_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_movement_type
        CHECK (
            movement_type IN (
                'PURCHASE',
                'SALE',
                'RETURN',
                'ADJUSTMENT',
                'DAMAGE',
                'TRANSFER'
            )
        ),

    CONSTRAINT chk_quantity_change
        CHECK (quantity_change <> 0)
);
-- ------------------------------------------------------------
-- 11. SALES
-- ------------------------------------------------------------

CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,

    store_id INT NOT NULL,
    customer_id INT,
    user_id INT,

    invoice_number VARCHAR(100) UNIQUE NOT NULL,

    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    subtotal NUMERIC(12,2) NOT NULL DEFAULT 0,
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',

    CONSTRAINT fk_sale_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_sale_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_sale_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_sale_subtotal
        CHECK (subtotal >= 0),

    CONSTRAINT chk_sale_discount
        CHECK (discount_amount >= 0),

    CONSTRAINT chk_sale_tax
        CHECK (tax_amount >= 0),

    CONSTRAINT chk_sale_total
        CHECK (total_amount >= 0),

    CONSTRAINT chk_sale_status
        CHECK (
            status IN (
                'COMPLETED',
                'CANCELLED',
                'REFUNDED',
                'PARTIALLY_REFUNDED'
            )
        )
);
-- ------------------------------------------------------------
-- 12. SALE ITEMS
-- ------------------------------------------------------------

CREATE TABLE sale_items (
    sale_item_id SERIAL PRIMARY KEY,

    sale_id INT NOT NULL,
    product_id INT NOT NULL,

    quantity INT NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,

    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    line_total NUMERIC(12,2) NOT NULL,

    CONSTRAINT fk_sale_item_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_sale_item_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_sale_item_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_sale_item_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_sale_item_discount
        CHECK (discount_amount >= 0),

    CONSTRAINT chk_sale_item_total
        CHECK (line_total >= 0)
);
-- ------------------------------------------------------------
-- 13. PAYMENTS
-- ------------------------------------------------------------

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,

    sale_id INT NOT NULL,

    payment_method VARCHAR(30) NOT NULL,

    amount NUMERIC(12,2) NOT NULL,

    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    transaction_reference VARCHAR(150),

    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',

    CONSTRAINT fk_payment_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_payment_amount
        CHECK (amount > 0),

    CONSTRAINT chk_payment_method
        CHECK (
            payment_method IN (
                'CASH',
                'CARD',
                'UPI',
                'NET_BANKING',
                'WALLET'
            )
        ),

    CONSTRAINT chk_payment_status
        CHECK (
            status IN (
                'PENDING',
                'COMPLETED',
                'FAILED',
                'REFUNDED'
            )
        )
);
-- ------------------------------------------------------------
-- 14. RETURNS
-- ------------------------------------------------------------

CREATE TABLE returns (
    return_id SERIAL PRIMARY KEY,

    sale_id INT NOT NULL,
    customer_id INT,

    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    reason VARCHAR(255),

    status VARCHAR(30) NOT NULL DEFAULT 'REQUESTED',

    total_refund_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    CONSTRAINT fk_return_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_return_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_return_status
        CHECK (
            status IN (
                'REQUESTED',
                'APPROVED',
                'REJECTED',
                'COMPLETED'
            )
        ),

    CONSTRAINT chk_return_amount
        CHECK (total_refund_amount >= 0)
);
-- ------------------------------------------------------------
-- 15. RETURN ITEMS
-- ------------------------------------------------------------

CREATE TABLE return_items (
    return_item_id SERIAL PRIMARY KEY,

    return_id INT NOT NULL,
    sale_item_id INT NOT NULL,

    quantity INT NOT NULL,

    refund_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    CONSTRAINT fk_return_item_return
        FOREIGN KEY (return_id)
        REFERENCES returns(return_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_return_item_sale_item
        FOREIGN KEY (sale_item_id)
        REFERENCES sale_items(sale_item_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_return_item_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_return_item_refund
        CHECK (refund_amount >= 0)
);
-- ------------------------------------------------------------
-- 16. REFUNDS
-- ------------------------------------------------------------

CREATE TABLE refunds (
    refund_id SERIAL PRIMARY KEY,

    return_id INT NOT NULL,

    refund_amount NUMERIC(12,2) NOT NULL,

    refund_method VARCHAR(30) NOT NULL,

    refund_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    transaction_reference VARCHAR(150),

    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',

    CONSTRAINT fk_refund_return
        FOREIGN KEY (return_id)
        REFERENCES returns(return_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_refund_amount
        CHECK (refund_amount > 0),

    CONSTRAINT chk_refund_method
        CHECK (
            refund_method IN (
                'CASH',
                'CARD',
                'UPI',
                'NET_BANKING',
                'WALLET'
            )
        ),

    CONSTRAINT chk_refund_status
        CHECK (
            status IN (
                'PENDING',
                'COMPLETED',
                'FAILED'
            )
        )
);
-- ------------------------------------------------------------
-- 19. RAW DATA BATCHES
-- ------------------------------------------------------------

CREATE TABLE raw_data_batches (
    batch_id SERIAL PRIMARY KEY,

    source_name VARCHAR(100) NOT NULL,

    source_type VARCHAR(50) NOT NULL,

    file_name VARCHAR(255),

    record_count INT,

    ingestion_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    ingestion_completed_at TIMESTAMP,

    status VARCHAR(30) NOT NULL DEFAULT 'RECEIVED',

    error_message TEXT,

    CONSTRAINT chk_raw_source_type
        CHECK (
            source_type IN (
                'CSV',
                'API',
                'DATABASE',
                'ERP'
            )
        ),

    CONSTRAINT chk_raw_batch_status
        CHECK (
            status IN (
                'RECEIVED',
                'PROCESSING',
                'COMPLETED',
                'FAILED'
            )
        ),

    CONSTRAINT chk_raw_record_count
        CHECK (record_count >= 0)
);
-- ------------------------------------------------------------
-- 20. RAW SALES
-- ------------------------------------------------------------

CREATE TABLE raw_sales (
    raw_sale_id SERIAL PRIMARY KEY,

    batch_id INT,

    source_row_number INT,

    invoice_number VARCHAR(100),

    sale_date_raw VARCHAR(100),

    store_code_raw VARCHAR(100),

    customer_code_raw VARCHAR(100),

    product_code_raw VARCHAR(100),

    quantity_raw VARCHAR(100),

    unit_price_raw VARCHAR(100),

    total_amount_raw VARCHAR(100),

    ingestion_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    validation_error TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_raw_sale_batch
        FOREIGN KEY (batch_id)
        REFERENCES raw_data_batches(batch_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_raw_sale_status
        CHECK (
            ingestion_status IN (
                'PENDING',
                'VALID',
                'INVALID',
                'PROCESSED'
            )
        )
);
-- ------------------------------------------------------------
-- 21. DATA QUALITY ISSUES
-- ------------------------------------------------------------

CREATE TABLE data_quality_issues (
    issue_id SERIAL PRIMARY KEY,

    batch_id INT,

    raw_sale_id INT,

    issue_type VARCHAR(100) NOT NULL,

    issue_description TEXT NOT NULL,

    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    resolved_at TIMESTAMP,

    CONSTRAINT fk_quality_batch
        FOREIGN KEY (batch_id)
        REFERENCES raw_data_batches(batch_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_quality_raw_sale
        FOREIGN KEY (raw_sale_id)
        REFERENCES raw_sales(raw_sale_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_quality_severity
        CHECK (
            severity IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    CONSTRAINT chk_quality_status
        CHECK (
            status IN (
                'OPEN',
                'RESOLVED',
                'IGNORED'
            )
        )
);
-- ------------------------------------------------------------
-- 22. DAILY STORE METRICS
-- ------------------------------------------------------------

CREATE TABLE daily_store_metrics (
    metric_id SERIAL PRIMARY KEY,

    store_id INT NOT NULL,

    metric_date DATE NOT NULL,

    total_sales NUMERIC(14,2) NOT NULL DEFAULT 0,

    total_orders INT NOT NULL DEFAULT 0,

    total_returns NUMERIC(14,2) NOT NULL DEFAULT 0,

    total_expenses NUMERIC(14,2) NOT NULL DEFAULT 0,

    net_sales NUMERIC(14,2) NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_daily_metric_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_daily_store_metric
        UNIQUE (store_id, metric_date),

    CONSTRAINT chk_daily_sales
        CHECK (total_sales >= 0),

    CONSTRAINT chk_daily_orders
        CHECK (total_orders >= 0),

    CONSTRAINT chk_daily_returns
        CHECK (total_returns >= 0),

    CONSTRAINT chk_daily_expenses
        CHECK (total_expenses >= 0)
);
-- ------------------------------------------------------------
-- 23. PRODUCT PERFORMANCE
-- ------------------------------------------------------------

CREATE TABLE product_performance (
    performance_id SERIAL PRIMARY KEY,

    product_id INT NOT NULL,

    metric_date DATE NOT NULL,

    units_sold INT NOT NULL DEFAULT 0,

    revenue NUMERIC(14,2) NOT NULL DEFAULT 0,

    units_returned INT NOT NULL DEFAULT 0,

    return_amount NUMERIC(14,2) NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_product_performance_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_product_performance
        UNIQUE (product_id, metric_date),

    CONSTRAINT chk_product_units_sold
        CHECK (units_sold >= 0),

    CONSTRAINT chk_product_revenue
        CHECK (revenue >= 0),

    CONSTRAINT chk_product_units_returned
        CHECK (units_returned >= 0),

    CONSTRAINT chk_product_return_amount
        CHECK (return_amount >= 0)
);
-- ------------------------------------------------------------
-- 25. INVENTORY METRICS
-- ------------------------------------------------------------

CREATE TABLE inventory_metrics (
    metric_id SERIAL PRIMARY KEY,

    inventory_id INT NOT NULL,

    metric_date DATE NOT NULL,

    opening_quantity INT NOT NULL DEFAULT 0,

    closing_quantity INT NOT NULL DEFAULT 0,

    units_sold INT NOT NULL DEFAULT 0,

    units_received INT NOT NULL DEFAULT 0,

    units_returned INT NOT NULL DEFAULT 0,

    stock_value NUMERIC(14,2) NOT NULL DEFAULT 0,

    reorder_level INT NOT NULL DEFAULT 0,

    stock_status VARCHAR(30) NOT NULL DEFAULT 'NORMAL',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_inventory_metric_inventory
        FOREIGN KEY (inventory_id)
        REFERENCES inventory(inventory_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_inventory_metric
        UNIQUE (inventory_id, metric_date),

    CONSTRAINT chk_inventory_opening
        CHECK (opening_quantity >= 0),

    CONSTRAINT chk_inventory_closing
        CHECK (closing_quantity >= 0),

    CONSTRAINT chk_inventory_sold
        CHECK (units_sold >= 0),

    CONSTRAINT chk_inventory_received
        CHECK (units_received >= 0),

    CONSTRAINT chk_inventory_returned
        CHECK (units_returned >= 0),

    CONSTRAINT chk_inventory_stock_value
        CHECK (stock_value >= 0),

    CONSTRAINT chk_inventory_reorder
        CHECK (reorder_level >= 0),

    CONSTRAINT chk_inventory_status
        CHECK (
            stock_status IN (
                'NORMAL',
                'LOW_STOCK',
                'OUT_OF_STOCK',
                'OVERSTOCKED'
            )
        )
);
-- ------------------------------------------------------------
-- 26. ANOMALIES
-- ------------------------------------------------------------

CREATE TABLE anomalies (
    anomaly_id SERIAL PRIMARY KEY,

    store_id INT,

    product_id INT,

    sale_id INT,

    anomaly_type VARCHAR(100) NOT NULL,

    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',

    description TEXT NOT NULL,

    detected_value NUMERIC(14,2),

    expected_value NUMERIC(14,2),

    detection_method VARCHAR(50) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    resolved_at TIMESTAMP,

    CONSTRAINT fk_anomaly_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_anomaly_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_anomaly_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_anomaly_severity
        CHECK (
            severity IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    CONSTRAINT chk_anomaly_status
        CHECK (
            status IN (
                'OPEN',
                'INVESTIGATING',
                'RESOLVED',
                'IGNORED'
            )
        ),

    CONSTRAINT chk_anomaly_detection_method
        CHECK (
            detection_method IN (
                'RULE_BASED',
                'STATISTICAL',
                'ML_MODEL',
                'AI_AGENT'
            )
        )
);
-- ------------------------------------------------------------
-- 27. AI INSIGHTS
-- ------------------------------------------------------------

CREATE TABLE ai_insights (
    insight_id SERIAL PRIMARY KEY,

    anomaly_id INT,

    store_id INT,

    insight_type VARCHAR(100) NOT NULL,

    title VARCHAR(255) NOT NULL,

    insight_text TEXT NOT NULL,

    confidence_score NUMERIC(5,2),

    model_name VARCHAR(100),

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    status VARCHAR(30) NOT NULL DEFAULT 'NEW',

    CONSTRAINT fk_ai_insight_anomaly
        FOREIGN KEY (anomaly_id)
        REFERENCES anomalies(anomaly_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_ai_insight_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_ai_confidence
        CHECK (
            confidence_score IS NULL
            OR (
                confidence_score >= 0
                AND confidence_score <= 100
            )
        ),

    CONSTRAINT chk_ai_insight_status
        CHECK (
            status IN (
                'NEW',
                'REVIEWED',
                'ACCEPTED',
                'DISMISSED'
            )
        )
);
-- ------------------------------------------------------------
-- 28. ACTION ITEMS
-- ------------------------------------------------------------

CREATE TABLE action_items (
    action_item_id SERIAL PRIMARY KEY,

    anomaly_id INT,

    insight_id INT,

    store_id INT,

    assigned_user_id INT,

    action_type VARCHAR(100) NOT NULL,

    title VARCHAR(255) NOT NULL,

    description TEXT NOT NULL,

    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    due_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    CONSTRAINT fk_action_anomaly
        FOREIGN KEY (anomaly_id)
        REFERENCES anomalies(anomaly_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_action_insight
        FOREIGN KEY (insight_id)
        REFERENCES ai_insights(insight_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_action_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_action_user
        FOREIGN KEY (assigned_user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_action_priority
        CHECK (
            priority IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    CONSTRAINT chk_action_status
        CHECK (
            status IN (
                'OPEN',
                'IN_PROGRESS',
                'COMPLETED',
                'CANCELLED'
            )
        )
);
-- ------------------------------------------------------------
-- 29. AUTOMATION RUNS
-- ------------------------------------------------------------

CREATE TABLE automation_runs (
    run_id SERIAL PRIMARY KEY,

    workflow_name VARCHAR(150) NOT NULL,

    trigger_type VARCHAR(50) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'RUNNING',

    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    records_processed INT DEFAULT 0,

    records_created INT DEFAULT 0,

    error_message TEXT,

    CONSTRAINT chk_automation_trigger
        CHECK (
            trigger_type IN (
                'MANUAL',
                'SCHEDULED',
                'EVENT',
                'AGENT'
            )
        ),

    CONSTRAINT chk_automation_status
        CHECK (
            status IN (
                'RUNNING',
                'COMPLETED',
                'FAILED',
                'CANCELLED'
            )
        ),

    CONSTRAINT chk_records_processed
        CHECK (records_processed >= 0),

    CONSTRAINT chk_records_created
        CHECK (records_created >= 0)
);
-- ------------------------------------------------------------
-- 30. SYSTEM LOGS
-- ------------------------------------------------------------

CREATE TABLE system_logs (
    log_id SERIAL PRIMARY KEY,

    log_level VARCHAR(20) NOT NULL,

    module VARCHAR(100) NOT NULL,

    message TEXT NOT NULL,

    user_id INT,

    store_id INT,

    related_record_id INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_log_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_log_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_log_level
        CHECK (
            log_level IN (
                'DEBUG',
                'INFO',
                'WARNING',
                'ERROR',
                'CRITICAL'
            )
        )
);
-- ------------------------------------------------------------
-- 18. LOGIN EVENTS
-- ------------------------------------------------------------

CREATE TABLE login_events (
    login_event_id SERIAL PRIMARY KEY,

    user_id INT NOT NULL,

    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    ip_address VARCHAR(45),

    device_info TEXT,

    login_status VARCHAR(30) NOT NULL,

    failure_reason TEXT,

    CONSTRAINT fk_login_event_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_login_status
        CHECK (
            login_status IN (
                'SUCCESS',
                'FAILED'
            )
        )
);
-- ------------------------------------------------------------
-- 19. RAW DATA BATCHES
-- ------------------------------------------------------------

CREATE TABLE raw_data_batches (
    batch_id SERIAL PRIMARY KEY,

    source_name VARCHAR(100) NOT NULL,

    source_type VARCHAR(50) NOT NULL,

    file_name VARCHAR(255),

    record_count INT,

    ingestion_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    ingestion_completed_at TIMESTAMP,

    status VARCHAR(30) NOT NULL DEFAULT 'RECEIVED',

    error_message TEXT,

    CONSTRAINT chk_raw_source_type
        CHECK (
            source_type IN (
                'CSV',
                'API',
                'DATABASE',
                'ERP'
            )
        ),

    CONSTRAINT chk_raw_batch_status
        CHECK (
            status IN (
                'RECEIVED',
                'PROCESSING',
                'COMPLETED',
                'FAILED'
            )
        ),

    CONSTRAINT chk_raw_record_count
        CHECK (record_count >= 0)
);
-- ------------------------------------------------------------
-- 20. RAW SALES
-- ------------------------------------------------------------

CREATE TABLE raw_sales (
    raw_sale_id SERIAL PRIMARY KEY,

    batch_id INT,

    source_row_number INT,

    invoice_number VARCHAR(100),

    sale_date_raw VARCHAR(100),

    store_code_raw VARCHAR(100),

    customer_code_raw VARCHAR(100),

    product_code_raw VARCHAR(100),

    quantity_raw VARCHAR(100),

    unit_price_raw VARCHAR(100),

    total_amount_raw VARCHAR(100),

    ingestion_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    validation_error TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_raw_sale_batch
        FOREIGN KEY (batch_id)
        REFERENCES raw_data_batches(batch_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_raw_sale_status
        CHECK (
            ingestion_status IN (
                'PENDING',
                'VALID',
                'INVALID',
                'PROCESSED'
            )
        )
);
-- ------------------------------------------------------------
-- 21. DATA QUALITY ISSUES
-- ------------------------------------------------------------

CREATE TABLE data_quality_issues (
    issue_id SERIAL PRIMARY KEY,

    batch_id INT,

    raw_sale_id INT,

    issue_type VARCHAR(100) NOT NULL,

    issue_description TEXT NOT NULL,

    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    resolved_at TIMESTAMP,

    CONSTRAINT fk_quality_batch
        FOREIGN KEY (batch_id)
        REFERENCES raw_data_batches(batch_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_quality_raw_sale
        FOREIGN KEY (raw_sale_id)
        REFERENCES raw_sales(raw_sale_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_quality_severity
        CHECK (
            severity IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    CONSTRAINT chk_quality_status
        CHECK (
            status IN (
                'OPEN',
                'RESOLVED',
                'IGNORED'
            )
        )
);
-- ------------------------------------------------------------
-- 22. DAILY STORE METRICS
-- ------------------------------------------------------------

CREATE TABLE daily_store_metrics (
    metric_id SERIAL PRIMARY KEY,

    store_id INT NOT NULL,

    metric_date DATE NOT NULL,

    total_sales NUMERIC(14,2) NOT NULL DEFAULT 0,

    total_orders INT NOT NULL DEFAULT 0,

    total_returns NUMERIC(14,2) NOT NULL DEFAULT 0,

    total_expenses NUMERIC(14,2) NOT NULL DEFAULT 0,

    net_sales NUMERIC(14,2) NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_daily_metric_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_daily_store_metric
        UNIQUE (store_id, metric_date),

    CONSTRAINT chk_daily_sales
        CHECK (total_sales >= 0),

    CONSTRAINT chk_daily_orders
        CHECK (total_orders >= 0),

    CONSTRAINT chk_daily_returns
        CHECK (total_returns >= 0),

    CONSTRAINT chk_daily_expenses
        CHECK (total_expenses >= 0)
);
-- ------------------------------------------------------------
-- 23. PRODUCT PERFORMANCE
-- ------------------------------------------------------------

CREATE TABLE product_performance (
    performance_id SERIAL PRIMARY KEY,

    product_id INT NOT NULL,

    metric_date DATE NOT NULL,

    units_sold INT NOT NULL DEFAULT 0,

    revenue NUMERIC(14,2) NOT NULL DEFAULT 0,

    units_returned INT NOT NULL DEFAULT 0,

    return_amount NUMERIC(14,2) NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_product_performance_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_product_performance
        UNIQUE (product_id, metric_date),

    CONSTRAINT chk_product_units_sold
        CHECK (units_sold >= 0),

    CONSTRAINT chk_product_revenue
        CHECK (revenue >= 0),

    CONSTRAINT chk_product_units_returned
        CHECK (units_returned >= 0),

    CONSTRAINT chk_product_return_amount
        CHECK (return_amount >= 0)
);
-- ------------------------------------------------------------
-- 24. CUSTOMER METRICS
-- ------------------------------------------------------------

CREATE TABLE customer_metrics (
    metric_id SERIAL PRIMARY KEY,

    customer_id INT NOT NULL,

    metric_date DATE NOT NULL,

    total_orders INT NOT NULL DEFAULT 0,

    total_spent NUMERIC(14,2) NOT NULL DEFAULT 0,

    total_items_purchased INT NOT NULL DEFAULT 0,

    total_returns INT NOT NULL DEFAULT 0,

    total_refund_amount NUMERIC(14,2) NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_customer_metric_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_customer_metric
        UNIQUE (customer_id, metric_date),

    CONSTRAINT chk_customer_orders
        CHECK (total_orders >= 0),

    CONSTRAINT chk_customer_spent
        CHECK (total_spent >= 0),

    CONSTRAINT chk_customer_items
        CHECK (total_items_purchased >= 0),

    CONSTRAINT chk_customer_returns
        CHECK (total_returns >= 0),

    CONSTRAINT chk_customer_refund
        CHECK (total_refund_amount >= 0)
);
-- ------------------------------------------------------------
-- 25. INVENTORY METRICS
-- ------------------------------------------------------------

CREATE TABLE inventory_metrics (
    metric_id SERIAL PRIMARY KEY,

    inventory_id INT NOT NULL,

    metric_date DATE NOT NULL,

    opening_quantity INT NOT NULL DEFAULT 0,

    closing_quantity INT NOT NULL DEFAULT 0,

    units_sold INT NOT NULL DEFAULT 0,

    units_received INT NOT NULL DEFAULT 0,

    units_returned INT NOT NULL DEFAULT 0,

    stock_value NUMERIC(14,2) NOT NULL DEFAULT 0,

    reorder_level INT NOT NULL DEFAULT 0,

    stock_status VARCHAR(30) NOT NULL DEFAULT 'NORMAL',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_inventory_metric_inventory
        FOREIGN KEY (inventory_id)
        REFERENCES inventory(inventory_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_inventory_metric
        UNIQUE (inventory_id, metric_date),

    CONSTRAINT chk_inventory_opening
        CHECK (opening_quantity >= 0),

    CONSTRAINT chk_inventory_closing
        CHECK (closing_quantity >= 0),

    CONSTRAINT chk_inventory_sold
        CHECK (units_sold >= 0),

    CONSTRAINT chk_inventory_received
        CHECK (units_received >= 0),

    CONSTRAINT chk_inventory_returned
        CHECK (units_returned >= 0),

    CONSTRAINT chk_inventory_stock_value
        CHECK (stock_value >= 0),

    CONSTRAINT chk_inventory_reorder
        CHECK (reorder_level >= 0),

    CONSTRAINT chk_inventory_status
        CHECK (
            stock_status IN (
                'NORMAL',
                'LOW_STOCK',
                'OUT_OF_STOCK',
                'OVERSTOCKED'
            )
        )
);
-- ------------------------------------------------------------
-- 26. ANOMALIES
-- ------------------------------------------------------------

CREATE TABLE anomalies (
    anomaly_id SERIAL PRIMARY KEY,

    store_id INT,

    product_id INT,

    sale_id INT,

    anomaly_type VARCHAR(100) NOT NULL,

    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',

    description TEXT NOT NULL,

    detected_value NUMERIC(14,2),

    expected_value NUMERIC(14,2),

    detection_method VARCHAR(50) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    resolved_at TIMESTAMP,

    CONSTRAINT fk_anomaly_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_anomaly_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_anomaly_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales(sale_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_anomaly_severity
        CHECK (
            severity IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    CONSTRAINT chk_anomaly_status
        CHECK (
            status IN (
                'OPEN',
                'INVESTIGATING',
                'RESOLVED',
                'IGNORED'
            )
        ),

    CONSTRAINT chk_anomaly_detection_method
        CHECK (
            detection_method IN (
                'RULE_BASED',
                'STATISTICAL',
                'ML_MODEL',
                'AI_AGENT'
            )
        )
);
-- ------------------------------------------------------------
-- 27. AI INSIGHTS
-- ------------------------------------------------------------

CREATE TABLE ai_insights (
    insight_id SERIAL PRIMARY KEY,

    anomaly_id INT,

    store_id INT,

    insight_type VARCHAR(100) NOT NULL,

    title VARCHAR(255) NOT NULL,

    insight_text TEXT NOT NULL,

    confidence_score NUMERIC(5,2),

    model_name VARCHAR(100),

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    status VARCHAR(30) NOT NULL DEFAULT 'NEW',

    CONSTRAINT fk_ai_insight_anomaly
        FOREIGN KEY (anomaly_id)
        REFERENCES anomalies(anomaly_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_ai_insight_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_ai_confidence
        CHECK (
            confidence_score IS NULL
            OR (
                confidence_score >= 0
                AND confidence_score <= 100
            )
        ),

    CONSTRAINT chk_ai_insight_status
        CHECK (
            status IN (
                'NEW',
                'REVIEWED',
                'ACCEPTED',
                'DISMISSED'
            )
        )
);
-- ------------------------------------------------------------
-- 28. ACTION ITEMS
-- ------------------------------------------------------------

CREATE TABLE action_items (
    action_item_id SERIAL PRIMARY KEY,

    anomaly_id INT,

    insight_id INT,

    store_id INT,

    assigned_user_id INT,

    action_type VARCHAR(100) NOT NULL,

    title VARCHAR(255) NOT NULL,

    description TEXT NOT NULL,

    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    due_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    CONSTRAINT fk_action_anomaly
        FOREIGN KEY (anomaly_id)
        REFERENCES anomalies(anomaly_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_action_insight
        FOREIGN KEY (insight_id)
        REFERENCES ai_insights(insight_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_action_store
        FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_action_user
        FOREIGN KEY (assigned_user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_action_priority
        CHECK (
            priority IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    CONSTRAINT chk_action_status
        CHECK (
            status IN (
                'OPEN',
                'IN_PROGRESS',
                'COMPLETED',
                'CANCELLED'
            )
        )
);
-- ------------------------------------------------------------
-- 29. AUTOMATION RUNS
-- ------------------------------------------------------------

CREATE TABLE automation_runs (
    run_id SERIAL PRIMARY KEY,

    workflow_name VARCHAR(150) NOT NULL,

    trigger_type VARCHAR(50) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'RUNNING',

    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    records_processed INT DEFAULT 0,

    records_created INT DEFAULT 0,

    error_message TEXT,

    CONSTRAINT chk_automation_trigger
        CHECK (
            trigger_type IN (
                'MANUAL',
                'SCHEDULED',
                'EVENT',
                'AGENT'
            )
        ),

    CONSTRAINT chk_automation_status
        CHECK (
            status IN (
                'RUNNING',
                'COMPLETED',
                'FAILED',
                'CANCELLED'
            )
        ),

    CONSTRAINT chk_records_processed
        CHECK (records_processed >= 0),

    CONSTRAINT chk_records_created
        CHECK (records_created >= 0)
);
-- ------------------------------------------------------------
-- 30. AUDIT LOGS
-- ------------------------------------------------------------

CREATE TABLE audit_logs (
    audit_id SERIAL PRIMARY KEY,

    user_id INT,

    action VARCHAR(50) NOT NULL,

    entity_type VARCHAR(100) NOT NULL,

    entity_id INT,

    old_values JSONB,

    new_values JSONB,

    ip_address VARCHAR(45),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_audit_action
        CHECK (
            action IN (
                'CREATE',
                'UPDATE',
                'DELETE',
                'LOGIN',
                'LOGOUT',
                'APPROVE',
                'REJECT'
            )
        )
);