# FortiSIEM - USOM Threat Intelligence Integration (Decoupled Architecture)

An optimized, two-tier (decoupled) Python integration designed to securely and efficiently ingest large-scale Threat Intelligence feeds (like USOM Malicious IPs) into FortiSIEM environments.

## 📌 Overview: What is this?
Ingesting external Threat Intelligence feeds containing tens of thousands of Indicators of Compromise (IOCs) often involves heavily paginated APIs. In enterprise SIEM environments, long-running HTTP pull requests can lead to resource contention and disrupt real-time data ingestion pipelines.

This project introduces a **Decoupled Architecture** to FortiSIEM's ThreatFeed mechanism. By separating the *Data Extraction* phase from the *Data Ingestion* phase, this solution guarantees 100% data ingestion reliability, eliminates system timeout risks, and ensures database integrity.

## 🏗️ Architecture: Why Decoupled?
To achieve optimal performance and stability, the monolithic plugin approach was divided into two specialized, lightweight components:

1. **The Extractor (`usom_downloader.py`):** 
   * **Role:** Runs natively on the Linux OS level (via Cronjob). 
   * **Function:** Asynchronously navigates API pagination, handles external rate limits smoothly, and performs in-memory data sanitization and deduplication (preventing Unique Constraint Violations in the SIEM database). It outputs a clean, ready-to-ingest `.csv` file.
   
2. **The Ingestor (`usom_threatfeed.py`):** 
   * **Role:** Acts as the native FortiSIEM Python Plugin.
   * **Function:** Instead of holding an active HTTP connection to the internet, it instantly reads the sanitized `.csv` file from the local disk and pushes it to the FortiSIEM AppServer. This reduces the application-level execution time from minutes to milliseconds.

## ⚙️ Deployment & Configuration

### Step 1: Setup the Extractor (Background Worker)
Place the downloader script in the threatfeed integrations directory and grant execution permissions so the Linux OS can trigger it:

```bash
cp usom_downloader.py /opt/phoenix/data-definition/threatfeedIntegrations/
chmod 755 /opt/phoenix/data-definition/threatfeedIntegrations/usom_downloader.py
```

Schedule the data extraction to run daily (e.g., at 03:00 AM) by adding it to your crontab:

```bash
crontab -e
# Add the following line:
0 3 * * * /usr/bin/python3.9 /opt/phoenix/data-definition/threatfeedIntegrations/usom_downloader.py
```

### Step 2: Setup the Ingestor (FortiSIEM Plugin)
Place the feeder script in the same directory and grant execution permissions so the FortiSIEM `phoenix` daemon can execute it:

```bash
cp usom_threatfeed.py /opt/phoenix/data-definition/threatfeedIntegrations/
chmod 755 /opt/phoenix/data-definition/threatfeedIntegrations/usom_threatfeed.py
```

### Step 3: FortiSIEM GUI Configuration
Map the new ingestor script to the FortiSIEM interface:

1. Navigate to **RESOURCES > Malware IPs**.
2. Create or Edit the USOM Threatfeed group.
3. Configure with the following parameters:
   * **Update via API:** `Checked`
   * **Plugin Type:** `Python`
   * **Script Name:** `usom_threatfeed.py`
   * **Update Type:** `Full Update`
   * **URL:** 'https://siberguvenlik.gov.tr/api/address/index?type=ip' *(Note: Since the decoupled ingestor reads locally, a dummy URL is sufficient to pass GUI validation).*
4. Click **Save**, right-click the group, and select **Update > Once**. The dashboard will populate instantly.

## 🛡️ Prerequisites
* FortiSIEM (Tested on v7.x)
* Python 3.9+
* Network access to the target API for the FortiSIEM Supervisor/Worker node.
