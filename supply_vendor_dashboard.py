import streamlit as st
import pandas as pd

# ==========================
# CONFIG – COLUMN NAMES
# ==========================
VENDOR_CODE_COL = "Vendor Code"
VENDOR_NAME_COL = "Vendor Name"
NAME_COL = "Name"
EMAIL_COL = "Email"
PHONE_COL = "Phone Number"
CATEGORY_COL = "Category"
CUISINE_1_COL = "Cuisine type 1"
CUISINE_2_COL = "Cuisine Type 2"
SERVICE_MODEL_COL = "Service Model"
SERVING_CAP_COL = "Serving Capacity"
STATE_COL = "State"
CITY_COL = "City"
AREA_COL = "Area"
OTHER_CITY_COL = "Other City 1"
AREA_1_COL = "Area 1"
CERT_1_COL = "Certification 1"
CERT_2_COL = "Certification 2"
CERT_3_COL = "Certification 3"

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="Vendor Master Dashboard",
    layout="wide",
    page_icon="📊"
)

# ==========================
# LOAD DATA
# ==========================
@st.cache_data
def load_vendor_data(uploaded_file) -> pd.DataFrame:
    """
    Read uploaded file (CSV/XLSX/XLS) and clean up column names.
    Falls back with a friendly error if openpyxl is missing.
    """
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        # Excel case: needs openpyxl in the environment
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        except ImportError:
            st.error(
                "To read Excel files (.xlsx / .xls), this app needs the "
                "`openpyxl` package installed.\n\n"
                "➡️ Either:\n"
                "- Add `openpyxl` to your `requirements.txt` on Streamlit Cloud and redeploy, **or**\n"
                "- Upload the file as a `.csv` instead."
            )
            st.stop()

    df.columns = df.columns.str.strip()
    return df

# ==========================
# HELPERS
# ==========================
def safe_get(row, col, default="-"):
    if col in row and pd.notna(row[col]):
        return row[col]
    return default


def extract_vendor_info(row):
    """Return all display fields for a vendor row as a dict."""
    vendor_code = safe_get(row, VENDOR_CODE_COL)
    vendor_name = safe_get(row, VENDOR_NAME_COL)

    owner_name = safe_get(row, NAME_COL)
    phone = safe_get(row, PHONE_COL)
    email = safe_get(row, EMAIL_COL)

    # Build location from multiple columns
    location_parts = []
    for col in [AREA_COL, AREA_1_COL, CITY_COL, OTHER_CITY_COL, STATE_COL]:
        if col in row and pd.notna(row[col]):
            location_parts.append(str(row[col]))
    location = ", ".join(location_parts) if location_parts else "-"

    category = safe_get(row, CATEGORY_COL)
    cuisine1 = safe_get(row, CUISINE_1_COL, "")
    cuisine2 = safe_get(row, CUISINE_2_COL, "")
    cuisine_parts = [c for c in (cuisine1, cuisine2) if c not in ["", "-"]]
    cuisine_text = " / ".join(cuisine_parts) if cuisine_parts else "-"

    service_model = safe_get(row, SERVICE_MODEL_COL)
    serving_capacity = safe_get(row, SERVING_CAP_COL)

    return {
        "vendor_code": vendor_code,
        "vendor_name": vendor_name,
        "owner_name": owner_name,
        "phone": phone,
        "email": email,
        "location": location,
        "category": category,
        "cuisine_text": cuisine_text,
        "service_model": service_model,
        "serving_capacity": serving_capacity,
    }


def render_owner_and_vendor_boxes(info):
    """Render Owner details 2x2 + Vendor details 2x2 for one vendor."""
    # Owner details
    with st.container(border=True):
        st.subheader("Owner details")

        # Row 1: Owner name | Phone
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.write("**Owner name**")
            st.write(info["owner_name"])
        with r1c2:
            st.write("**Phone number**")
            st.write(info["phone"])

        # Row 2: Email | Location
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.write("**Email**")
            st.write(info["email"])
        with r2c2:
            st.write("**Location**")
            st.write(info["location"])

    # Vendor details
    with st.container(border=True):
        st.subheader("Vendor details")

        # Row 1: Category | Cuisine type
        v_r1c1, v_r1c2 = st.columns(2)
        with v_r1c1:
            st.write("**Category**")
            st.write(info["category"])
        with v_r1c2:
            st.write("**Cuisine type**")
            st.write(info["cuisine_text"])

        # Row 2: Service model | Serving capacity
        v_r2c1, v_r2c2 = st.columns(2)
        with v_r2c1:
            st.write("**Service model**")
            st.write(info["service_model"])
        with v_r2c2:
            st.write("**Serving capacity**")
            st.write(info["serving_capacity"])


# ==========================
# HEADER
# ==========================
st.title("Vendor Master Dashboard")
st.caption("Single source of truth for vendor master data")

# ==========================
# SIDEBAR – UPLOAD & FILTERS
# ==========================
st.sidebar.title("Controls")

# File uploader at the very top of sidebar
uploaded_file = st.sidebar.file_uploader(
    "Upload vendor dashboard data (.csv / .xlsx / .xls)",
    type=["csv", "xlsx", "xls"],
    help="Upload the vendor master file."
)

if uploaded_file is None:
    st.info("⬅️ Upload a CSV or Excel file from the sidebar to see the dashboard.")
    st.stop()

# Load data from uploaded file
df = load_vendor_data(uploaded_file)

st.sidebar.header("Filters")

# Vendor select (used in basic mode)
vendor_list = sorted(df[VENDOR_NAME_COL].dropna().unique().tolist())
selected_vendor = st.sidebar.selectbox(
    "Vendor",
    options=["All Vendors"] + vendor_list,
    index=0
)

# Advanced filter toggle
show_advanced = st.sidebar.toggle("Advanced filters", value=False)

# Advanced search controls (in sidebar)
if show_advanced:
    search_query = st.sidebar.text_input(
        "Search (matches across name, category, location, etc.)",
        value="",
        placeholder="Type to search..."
    )

    # Serving capacity options
    if SERVING_CAP_COL in df.columns:
        serving_caps_raw = (
            df[SERVING_CAP_COL]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        serving_caps_raw = sorted(serving_caps_raw)
        serving_capacity_option = st.sidebar.selectbox(
            "Serving capacity",
            options=["All"] + serving_caps_raw,
            index=0
        )
    else:
        serving_capacity_option = "All"
else:
    search_query = ""
    serving_capacity_option = "All"

# ==========================
# MAIN AREA
# ==========================
if show_advanced:
    # ---- ADVANCED MODE ----
    st.header("Advanced search results")

    # Apply filters
    results_df = df.copy()

    # Global search
    if search_query:
        string_cols = results_df.select_dtypes(include=["object", "string"]).columns
        if len(string_cols) > 0:
            mask = pd.Series(False, index=results_df.index)
            for col in string_cols:
                mask |= results_df[col].astype(str).str.contains(
                    search_query,
                    case=False,
                    na=False,
                )
            results_df = results_df[mask]

    # Serving capacity filter
    if serving_capacity_option != "All" and SERVING_CAP_COL in results_df.columns:
        results_df = results_df[
            results_df[SERVING_CAP_COL].astype(str) == serving_capacity_option
        ]

    st.write(f"Showing **{len(results_df)}** vendor(s) matching the filters.")

    if results_df.empty:
        st.info("No vendors match the current search and serving capacity filter.")
    else:
        # Loop over matching vendors and show each in an expander
        for _, row in results_df.iterrows():
            info = extract_vendor_info(row)
            header_text = (
                f"{info['vendor_code']} · {info['vendor_name']}"
                if info["vendor_code"] not in ["", "-"]
                else info["vendor_name"]
            )

            with st.expander(header_text, expanded=False):
                # Small header line
                st.write(f"**Location:** {info['location']}")
                st.write("---")
                render_owner_and_vendor_boxes(info)

else:
    # ---- BASIC MODE ----
    st.header("Vendor overview")

    if selected_vendor == "All Vendors":
        st.write("Select a specific vendor from the sidebar to see details.")
    else:
        vendor_rows = df[df[VENDOR_NAME_COL] == selected_vendor]
        if vendor_rows.empty:
            st.warning("No data found for the selected vendor.")
        else:
            # Take the first row for that vendor
            row = vendor_rows.iloc[0]
            info = extract_vendor_info(row)

            # Top summary container
            with st.container(border=True):
                col_left, col_right = st.columns([2, 1])

                with col_left:
                    st.write("**Vendor**")
                    if info["vendor_code"] not in ["", "-"]:
                        st.write(f"{info['vendor_code']} · {info['vendor_name']}")
                    else:
                        st.write(info["vendor_name"])

                with col_right:
                    st.write("**Primary location**")
                    st.write(info["location"])

            # Owner + Vendor details
            render_owner_and_vendor_boxes(info)
