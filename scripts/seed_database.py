import os
import pandas as pd
import psycopg2


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "finsight"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
    "FinSight_synthetic_ERP_dataset_v1",
    "reference"
)


# ------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )


# ------------------------------------------------------------
# LOAD COMPANIES
# ------------------------------------------------------------

def load_companies():

    file_path = os.path.join(DATA_DIR, "companies.csv")

    print(f"Reading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"\nRows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO companies (
                company_id,
                company_name,
                industry
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (company_id)
            DO NOTHING;
            """,
            (
                int(row["company_id"]),
                row["company_name"],
                row["industry"]
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("\nCompanies loaded successfully!")


# ------------------------------------------------------------
# LOAD STORES
# ------------------------------------------------------------

# ------------------------------------------------------------
# LOAD STORES
# ------------------------------------------------------------

def load_stores():

    file_path = os.path.join(DATA_DIR, "stores.csv")

    print(f"\nReading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"Rows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO stores (
                store_id,
                company_id,
                store_name,
                city,
                state
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (store_id)
            DO NOTHING;
            """,
            (
                int(row["store_id"]),
                int(row["company_id"]),
                row["store_name"],
                row["city"],
                row["state"]
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("\nStores loaded successfully!")
    # ------------------------------------------------------------
# LOAD USERS
# ------------------------------------------------------------

def load_users():

    file_path = os.path.join(DATA_DIR, "users.csv")

    print(f"\nReading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"Rows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO users (
                user_id,
                store_id,
                full_name,
                email,
                role,
                is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id)
            DO NOTHING;
            """,
            (
                int(row["user_id"]),
                int(row["store_id"]),
                row["name"],
                row["email"],
                row["role"],
                row["status"].lower() == "active"
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("\nUsers loaded successfully!")
    # ------------------------------------------------------------
# LOAD CUSTOMERS
# ------------------------------------------------------------

def load_customers():

    file_path = os.path.join(DATA_DIR, "customers.csv")

    print(f"\nReading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"Rows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO customers (
                customer_id,
                full_name,
                email,
                phone,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (customer_id)
            DO NOTHING;
            """,
            (
                int(row["customer_id"]),
                row["name"],
                row["email"],
                str(row["phone"]),
                row["created_at"]
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("\nCustomers loaded successfully!")
# ------------------------------------------------------------
# LOAD CATEGORIES
# ------------------------------------------------------------

def load_categories():

    file_path = os.path.join(DATA_DIR, "categories.csv")

    print(f"\nReading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"Rows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO categories (
                category_id,
                category_name
            )
            VALUES (%s, %s)
            ON CONFLICT (category_id)
            DO NOTHING;
            """,
            (
                int(row["category_id"]),
                row["category_name"]
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("\nCategories loaded successfully!")
    # ------------------------------------------------------------
# LOAD PRODUCTS
# ------------------------------------------------------------

def load_products():

    file_path = os.path.join(DATA_DIR, "products.csv")

    print(f"\nReading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"Rows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO products (
                product_id,
                category_id,
                product_name,
                sku,
                unit_price,
                cost_price,
                is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id)
            DO NOTHING;
            """,
            (
                int(row["product_id"]),
                int(row["category_id"]),
                row["product_name"],
                row["sku"],
                float(row["selling_price"]),
                float(row["cost_price"]),
                row["status"].lower() == "active"
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("\nProducts loaded successfully!")
    # ------------------------------------------------------------
# LOAD SUPPLIERS
# ------------------------------------------------------------

def load_suppliers():

    file_path = os.path.join(DATA_DIR, "suppliers.csv")

    print(f"\nReading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"Rows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO suppliers (
                supplier_id,
                supplier_name,
                email
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (supplier_id)
            DO NOTHING;
            """,
            (
                int(row["supplier_id"]),
                row["supplier_name"],
                row["contact_email"]
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("\nSuppliers loaded successfully!")
# ------------------------------------------------------------
# LOAD SUPPLIER PRODUCTS
# ------------------------------------------------------------

def load_supplier_products():

    file_path = os.path.join(DATA_DIR, "supplier_products.csv")

    print(f"\nReading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"Rows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO supplier_products (
                supplier_id,
                product_id,
                supplier_price,
                lead_time_days
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (supplier_id, product_id)
            DO NOTHING;
            """,
            (
                int(row["supplier_id"]),
                int(row["product_id"]),
                float(row["supplier_price"]),
                int(row["lead_time_days"])
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("\nSupplier products loaded successfully!")

def load_inventory():
    print("\nLoading inventory...")

    file_path = os.path.join(
        os.path.dirname(DATA_DIR),
        "raw",
        "inventory",
        "inventory.csv"
    )

    print(f"Reading file: {file_path}")

    df = pd.read_csv(file_path)

    print(f"Found {len(df)} inventory rows")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO inventory (
                inventory_id,
                store_id,
                product_id,
                quantity,
                reorder_level,
                last_updated
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (inventory_id)
            DO NOTHING;
            """,
            (
                int(row["inventory_id"]),
                int(row["store_id"]),
                int(row["product_id"]),
                int(row["quantity"]),
                int(row["reorder_level"]),
                row["updated_at"]
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"Inserted {len(df)} inventory rows.")
    # ------------------------------------------------------------
# LOAD INVENTORY MOVEMENTS
# ------------------------------------------------------------

def load_inventory_movements():

    print("\nLoading inventory movements...")

    file_path = os.path.join(
        os.path.dirname(DATA_DIR),
        "raw",
        "inventory",
        "inventory_movements.csv"
    )

    print(f"Reading file: {file_path}")

    df = pd.read_csv(file_path)

    print("\nColumns found:")
    print(df.columns.tolist())

    print(f"Rows found: {len(df)}")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():

        reference_id = (
            None
            if pd.isna(row["reference_id"])
            else int(row["reference_id"])
        )

        cursor.execute(
            """
            INSERT INTO inventory_movements (
                movement_id,
                store_id,
                product_id,
                movement_type,
                quantity_change,
                reference_type,
                reference_id,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (movement_id)
            DO NOTHING;
            """,
            (
                int(row["movement_id"]),
                int(row["store_id"]),
                int(row["product_id"]),
                row["movement_type"],
                int(row["quantity"]),
                row["reference_type"],
                reference_id,
                row["created_at"]
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(f"\nInventory movements loaded successfully!")
    print(f"Inserted {len(df)} inventory movement rows.")
# MAIN
# ------------------------------------------------------------

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":

    load_companies()
    load_stores()
    load_users()
    load_categories()
    load_customers()
    load_products()
    load_suppliers()
    load_supplier_products()
    load_inventory()
    load_inventory_movements()