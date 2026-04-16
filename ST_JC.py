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
# CLEAN
# -------------------------------
df.columns = df.columns.str.strip()
df = df.loc[:, ~df.columns.duplicated()]

# -------------------------------
# COLUMN INDEX GROUPS (IMPORTANT FIX)
# -------------------------------
groups = [
    (12,13,14),   # M,N,O
    (20,21,22),   # U,V,W
    (28,29,30),   # AC,AD,AE
    (36,37,38),   # AK,AL,AM
    (44,45,46),   # AS,AT,AU
    (52,53,54),   # BA,BB,BC
    (60,61,62),   # BI,BJ,BK
    (68,69,70),   # BQ,BR,BS
    (76,77,78),   # BY,BZ,CA
    (84,85,86),   # CG,CH,CI
    (92,93,94),   # CO,CP,CQ
    (100,101,102),# CW,CX,CY
    (108,109,110),
    (116,117,118),
    (124,125,126),
    (132,133,134),
    (140,141,142),
    (148,149,150),
    (156,157,158),
    (164,165,166),
    (172,173,174),
    (180,181,182),
    (188,189,190),
    (196,197,198),
    (204,205,206)
]

# -------------------------------
# BASE COLUMNS (A–G)
# -------------------------------
base_cols = df.columns[:7]

# -------------------------------
# ROW BIND
# -------------------------------
final_rows = []

for _, row in df.iterrows():
    base_data = row[base_cols].to_dict()

    for g in groups:
        try:
            doer = row.iloc[g[0]]
            planned = row.iloc[g[1]]
            actual = row.iloc[g[2]]

            if str(doer).strip() == "" and str(planned).strip() == "" and str(actual).strip() == "":
                continue

            new_row = base_data.copy()
            new_row["DOER"] = doer
            new_row["PLANNED"] = planned
            new_row["ACTUAL"] = actual

            final_rows.append(new_row)

        except:
            continue

final_df = pd.DataFrame(final_rows)

# -------------------------------
# DATE PARSE
# -------------------------------
if "PLANNED" in final_df.columns:
    final_df["PLANNED"] = pd.to_datetime(final_df["PLANNED"], format="%d-%m-%Y %H:%M", errors="coerce")

if "ACTUAL" in final_df.columns:
    final_df["ACTUAL"] = pd.to_datetime(final_df["ACTUAL"], format="%d-%m-%Y %H:%M", errors="coerce")

# -------------------------------
# UI
# -------------------------------
st.set_page_config(layout="wide")
st.title("📊 ST JC FMS - Row Bind View")

# DEBUG (REMOVE LATER)
# st.write(df.shape)
# st.write(df.columns)

# FILTER
if "DOER" in final_df.columns:
    doer_list = ["ALL"] + sorted(final_df["DOER"].dropna().unique())
    selected_doer = st.selectbox("Filter by DOER", doer_list)

    if selected_doer != "ALL":
        final_df = final_df[final_df["DOER"] == selected_doer]

# DISPLAY
st.markdown(f"### Total Records: {len(final_df)}")
st.dataframe(final_df, use_container_width=True, height=600)
