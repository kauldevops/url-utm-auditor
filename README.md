# 🔗 Paid Media URL & UTM Parameter Auditor

An automated diagnostic web app designed to protect paid media attribution. It bulk-audits landing page URLs to verify that critical marketing parameters (such as `utm`, `gclid`, `gbraid`, and `gad` identifiers) successfully persist when users encounter server-side redirects.

## ⚠️ The Problem It Solves
When active paid media URLs point to deprecated routes, vanity URLs, or mapped facets, web servers trigger a redirect (HTTP 301/302). If the server is not configured correctly, it will drop incoming query parameters during this hop. When tracking parameters are dropped, platforms like GA4, Segment, and Google Ads lose the attribution link, causing expensive paid traffic to be misclassified as "Direct" or "Unassigned."

## ⚙️ Features
* **Browser Simulation:** Mimics a real Google Chrome browser TLS fingerprint to bypass CDN/WAF bot protection (like Akamai or Cloudflare).
* **Smart Parameter Filtering:** Includes a customizable "Ignore List" to automatically ignore harmless internal backend variables (e.g., `idSector`, `isFuzzySearch`) so dropping them does not trigger a false alarm.
* **Accurate Trace Routing:** Follows the full HTTP redirect chain and captures the *exact* status code that caused the redirect (301/302), rather than just the final page load status (200).
* **CSV Export:** Instantly generates a downloadable report of failing URLs and exactly which parameters were stripped.

## 🚀 How to Run This App Locally

### Prerequisites
You must have Python installed on your computer.

### Step 1: Clone the Repository
Download the code to your local machine:
```bash
git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
cd YOUR-REPO-NAME
