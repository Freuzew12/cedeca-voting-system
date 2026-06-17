import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- FILE CONFIGURATION ---
EXCEL_FILE = "TODECA_TRI_USA_DOUALA_YAOUNDE.xlsx"
VOTE_LOG_FILE = "vote_log.csv"

# --- LOAD DATA ---
@st.cache_data
def load_member_list():
    df = pd.read_excel(EXCEL_FILE, sheet_name='TODECA', skiprows=2)
    df = df.iloc[:, :3] # Keep SN, NAMES, RESIDENCE
    df.columns = ['SN', 'NAMES', 'RESIDENCE']
    df = df[df['SN'].apply(lambda x: str(x).strip().isdigit() if pd.notnull(x) else False)]
    df['SN'] = df['SN'].astype(str).str.strip()
    return df

try:
    members_df = load_member_list()
except Exception:
    df = pd.read_excel(EXCEL_FILE, sheet_name='TODECA')
    df.columns = [f"Col_{i}" for i in range(len(df.columns))]
    members_df = df

# Initialize vote log
if os.path.exists(VOTE_LOG_FILE):
    vote_log = pd.read_csv(VOTE_LOG_FILE, dtype={'Voter_SN': str})
else:
    vote_log = pd.DataFrame(columns=['Voter_SN', 'Candidate', 'Timestamp'])

# --- APP NAVIGATION ---
st.sidebar.title("CEDECA Elections 🗳️")
page = st.sidebar.radio("Go to", ["Voter Booth", "Admin Dashboard"])

# ==================== PAGE 1: VOTER BOOTH ====================
if page == "Voter Booth":
    st.title("🗳️ CEDECA Presidential Election")
    st.write("Please verify your identity using your Serial Number (SN) from the official list to cast your vote.")
    
    voter_sn = st.text_input("Enter your Serial Number (SN):", placeholder="e.g., 1").strip()
    
    if voter_sn:
        voter_row = members_df[members_df['SN'] == voter_sn]
        
        if voter_row.empty:
            st.error("❌ Serial Number not found. Please verify with the village meeting secretary.")
        else:
            voter_name = voter_row.iloc[0]['NAMES']
            st.success(f"Hello, **{voter_name}**!")
            
            has_voted = voter_sn in vote_log['Voter_SN'].values
            
            if has_voted:
                st.warning("⚠️ You have already cast your vote! You cannot vote a second time.")
            else:
                st.write("### Choose your candidate for the Post of President of CEDECA:")
                choice = st.radio("Candidates:", ["John", "Marry", "Paul"], index=None, placeholder="Select a candidate...")
                
                if st.button("Submit Vote", type="primary"):
                    if choice is None:
                        st.error("Please select a candidate before submitting.")
                    else:
                        new_vote = pd.DataFrame([{
                            'Voter_SN': voter_sn,
                            'Candidate': choice,
                            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }])
                        vote_log = pd.concat([vote_log, new_vote], ignore_index=True)
                        vote_log.to_csv(VOTE_LOG_FILE, index=False)
                        
                        st.balloons()
                        st.success(f"🎉 Success! Your vote for **{choice}** has been securely recorded.")
                        st.rerun()

# ==================== PAGE 2: ADMIN DASHBOARD ====================
elif page == "Admin Dashboard":
    st.title("📊 Live Election Results (PC Dashboard)")
    
    password = st.text_input("Enter Admin Password to view results:", type="password")
    
    if password == "cedeca2026":
        st.success("Access Granted.")
        
        total_voters = len(members_df)
        votes_cast = len(vote_log)
        turnout = (votes_cast / total_voters) * 100 if total_voters > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Eligible Voters", total_voters)
        col2.metric("Total Votes Cast", votes_cast)
        col3.metric("Voter Turnout", f"{turnout:.1f}%")
        
        st.divider()
        
        if votes_cast > 0:
            st.subheader("Current Standings")
            counts = vote_log['Candidate'].value_counts().reindex(["John", "Marry", "Paul"], fill_value=0)
            st.bar_chart(counts)
            st.dataframe(counts.rename("Total Votes"), use_container_width=True)
            
            st.subheader("📜 Live Audit Log")
            st.dataframe(vote_log, use_container_width=True)
        else:
            st.info("No votes have been cast yet.")
    elif password != "":
        st.error("❌ Incorrect Password. Access Denied.")
