import pandas as pd


def calculate_kpis(df: pd.DataFrame):

    kpis = {}

    kpis["total_orders"] = len(df)
    kpis["total_columns"] = len(df.columns)

    if "price" in df.columns and "quantity" in df.columns:
        df["revenue"] = df["price"] * df["quantity"]
        kpis["total_revenue"] = float(df["revenue"].sum())
        kpis["average_order_value"] = float(df["revenue"].mean())

    if "product" in df.columns and "revenue" in df.columns:
        product_revenue = df.groupby("product")["revenue"].sum()
        kpis["top_product"] = product_revenue.idxmax()
        kpis["top_product_revenue"] = float(product_revenue.max())

    if "category" in df.columns and "revenue" in df.columns:
        kpis["revenue_by_category"] = df.groupby("category")["revenue"].sum().to_dict()

    if "customer_id" in df.columns:
        kpis["total_customers"] = df["customer_id"].nunique()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        kpis["date_range"] = {
            "start": str(df["date"].min()),
            "end": str(df["date"].max())
        }

    return kpis