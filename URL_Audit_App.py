import streamlit as st
import pandas as pd
from urllib.parse import parse_qs, urlparse
from curl_cffi import requests

# Configure Page Layout
st.set_page_config(page_title="Paid Media URL & UTM Auditor", page_icon="🔗", layout="wide")

st.title("🔗 Paid Media URL & UTM Parameter Auditor")
st.markdown("Audits paid media landing pages across **The Knot**, **WeddingWire**, and other marketplace domains to verify server-side redirects and ensure ad tracking parameters (`utm`, `gclid`, `gbraid`, `gad`, etc.) are preserved.")

# Internal backend parameters that can be safely ignored if dropped
DEFAULT_IGNORED_PARAMS = {
    "idSector", "isNavegacionUsuario", "isFuzzySearch", 
    "isSearch", "isHome", "pageSize", "strBusqueda"
}

def audit_url(url, ignored_params=DEFAULT_IGNORED_PARAMS):
    if pd.isna(url) or not str(url).strip():
        return "", "", "SKIP", "Empty Row"
        
    url_str = str(url).strip()
    if not url_str.startswith('http'):
        url_str = 'https://' + url_str
        
    try:
        # Impersonate Google Chrome TLS signature to bypass CDN/WAF bot blocks
        response = requests.get(url_str, impersonate="chrome", allow_redirects=True, timeout=15)
        final_url = response.url
        
        # Capture initial redirect status code (301/302) if history exists, otherwise final status code (200)
        initial_status = response.history[0].status_code if response.history else response.status_code
        final_status = response.status_code
        
        # Check for Bot Protection / Error pages
        if final_status in [403, 429, 503]:
            return final_url, final_status, f"BLOCKED ({final_status})", "WAF / Bot Protection Block"
        elif final_status >= 400:
            return final_url, final_status, f"ERROR ({final_status})", "HTTP Error Page"
        
        # Parse query parameters from original and final URLs
        orig_params = set(parse_qs(urlparse(url_str).query).keys())
        final_params = set(parse_qs(urlparse(final_url).query).keys())
        
        # Exclude harmless internal backend parameters from the audit check
        relevant_orig_params = orig_params - set(ignored_params)
        
        # Identify dropped marketing and ad parameters
        dropped = relevant_orig_params - final_params
        
        if dropped:
            return final_url, initial_status, "FAIL - Parameters Dropped", ", ".join(sorted(dropped))
        elif response.history:
            return final_url, initial_status, "PASS (Redirected)", "None"
        else:
            return final_url, initial_status, "PASS (Direct Target)", "None"
            
    except Exception as e:
        return "Error", "ERROR", "FAIL - Connection Error", str(e)

# Sidebar Options
st.sidebar.header("Audit Settings")
input_option = st.sidebar.radio("Choose URL Input Method:", ["Upload CSV File", "Paste URLs Text"])

st.sidebar.subheader("Ignore List Customization")
ignore_input = st.sidebar.text_area(
    "Internal parameters to ignore (comma-separated):", 
    value=", ".join(DEFAULT_IGNORED_PARAMS),
    height=100
)
custom_ignored = {p.strip() for p in ignore_input.split(",") if p.strip()}

urls_to_audit = []

if input_option == "Upload CSV File":
    uploaded_file = st.file_uploader("Upload a CSV file containing URLs", type=["csv"])
    if uploaded_file is not None:
        df_input = pd.read_csv(uploaded_file)
        st.write("Preview of Uploaded Data:", df_input.head(3))
        
        url_col = st.selectbox("Select the column containing URLs:", df_input.columns)
        urls_to_audit = df_input[url_col].dropna().tolist()

else:
    pasted_text = st.text_area("Paste URLs below (one per line):", height=200)
    if pasted_text:
        urls_to_audit = [line.strip() for line in pasted_text.split('\n') if line.strip()]

# Execute Audit
if urls_to_audit:
    if st.button("🚀 Run URL Audit", type="primary"):
        st.info(f"Auditing {len(urls_to_audit)} URLs. Please wait...")
        
        progress_bar = st.progress(0)
        results = []
        
        for idx, url in enumerate(urls_to_audit):
            res = audit_url(url, ignored_params=custom_ignored)
            results.append({
                "Original URL": url,
                "Final Landing URL": res[0],
                "Status Code": res[1],
                "Audit Status": res[2],
                "Dropped Parameters": res[3]
            })
            progress_bar.progress((idx + 1) / len(urls_to_audit))
            
        results_df = pd.DataFrame(results)
        
        # Summary Metrics
        st.subheader("📊 Audit Results Summary")
        col1, col2, col3 = st.columns(3)
        total_urls = len(results_df)
        passed_urls = len(results_df[results_df["Audit Status"].str.contains("PASS", na=False)])
        failed_urls = total_urls - passed_urls
        
        col1.metric("Total Audited", total_urls)
        col2.metric("Passed", passed_urls)
        col3.metric("Failed / Dropped", failed_urls, delta_color="inverse")
        
        # Results Table
        st.dataframe(results_df, use_container_width=True)
        
        # Download CSV
        csv_data = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Audit Results CSV",
            data=csv_data,
            file_name="marketplace_url_audit_results.csv",
            mime="text/csv"
        )