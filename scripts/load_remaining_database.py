import os
import pandas as pd
import psycopg2
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[1]

DATASET_DIR = REPO_ROOT / "data" / "FinSight_synthetic_ERP_dataset_v1"

RAW = DATASET_DIR / "raw"
PROCESSED = DATASET_DIR / "processed" / "sales"


# ============================================================
# DATABASE CONFIG
# ============================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "finsight"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

def conn():
    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# 1. SALES
# ============================================================

def load_sales():

    path = os.path.join(PROCESSED, "sales.csv")

    df = pd.read_csv(path)

    df["status"] = df["status"].astype(str).str.upper()

    c = conn()
    cur = c.cursor()

    for _, r in df.iterrows():

        cur.execute("""
            INSERT INTO sales
            (
                sale_id,
                store_id,
                customer_id,
                user_id,
                invoice_number,
                sale_date,
                subtotal,
                discount_amount,
                tax_amount,
                total_amount,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

            ON CONFLICT (sale_id) DO NOTHING
        """, (
            int(r.sale_id),
            int(r.store_id),

            None if pd.isna(r.customer_id)
            else int(r.customer_id),

            None if pd.isna(r.user_id)
            else int(r.user_id),

            r.invoice_number,
            r.sale_date,

            float(r.subtotal),
            float(r.discount),
            float(r.tax),
            float(r.total_amount),

            r.status
        ))

    c.commit()

    cur.close()
    c.close()

    print(f"Sales loaded: {len(df)}")


# ============================================================
# 2. SALE ITEMS
# ============================================================

def load_sale_items():

    path = os.path.join(PROCESSED, "sale_items.csv")

    df = pd.read_csv(path)

    c = conn()
    cur = c.cursor()

    for _, r in df.iterrows():

        cur.execute("""
            INSERT INTO sale_items
            (
                sale_item_id,
                sale_id,
                product_id,
                quantity,
                unit_price,
                discount_amount,
                line_total
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)

            ON CONFLICT (sale_item_id) DO NOTHING
        """, (
            int(r.sale_item_id),
            int(r.sale_id),
            int(r.product_id),
            int(r.quantity),
            float(r.unit_price),
            float(r.discount),
            float(r.line_total)
        ))

    c.commit()

    cur.close()
    c.close()

    print(f"Sale items loaded: {len(df)}")


# ============================================================
# 3. PAYMENT CONSTRAINT
# ============================================================

def prepare_payment_constraint(cur):

    cur.execute("""
        ALTER TABLE payments
        DROP CONSTRAINT IF EXISTS chk_payment_method
    """)

    cur.execute("""
        ALTER TABLE payments
        ADD CONSTRAINT chk_payment_method CHECK (
            payment_method IN (
                'CASH',
                'CARD',
                'UPI',
                'NET_BANKING',
                'WALLET',
                'BANK_TRANSFER'
            )
        )
    """)


# ============================================================
# 4. PAYMENTS
# ============================================================

def load_payments():

    path = os.path.join(
        RAW,
        "sales",
        "payments.csv"
    )

    df = pd.read_csv(path)

    c = conn()
    cur = c.cursor()

    prepare_payment_constraint(cur)

    for _, r in df.iterrows():

        status = str(
            r.payment_status
        ).strip().upper()

        # Source: SUCCESS
        # Database: COMPLETED

        if status == "SUCCESS":
            status = "COMPLETED"

        elif status == "PROCESSED":
            status = "COMPLETED"

        cur.execute("""
            INSERT INTO payments
            (
                payment_id,
                sale_id,
                payment_method,
                amount,
                payment_date,
                transaction_reference,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)

            ON CONFLICT (payment_id) DO NOTHING
        """, (
            int(r.payment_id),
            int(r.sale_id),
            str(r.payment_method).strip().upper(),
            float(r.amount),
            r.paid_at,
            r.transaction_reference,
            status
        ))

    c.commit()

    cur.close()
    c.close()

    print(f"Payments loaded: {len(df)}")


# ============================================================
# 5. RETURNS
# ============================================================

def load_returns():

    path = os.path.join(
        RAW,
        "sales",
        "returns.csv"
    )

    df = pd.read_csv(path)

    df["status"] = (
        df["status"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    c = conn()
    cur = c.cursor()

    for _, r in df.iterrows():

        cur.execute("""
            INSERT INTO returns
            (
                return_id,
                sale_id,
                customer_id,
                return_date,
                reason,
                status,
                total_refund_amount
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)

            ON CONFLICT (return_id) DO NOTHING
        """, (
            int(r.return_id),
            int(r.sale_id),

            None if pd.isna(r.customer_id)
            else int(r.customer_id),

            r.return_date,
            r.reason,
            r.status,
            float(r.total_refund)
        ))

    c.commit()

    cur.close()
    c.close()

    print(f"Returns loaded: {len(df)}")


# ============================================================
# 6. RETURN ITEMS
# ============================================================

def load_return_items():

    path = os.path.join(
        RAW,
        "sales",
        "return_items.csv"
    )

    df = pd.read_csv(path)

    c = conn()
    cur = c.cursor()

    # --------------------------------------------------------
    # Map:
    #
    # return_id -> sale_id
    # sale_id + product_id -> sale_item_id
    # --------------------------------------------------------

    cur.execute("""
        SELECT
            return_id,
            sale_id
        FROM returns
    """)

    return_map = {
        int(return_id): int(sale_id)
        for return_id, sale_id in cur.fetchall()
    }

    cur.execute("""
        SELECT
            sale_item_id,
            sale_id,
            product_id
        FROM sale_items
    """)

    item_map = {}

    for sale_item_id, sale_id, product_id in cur.fetchall():

        key = (
            int(sale_id),
            int(product_id)
        )

        item_map.setdefault(
            key,
            []
        ).append(
            int(sale_item_id)
        )

    loaded = 0
    skipped = 0

    for _, r in df.iterrows():

        return_id = int(r.return_id)

        sale_id = return_map.get(
            return_id
        )

        if sale_id is None:

            skipped += 1
            continue

        key = (
            sale_id,
            int(r.product_id)
        )

        candidates = item_map.get(
            key,
            []
        )

        if not candidates:

            skipped += 1
            continue

        sale_item_id = candidates[0]

        cur.execute("""
            INSERT INTO return_items
            (
                return_item_id,
                return_id,
                sale_item_id,
                quantity,
                refund_amount
            )
            VALUES (%s,%s,%s,%s,%s)

            ON CONFLICT (return_item_id) DO NOTHING
        """, (
            int(r.return_item_id),
            return_id,
            sale_item_id,
            int(r.quantity),
            float(r.refund_amount)
        ))

        loaded += 1

    c.commit()

    cur.close()
    c.close()

    print(
        f"Return items loaded: {loaded}; "
        f"skipped: {skipped}"
    )


# ============================================================
# 7. REFUND METHOD CONSTRAINT
# ============================================================

def prepare_refund_constraint(cur):

    cur.execute("""
        ALTER TABLE refunds
        DROP CONSTRAINT IF EXISTS chk_refund_method
    """)

    cur.execute("""
        ALTER TABLE refunds
        ADD CONSTRAINT chk_refund_method CHECK (
            refund_method IN (
                'CASH',
                'CARD',
                'UPI',
                'NET_BANKING',
                'WALLET',
                'BANK_TRANSFER'
            )
        )
    """)


# ============================================================
# 8. REFUNDS
# ============================================================

def load_refunds():

    path = os.path.join(
        RAW,
        "sales",
        "refunds.csv"
    )

    df = pd.read_csv(path)

    c = conn()
    cur = c.cursor()

    prepare_refund_constraint(cur)

    for _, r in df.iterrows():

        # ----------------------------------------------------
        # Normalize refund status
        #
        # Source:
        # PROCESSED
        #
        # Database:
        # COMPLETED
        # ----------------------------------------------------

        source_status = (
            str(r.refund_status)
            .strip()
            .upper()
        )

        if source_status in (
            "SUCCESS",
            "PROCESSED",
            "COMPLETED"
        ):

            status = "COMPLETED"

        elif source_status == "PENDING":

            status = "PENDING"

        elif source_status == "FAILED":

            status = "FAILED"

        else:

            status = source_status

        cur.execute("""
            INSERT INTO refunds
            (
                refund_id,
                return_id,
                refund_amount,
                refund_method,
                refund_date,
                transaction_reference,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)

            ON CONFLICT (refund_id) DO NOTHING
        """, (
            int(r.refund_id),
            int(r.return_id),
            float(r.amount),
            str(r.refund_method)
                .strip()
                .upper(),
            r.processed_at,

            # Source does not contain
            # transaction_reference
            None,

            status
        ))

    c.commit()

    cur.close()
    c.close()

    print(f"Refunds loaded: {len(df)}")


# ============================================================
# 9. EXPENSES
# ============================================================

def load_expenses():

    path = os.path.join(
        RAW,
        "expenses",
        "expenses.csv"
    )

    df = pd.read_csv(path)

    c = conn()
    cur = c.cursor()

    for _, r in df.iterrows():

        cur.execute("""
            INSERT INTO expenses
            (
                expense_id,
                store_id,
                category,
                amount,
                description,
                expense_date
            )
            VALUES (%s,%s,%s,%s,%s,%s)

            ON CONFLICT (expense_id) DO NOTHING
        """, (
            int(r.expense_id),
            int(r.store_id),
            r.category,
            float(r.amount),
            r.description,
            r.expense_date
        ))

    c.commit()

    cur.close()
    c.close()

    print(f"Expenses loaded: {len(df)}")


# ============================================================
# 10. LOGIN EVENTS
# ============================================================

def load_login_events():

    path = os.path.join(
        RAW,
        "customers",
        "login_events.csv"
    )

    df = pd.read_csv(path)

    c = conn()
    cur = c.cursor()

    for _, r in df.iterrows():

        status = (
            str(r.login_status)
            .strip()
            .upper()
        )

        cur.execute("""
            INSERT INTO login_events
            (
                login_event_id,
                user_id,
                login_time,
                logout_time,
                ip_address,
                device_info,
                login_status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)

            ON CONFLICT (login_event_id) DO NOTHING
        """, (
            int(r.login_event_id),
            int(r.user_id),
            r.login_time,

            None if pd.isna(r.logout_time)
            else r.logout_time,

            r.ip_address,
            r.device_info,
            status
        ))

    c.commit()

    cur.close()
    c.close()

    print(
        f"Login events loaded: {len(df)}"
    )


# ============================================================
# 11. VERIFY DATABASE
# ============================================================

def verify():

    tables = [
        "companies",
        "stores",
        "users",
        "categories",
        "customers",
        "products",
        "suppliers",
        "supplier_products",
        "inventory",
        "inventory_movements",
        "sales",
        "sale_items",
        "payments",
        "returns",
        "return_items",
        "refunds",
        "expenses",
        "login_events"
    ]

    c = conn()
    cur = c.cursor()

    print()
    print("DATABASE COUNTS")
    print("-" * 40)

    for table in tables:

        cur.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cur.fetchone()[0]

        print(
            f"{table:25} {count}"
        )

    cur.close()
    c.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "=== FinSight remaining database loader ==="
    )

    load_sales()

    load_sale_items()

    load_payments()

    load_returns()

    load_return_items()

    load_refunds()

    load_expenses()

    load_login_events()

    verify()

    print()
    print(
        "All operational ERP tables loaded successfully."
    )