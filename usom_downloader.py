import requests
import time
import csv
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_usom():
    data_list = []
    headers = {'accept': 'application/json'}
    current_page = 0
    total_pages = 1
    url = "https://siberguvenlik.gov.tr/api/address/index?type=ip"
    
    try:
        while current_page < total_pages:
            paginated_url = f"{url}&page={current_page}"
            response = requests.get(paginated_url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if current_page == 0:
                total_pages = data.get("pageCount", 1)
                
            for item in data.get("models", []):
                ip_addr = item.get("url")
                date_str = item.get("date")
                
                try:
                    clean_date_str = date_str.split('.')[0]
                    date_obj = datetime.strptime(clean_date_str, "%Y-%m-%d %H:%M:%S")
                    formatted_date = date_obj.strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    formatted_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                entry_dict = {
                    "name": f"USOM_{ip_addr}",
                    "lowIp": ip_addr,
                    "highIp": ip_addr,
                    "description": f"USOM | Type: {item.get('connectiontype', 'N/A')} | Source: {item.get('source', 'N/A')}",
                    "severity": str(item.get("criticality_level", 5)),
                    "country": "TR",
                    "dateFound": formatted_date
                }
                data_list.append(entry_dict)
                
            current_page += 1
            time.sleep(0.2)
            
        if len(data_list) > 0:
            unique_ips = set()
            clean_data_list = []
            for entry in data_list:
                if entry["lowIp"] not in unique_ips:
                    unique_ips.add(entry["lowIp"])
                    clean_data_list.append(entry)
                    
            # Sabit CSV dosyasına yaz
            csv_path = "/opt/phoenix/cache/MalwareIP/usom_temiz.csv"
            keys = ['name', 'lowIp', 'highIp', 'description', 'severity', 'country', 'dateFound']
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(clean_data_list)
                
    except Exception as e:
        pass

if __name__ == '__main__':
    download_usom()
