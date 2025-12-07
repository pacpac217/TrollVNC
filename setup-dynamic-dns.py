#!/usr/bin/env python3
"""
Dynamic DNS Updater cho serverapi.xyz
Tự động cập nhật IP khi IP server thay đổi
"""

import requests
import time
import os
from datetime import datetime

# ==============================================================================
# CẤU HÌNH
# ==============================================================================

# Cloudflare API (nếu dùng Cloudflare DNS)
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", "")
DOMAIN = "serverapi.xyz"
RECORD_NAME = "@"  # hoặc "serverapi" nếu dùng subdomain

# Hoặc dùng DDNS service khác (No-IP, DuckDNS, etc.)
DDNS_SERVICE = "cloudflare"  # "cloudflare", "noip", "duckdns"

# File lưu IP cũ
IP_FILE = "last_ip.txt"

# ==============================================================================
# HÀM LẤY IP PUBLIC
# ==============================================================================

def get_public_ip():
    """Lấy IP public hiện tại của server"""
    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
        "https://api.ip.sb/ip"
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                # Validate IP
                parts = ip.split(".")
                if len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts):
                    return ip
        except:
            continue
    
    return None

# ==============================================================================
# CLOUDFLARE DNS UPDATE
# ==============================================================================

def get_cloudflare_record_id(zone_id, record_name, api_token):
    """Lấy Record ID từ Cloudflare"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    params = {"name": record_name, "type": "A"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("result") and len(data["result"]) > 0:
                return data["result"][0]["id"]
    except Exception as e:
        print(f"Error getting record ID: {e}")
    
    return None

def update_cloudflare_dns(zone_id, record_id, record_name, new_ip, api_token):
    """Cập nhật DNS record trên Cloudflare"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": record_name,
        "content": new_ip,
        "ttl": 300  # 5 minutes
    }
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return True, "DNS updated successfully"
            else:
                return False, result.get("errors", [{}])[0].get("message", "Unknown error")
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# NO-IP DDNS UPDATE
# ==============================================================================

def update_noip_dns(username, password, hostname, new_ip):
    """Cập nhật DNS qua No-IP DDNS service"""
    url = f"https://dynupdate.no-ip.com/nic/update"
    params = {
        "hostname": hostname,
        "myip": new_ip
    }
    auth = (username, password)
    
    try:
        response = requests.get(url, params=params, auth=auth, timeout=10)
        if response.status_code == 200:
            if "good" in response.text or "nochg" in response.text:
                return True, "DNS updated successfully"
            else:
                return False, response.text
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# DUCKDNS UPDATE
# ==============================================================================

def update_duckdns_dns(token, domain, new_ip):
    """Cập nhật DNS qua DuckDNS"""
    url = f"https://www.duckdns.org/update"
    params = {
        "domains": domain,
        "token": token,
        "ip": new_ip
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            if "OK" in response.text:
                return True, "DNS updated successfully"
            else:
                return False, response.text
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

def get_last_ip():
    """Lấy IP đã lưu"""
    if os.path.exists(IP_FILE):
        try:
            with open(IP_FILE, "r") as f:
                return f.read().strip()
        except:
            return None
    return None

def save_ip(ip):
    """Lưu IP hiện tại"""
    try:
        with open(IP_FILE, "w") as f:
            f.write(ip)
    except:
        pass

def main():
    print(f"[{datetime.now()}] Checking IP...")
    
    # Lấy IP hiện tại
    current_ip = get_public_ip()
    if not current_ip:
        print("❌ Cannot get public IP")
        return
    
    print(f"Current IP: {current_ip}")
    
    # Kiểm tra IP có thay đổi không
    last_ip = get_last_ip()
    if last_ip == current_ip:
        print("✅ IP unchanged, no update needed")
        return
    
    print(f"IP changed: {last_ip} → {current_ip}")
    
    # Cập nhật DNS
    success = False
    message = ""
    
    if DDNS_SERVICE == "cloudflare":
        if not CLOUDFLARE_API_TOKEN or not CLOUDFLARE_ZONE_ID:
            print("❌ Cloudflare API token or Zone ID not configured")
            return
        
        record_id = get_cloudflare_record_id(CLOUDFLARE_ZONE_ID, DOMAIN, CLOUDFLARE_API_TOKEN)
        if not record_id:
            print("❌ Cannot find DNS record")
            return
        
        success, message = update_cloudflare_dns(
            CLOUDFLARE_ZONE_ID, record_id, RECORD_NAME, current_ip, CLOUDFLARE_API_TOKEN
        )
    
    elif DDNS_SERVICE == "noip":
        username = os.getenv("NOIP_USERNAME", "")
        password = os.getenv("NOIP_PASSWORD", "")
        if not username or not password:
            print("❌ No-IP credentials not configured")
            return
        
        success, message = update_noip_dns(username, password, DOMAIN, current_ip)
    
    elif DDNS_SERVICE == "duckdns":
        token = os.getenv("DUCKDNS_TOKEN", "")
        if not token:
            print("❌ DuckDNS token not configured")
            return
        
        success, message = update_duckdns_dns(token, DOMAIN, current_ip)
    
    if success:
        print(f"✅ {message}")
        save_ip(current_ip)
    else:
        print(f"❌ Update failed: {message}")

if __name__ == "__main__":
    main()

