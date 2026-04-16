# -------------------------------//-----------------------------------------
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="ST JC FMS", layout="wide")

# ---------------------------
# CUSTOM CSS
# ---------------------------
st.markdown("""
<style>
.header-row {
    position: sticky;
    top: 0;
    background-color: #0E1117;
    z-index: 999;
    padding: 10px 0;
    border-bottom: 2px solid #444;
}

div.stButton > button {
    white-space: nowrap;
    width: 100%;
    height: 40px;
    font-weight: bold;
}

.done-btn button {
    background-color: #28a745 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# GOOGLE SHEETS CONNECTION
# ---------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# ---------------------------
# SHEETS
# ---------------------------
SHEET_ID = "13W7_scwOIY_H0z1a2JPzKC5IWQWsaFiSeqIE9UURgPQ"
MAIN_SHEET = client.open_by_key(SHEET_ID).worksheet("ST JC FMS")
STORE_SHEET = client.open_by_key(SHEET_ID).worksheet("TASK UPDATE")

# ---------------------------
# STEP DESCRIPTION MAP
# ---------------------------
STEP_DESC = {
    "STEP-1": "CAD MAKING",
    "STEP-2": "MINI PRINT CHECKING & SIGN BY YADAV",
    "STEP-3": "AFTER CHECKING MINI PRINT - CUTTER",
    "STEP-4": "CAD MAN PRINT OUT",
    "STEP-5": "FABRIC ISSUE IN CUTTING",
    "STEP-6": "CUTTING PROCESS",
    "STEP-7": "CUTTING ACCOUNT",
    "STEP-8": "STITCHING JOB CARD",
    "STEP-9": "CUTTING ISSUE TO STITCHING"
}

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data(ttl=60)
def load_data():
    data = MAIN_SHEET.get("A6:HD")
    df = pd.DataFrame(data)
    df.columns = range(len(df.columns))
    df = df[1:].reset_index(drop=True)
    return df

df = load_data()

# ---------------------------
# PROCESS FUNCTION
# ---------------------------
def process_block(df, doer_i, planned_i, actual_i, step_name):
    temp = df[[0,2,3,4,5,6,doer_i,planned_i,actual_i]].copy()

    temp.columns = [
        "JOB SERIES","JC CARD NO","BUYER","ITEM CODE",
        "CUT QTY","CUTTER","DOER","PLANNED","ACTUAL"
    ]

    temp["PLANNED"] = temp["PLANNED"].astype(str).str.strip()
    temp["ACTUAL"] = temp["ACTUAL"].astype(str).str.strip()

    temp = temp[(temp["PLANNED"] != "") & (temp["ACTUAL"] == "")]

    temp["STEP NO"] = step_name
    temp["STEP DESCRIPTION"] = STEP_DESC.get(step_name, "")

    return temp

# ---------------------------
# BLOCKS
# ---------------------------
blocks = [
    (12,13,14,"STEP-1"),
    (20,21,22,"STEP-2"),
    (28,29,30,"STEP-3"),
    (36,37,38,"STEP-4"),
    (44,45,46,"STEP-5"),
    (52,53,54,"STEP-6"),
    (60,61,62,"STEP-7"),
    (68,69,70,"STEP-8"),
    (76,77,78,"STEP-9"),
]

final_df = pd.concat([process_block(df,*b) for b in blocks], ignore_index=True)

# ---------------------------
# SESSION STATE
# ---------------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = set()

# ---------------------------
# UI
# ---------------------------
st.title("📊 ST JC FMS - Pending Work")

if final_df.empty:
    st.warning("No pending data")
    st.stop()

st.success(f"Total Pending Rows: {len(final_df)}")

# ---------------------------
# FILTERS
# ---------------------------
c1, c2 = st.columns(2)

doer = c1.selectbox("Filter by DOER", ["All"] + sorted(final_df["DOER"].unique()))
step = c2.selectbox("Filter by STEP", ["All"] + sorted(final_df["STEP NO"].unique()))

df_f = final_df.copy()

if doer != "All":
    df_f = df_f[df_f["DOER"] == doer]

if step != "All":
    df_f = df_f[df_f["STEP NO"] == step]

# ---------------------------
# HEADER
# ---------------------------
header = st.columns([2,2,2,2,2,2,2,2,2,3,1])

for col, name in zip(header, [
    "JOB SERIES","JC CARD NO","BUYER","ITEM CODE",
    "CUT QTY","CUTTER","DOER","PLANNED",
    "STEP NO","STEP DESCRIPTION","ACTION"
]):
    col.markdown(f"<div class='header-row'><b>{name}</b></div>", unsafe_allow_html=True)

# ---------------------------
# ROWS
# ---------------------------
for i, row in df_f.iterrows():
    cols = st.columns([2,2,2,2,2,2,2,2,2,3,1])

    cols[0].write(row["JOB SERIES"])
    cols[1].write(row["JC CARD NO"])
    cols[2].write(row["BUYER"])
    cols[3].write(row["ITEM CODE"])
    cols[4].write(row["CUT QTY"])
    cols[5].write(row["CUTTER"])
    cols[6].write(row["DOER"])
    cols[7].write(row["PLANNED"])
    cols[8].write(row["STEP NO"])
    cols[9].write(row["STEP DESCRIPTION"])

    key = f"{row['JOB SERIES']}_{row['STEP NO']}"

    if key in st.session_state.submitted:
        cols[10].markdown("<div class='done-btn'>", unsafe_allow_html=True)
        cols[10].button("DONE", key=f"d{i}", disabled=True)
        cols[10].markdown("</div>", unsafe_allow_html=True)
    else:
        if cols[10].button("SUBMIT", key=f"s{i}"):

            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

            col_a = STORE_SHEET.col_values(1)
            next_row = len(col_a) + 1

            data = [[
                current_time,
                row["JOB SERIES"],
                row["STEP NO"],
                "YES"
            ]]

            STORE_SHEET.update(
                f"A{next_row}:D{next_row}",
                data,
                value_input_option="USER_ENTERED"
            )

            st.session_state.submitted.add(key)

            st.success(f"Submitted {row['JOB SERIES']} - {row['STEP NO']}")

            st.cache_data.clear()
            st.rerun()



