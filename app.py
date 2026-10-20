from pathlib import Path

import pandas as pd
import plotly.express as px
from flask import Flask, flash, redirect, render_template, request, url_for

# Keep file paths relative to this project so it runs from any folder.
PROJECT_FOLDER = Path(__file__).parent
DATA_FOLDER = PROJECT_FOLDER / "data"
UPLOAD_FOLDER = PROJECT_FOLDER / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = "local-development-key"


def load_data():
    """Load the uploaded CSV, or the sample file when no upload exists."""
    uploaded_file = UPLOAD_FOLDER / "current.csv"
    sample_file = DATA_FOLDER / "sample_superstore.csv"

    file_to_read = uploaded_file if uploaded_file.exists() else sample_file
    data = pd.read_csv(file_to_read)

    # Superstore files usually use these columns. Convert them to usable types.
    for column in ["Sales", "Profit", "Discount", "Quantity"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    if "Order Date" in data.columns:
        data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")

    # Sales and Profit are needed for the main calculations.
    if "Sales" not in data.columns or "Profit" not in data.columns:
        raise ValueError("The CSV needs both Sales and Profit columns.")

    data = data.dropna(subset=["Sales", "Profit"]).copy()

    # Some charts use these columns. Add a simple fallback if a file lacks one.
    optional_defaults = {
        "Category": "Not provided",
        "Sub-Category": "Not provided",
        "Region": "Not provided",
        "Customer Name": "Unknown",
        "Order ID": None,
        "Quantity": 0,
        "Discount": 0,
    }
    for column, default in optional_defaults.items():
        if column not in data.columns:
            data[column] = default

    return data


def format_money(number):
    """Show currency values without unnecessary decimal places."""
    return "${:,.0f}".format(number)


def format_percent(number):
    """Convert a decimal such as 0.25 to '25.0%'."""
    return "{:.1f}%".format(number * 100)


def make_dashboard(data):
    """Calculate the numbers and charts used by the webpage."""
    sales = data["Sales"].sum()
    profit = data["Profit"].sum()
    margin = profit / sales if sales else 0
    order_count = data["Order ID"].nunique() if data["Order ID"].notna().any() else len(data)

    # The first chart uses months when the dataset includes valid order dates.
    if "Order Date" in data.columns and data["Order Date"].notna().any():
        dated_rows = data.dropna(subset=["Order Date"]).copy()
        dated_rows["Month"] = dated_rows["Order Date"].dt.to_period("M").dt.to_timestamp()
        trend_data = dated_rows.groupby("Month", as_index=False)[["Sales", "Profit"]].sum()

        trend_chart = px.line(
            trend_data,
            x="Month",
            y=["Sales", "Profit"],
            color_discrete_map={"Sales": "#C66A4E", "Profit": "#789184"},
        )
        trend_title = "Sales and profit over time"
        trend_note = "Look for months where sales rise but profit does not keep pace."
    else:
        trend_data = data.groupby("Category", as_index=False)[["Sales", "Profit"]].sum()
        trend_chart = px.bar(
            trend_data,
            x="Category",
            y=["Sales", "Profit"],
            barmode="group",
            color_discrete_map={"Sales": "#C66A4E", "Profit": "#789184"},
        )
        trend_title = "Sales and profit by category"
        trend_note = "Add valid Order Date values to see monthly trends."

    trend_chart.update_layout(
        template="plotly_white",
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color="#202B2A", size=12),
        legend=dict(orientation="h", y=1.02, x=0),
    )
    trend_chart.update_yaxes(tickprefix="$", tickformat=",.0f", gridcolor="#E8E5DD")

    # Sort categories so weaker profit areas are easy to spot.
    category_data = data.groupby("Category", as_index=False)[["Sales", "Profit"]].sum()
    category_data = category_data.sort_values("Profit")

    category_chart = px.bar(
        category_data,
        x="Profit",
        y="Category",
        orientation="h",
        color="Profit",
        color_continuous_scale=["#C66A4E", "#E7D8BD", "#789184"],
    )
    category_chart.update_layout(
        template="plotly_white",
        height=260,
        margin=dict(l=5, r=5, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color="#202B2A", size=12),
        coloraxis_showscale=False,
    )
    category_chart.update_xaxes(tickprefix="$", tickformat=",.0f", gridcolor="#E8E5DD")

    # Compare sub-categories to make a short review list.
    subcategory_data = data.groupby("Sub-Category", as_index=False).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Average_Discount=("Discount", "mean"),
    )
    subcategory_data["Margin"] = subcategory_data.apply(
        lambda row: row["Profit"] / row["Sales"] if row["Sales"] else 0,
        axis=1,
    )
    subcategory_data = subcategory_data.sort_values("Profit")

    worst = subcategory_data.head(5)
    best = subcategory_data.tail(5)
    review_rows = pd.concat([worst, best]).drop_duplicates("Sub-Category")

    table_rows = []
    for _, row in review_rows.iterrows():
        if row["Profit"] < 0:
            status = "Review"
        elif row["Margin"] > margin:
            status = "Strong"
        else:
            status = "Monitor"

        table_rows.append({
            "subcategory": row["Sub-Category"],
            "sales": format_money(row["Sales"]),
            "profit": format_money(row["Profit"]),
            "margin": format_percent(row["Margin"]),
            "discount": format_percent(row["Average_Discount"]),
            "status": status,
        })

    lowest_profit = subcategory_data.iloc[0]
    highest_profit = subcategory_data.iloc[-1]

    # This is descriptive analysis: it shows patterns, not cause and effect.
    high_discount_rows = data[data["Discount"] >= data["Discount"].quantile(0.75)]
    high_discount_profit = high_discount_rows["Profit"].sum()

    return {
        "kpis": [
            {"label": "Net sales", "value": format_money(sales), "note": "Total recorded sales"},
            {"label": "Profit", "value": format_money(profit), "note": "Total recorded profit"},
            {"label": "Profit margin", "value": format_percent(margin), "note": "Profit divided by sales"},
            {"label": "Orders", "value": "{:,.0f}".format(order_count), "note": "Distinct order IDs"},
        ],
        "secondary": [
            {"label": "Customers", "value": "{:,.0f}".format(data["Customer Name"].nunique())},
            {"label": "Units sold", "value": "{:,.0f}".format(data["Quantity"].sum())},
            {"label": "Average discount", "value": format_percent(data["Discount"].mean())},
            {"label": "Rows analysed", "value": "{:,.0f}".format(len(data))},
        ],
        "trend_plot": trend_chart.to_json(),
        "category_plot": category_chart.to_json(),
        "trend_title": trend_title,
        "trend_note": trend_note,
        "margin_text": (
            "For every $100 in sales, the data records about ${:.2f} in profit.".format(margin * 100)
            if sales else "Sales are zero, so profit margin cannot be calculated."
        ),
        "insights": [
            {
                "label": "Watch list",
                "title": str(lowest_profit["Sub-Category"]),
                "body": "Lowest total profit in the sub-category breakdown: {} from {} in sales.".format(
                    format_money(lowest_profit["Profit"]), format_money(lowest_profit["Sales"])
                ),
            },
            {
                "label": "Bright spot",
                "title": str(highest_profit["Sub-Category"]),
                "body": "Highest total profit in the sub-category breakdown: {}.".format(
                    format_money(highest_profit["Profit"])
                ),
            },
            {
                "label": "Discount check",
                "title": "Higher-discount rows",
                "body": "{} total profit across rows in the top quarter of discounts. Investigate further before drawing conclusions.".format(
                    format_money(high_discount_profit)
                ),
            },
        ],
        "table_rows": table_rows,
        "source_note": "Figures are calculated from the loaded CSV. Patterns are leads for investigation, not proof of cause.",
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        csv_file = request.files.get("dataset")

        if not csv_file or not csv_file.filename:
            flash("Choose a CSV file first.", "error")
            return redirect(url_for("index"))

        if not csv_file.filename.lower().endswith(".csv"):
            flash("Please upload a CSV file.", "error")
            return redirect(url_for("index"))

        try:
            # Check the file before saving it as the active dataset.
            import io
            new_data = pd.read_csv(io.BytesIO(csv_file.read()))
            if "Sales" not in new_data.columns or "Profit" not in new_data.columns:
                raise ValueError("The file must include Sales and Profit columns.")

            new_data.to_csv(UPLOAD_FOLDER / "current.csv", index=False)
            flash("Dataset loaded. The dashboard now uses your CSV.", "success")
        except Exception as error:
            flash("Could not load the file: {}".format(error), "error")

        return redirect(url_for("index"))

    try:
        data = load_data()
        dashboard = make_dashboard(data)
        using_upload = (UPLOAD_FOLDER / "current.csv").exists()
        data_label = "Your uploaded dataset" if using_upload else "Included demo data"
        return render_template(
            "index.html",
            dashboard=dashboard,
            data_label=data_label,
            row_count=len(data),
        )
    except Exception as error:
        flash(str(error), "error")
        return render_template("index.html", dashboard=None, data_label="Data needs attention", row_count=0)


@app.route("/reset")
def reset():
    uploaded_file = UPLOAD_FOLDER / "current.csv"
    if uploaded_file.exists():
        uploaded_file.unlink()
    flash("Back to the included demo data.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # debug=True is convenient during local development; don't use it for public deployment.
    app.run(debug=True)
