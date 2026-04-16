# import streamlit as st
# import pandas as pd
# import gspread
# from google.oauth2.service_account import Credentials

# # -------------------------------
# # CONFIG
# # -------------------------------
# SHEET_ID = "13W7_scwOIY_H0z1a2JPzKC5IWQWsaFiSeqIE9UURgPQ"
# WORKSHEET_NAME = "ST JC FMS"

# # -------------------------------
# # CONNECT GOOGLE SHEETS
# # -------------------------------
# def connect_gsheet():
#     creds = Credentials.from_service_account_info(
#         st.secrets["gcp_service_account"],
#         scopes=["https://www.googleapis.com/auth/spreadsheets"]
#     )
#     client = gspread.authorize(creds)
#     return client.open_by_key(SHEET_ID)

# # -------------------------------
# # LOAD DATA
# # -------------------------------
# @st.cache_data(ttl=60)
# def load_data():
#     sh = connect_gsheet()
#     ws = sh.worksheet(WORKSHEET_NAME)

#     data = ws.get_all_values()

#     # Header row (Row 6)
#     header = data[5]
#     rows = data[6:]

#     df = pd.DataFrame(rows, columns=header)

#     return df

# df = load_data()

# # -------------------------------
# # CLEAN COLUMN NAMES
# # -------------------------------
# df.columns = df.columns.str.strip()

# # Remove duplicate columns
# df = df.loc[:, ~df.columns.duplicated()]

# # -------------------------------
# # SAFE DATE PARSING (FIXED)
# # -------------------------------

# # TIMESTAMP (Column B → dd/mm/yyyy hh:mm:ss)
# if "TIMESTAMP" in df.columns:
#     df["TIMESTAMP"] = pd.to_datetime(
#         df["TIMESTAMP"],
#         format="%d/%m/%Y %H:%M:%S",
#         errors="coerce"
#     )

# # PLANNED (Column N → dd-mm-yyyy hh:mm)
# if "PLANNED" in df.columns:
#     df["PLANNED"] = pd.to_datetime(
#         df["PLANNED"],
#         format="%d-%m-%Y %H:%M",
#         errors="coerce"
#     )

# # ACTUAL (Column O → dd-mm-yyyy hh:mm)
# if "ACTUAL" in df.columns:
#     df["ACTUAL"] = pd.to_datetime(
#         df["ACTUAL"],
#         format="%d-%m-%Y %H:%M",
#         errors="coerce"
#     )

# # -------------------------------
# # UI CONFIG
# # -------------------------------
# st.set_page_config(page_title="ST JC FMS", layout="wide")

# st.title("📊 ST JC FMS Dashboard")

# # -------------------------------
# # FILTER: DOER
# # -------------------------------
# if "DOER" in df.columns:
#     doer_list = ["ALL"] + sorted(df["DOER"].dropna().unique())
#     selected_doer = st.selectbox("Filter by DOER", doer_list)

#     if selected_doer != "ALL":
#         df = df[df["DOER"] == selected_doer]

# # -------------------------------
# # DISPLAY TABLE
# # -------------------------------
# st.markdown(f"### Total Records: {len(df)}")

# st.dataframe(
#     df,
#     use_container_width=True,
#     height=600
# )


# ---------------------------//---------------------------------

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

    header = data[5]
    rows = data[6:]

    df = pd.DataFrame(rows, columns=header)

    return df

df = load_data()

# -------------------------------
# CLEAN COLUMNS
# -------------------------------
df.columns = df.columns.str.strip()
df = df.loc[:, ~df.columns.duplicated()]

# -------------------------------
# COLUMN GROUPS (YOUR LOGIC)
# -------------------------------
groups = [
    ("M", "N", "O"),
    ("U", "V", "W"),
    ("AC", "AD", "AE"),
    ("AK", "AL", "AM"),
    ("AS", "AT", "AU"),
    ("BA", "BB", "BC"),
    ("BI", "BJ", "BK"),
    ("BQ", "BR", "BS"),
    ("BY", "BZ", "CA"),
    ("CG", "CH", "CI"),
    ("CO", "CP", "CQ"),
    ("CW", "CX", "CY"),
    ("DE", "DF", "DG"),
    ("DM", "DN", "DO"),
    ("DU", "DV", "DW"),
    ("EC", "ED", "EE"),
    ("EK", "EL", "EM"),
    ("ES", "ET", "EU"),
    ("FA", "FB", "FC"),
    ("FI", "FJ", "FK"),
    ("FQ", "FR", "FS"),
    ("FY", "FZ", "GA"),
    ("GG", "GH", "GI"),
    ("GO", "GP", "GQ"),
    ("GW", "GX", "GY")
]

# -------------------------------
# BASE COLUMNS (A–G)
# -------------------------------
base_cols = df.columns[:7]  # A to G

# -------------------------------
# ROW BIND LOGIC
# -------------------------------
final_rows = []

for _, row in df.iterrows():
    base_data = row[base_cols].to_dict()

    for g in groups:
        col1, col2, col3 = g

        if col1 in df.columns and col2 in df.columns and col3 in df.columns:
            doer = row[col1]
            planned = row[col2]
            actual = row[col3]

            # Skip empty groups
            if doer == "" and planned == "" and actual == "":
                continue

            new_row = base_data.copy()
            new_row["DOER"] = doer
            new_row["PLANNED"] = planned
            new_row["ACTUAL"] = actual

            final_rows.append(new_row)

# Create final dataframe
final_df = pd.DataFrame(final_rows)

# -------------------------------
# DATE PARSING
# -------------------------------
if "PLANNED" in final_df.columns:
    final_df["PLANNED"] = pd.to_datetime(
        final_df["PLANNED"],
        format="%d-%m-%Y %H:%M",
        errors="coerce"
    )

if "ACTUAL" in final_df.columns:
    final_df["ACTUAL"] = pd.to_datetime(
        final_df["ACTUAL"],
        format="%d-%m-%Y %H:%M",
        errors="coerce"
    )

if "TIMESTAMP" in final_df.columns:
    final_df["TIMESTAMP"] = pd.to_datetime(
        final_df["TIMESTAMP"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"
    )

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="Row Bind View", layout="wide")

st.title("📊 ST JC FMS - Row Bind View")

# -------------------------------
# FILTER
# -------------------------------
if "DOER" in final_df.columns:
    doer_list = ["ALL"] + sorted(final_df["DOER"].dropna().unique())
    selected_doer = st.selectbox("Filter by DOER", doer_list)

    if selected_doer != "ALL":
        final_df = final_df[final_df["DOER"] == selected_doer]

# -------------------------------
# DISPLAY
# -------------------------------
st.markdown(f"### Total Records: {len(final_df)}")

st.dataframe(final_df, use_container_width=True, height=600)
