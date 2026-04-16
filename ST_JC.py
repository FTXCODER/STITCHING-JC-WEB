import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# -------------------------------
# CONFIG
# -------------------------------
SHEET_ID = "13W7_scwOIY_H0z1a2JPzKC5IWQWsaFiSeqIE9UURgPQ"
WORKSHEET_NAME = "ST JC FMS"

# -------------------------------
# CONNECT GOOGLE SHEETS
# -------------------------------
def connect_gsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data(ttl=60)
def load_data():
    sh = connect_gsheet()
    ws = sh.worksheet(WORKSHEET_NAME)

    data = ws.get_all_values()

    # Header row (Row 6)
    header = data[5]
    rows = data[6:]

    df = pd.DataFrame(rows, columns=header)

    return df

df = load_data()

# -------------------------------
# CLEAN COLUMN NAMES
# -------------------------------
df.columns = df.columns.str.strip()

# Remove duplicate columns (IMPORTANT FIX)
df = df.loc[:, ~df.columns.duplicated()]

# -------------------------------
# DEBUG (optional - remove later)
# -------------------------------
# st.write(df.columns.tolist())

# -------------------------------
# SAFE DATE CONVERSION
# -------------------------------
date_cols = ["TIMESTAMP", "PLANNED", "ACTUAL"]

for col in date_cols:
    if col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        except Exception:
            pass

# -------------------------------
# UI CONFIG
# -------------------------------
st.set_page_config(page_title="ST JC FMS", layout="wide")

st.title("📊 ST JC FMS Dashboard")

# -------------------------------
# FILTER: DOER (Column M)
# -------------------------------
if "DOER" in df.columns:
    doer_list = ["ALL"] + sorted(df["DOER"].dropna().unique())
    selected_doer = st.selectbox("Filter by DOER", doer_list)

    if selected_doer != "ALL":
        df = df[df["DOER"] == selected_doer]

# -------------------------------
# DISPLAY TABLE
# -------------------------------
st.markdown(f"### Total Records: {len(df)}")

st.dataframe(
    df,
    use_container_width=True,
    height=600
)
