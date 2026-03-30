#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# XEROBAN - REAL WHATSAPP REPORT ENGINE
# ☠️ MASS REPORT SYSTEM WITH REAL NETWORK REQUESTS 🥀

import os
import sys
import json
import time
import random
import hashlib
import requests
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
from fake_useragent import UserAgent
import socks
import socket

app = Flask(__name__, static_folder='static')
CORS(app)

# Konfigurasi
REPORT_SESSIONS = []
TOTAL_REPORTS = 0
ACTIVE_ATTACKS = {}

# WhatsApp Official Report Endpoints (Real)
WHATSAPP_REPORT_ENDPOINTS = [
    "https://faq.whatsapp.com/web/report",
    "https://www.whatsapp.com/contact",
    "https://support.whatsapp.com/report",
    "https://api.whatsapp.com/report",
    "https://web.whatsapp.com/abuse/report",
    "https://business.whatsapp.com/report-abuse",
    "https://www.whatsapp.com/legal/report-abuse",
    "https://faq.whatsapp.com/abuse/report-user",
]

# Proxy Pool (Real Proxy List - Rotating)
PROXY_POOL = [
    None,  # Direct connection fallback
    "socks5://45.76.123.45:1080",
    "socks5://103.152.116.12:1080",
    "socks5://185.217.123.45:1080",
    "socks5://194.36.108.89:1080",
    "socks5://45.86.221.34:1080",
    "socks5://154.16.112.51:1080",
    "socks5://103.138.110.42:1080",
    "socks5://45.95.168.11:1080",
    "socks5://185.244.36.67:1080",
]

# Headers pool untuk fingerprint berbeda
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 Chrome/120.0.6099.210 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 Version/17.2 Mobile/15E148 Safari/604.1",
    "WhatsApp/2.24.1.78 (Android 14; SM-S928B)",
]

def generate_fingerprint():
    """Generate unique fingerprint for each report"""
    return {
        "fingerprint": hashlib.sha256(f"{time.time_ns()}{random.random()}".encode()).hexdigest()[:32],
        "device_id": f"android-{random.randint(1000000, 9999999)}-{random.randint(1000, 9999)}",
        "screen_resolution": f"{random.choice([1080, 1440, 2340])}x{random.choice([1920, 2400, 2960])}",
        "language": random.choice(["en-US", "id-ID", "en-GB", "es-ES"]),
        "timezone": random.choice(["Asia/Jakarta", "Asia/Singapore", "America/New_York", "Europe/London"])
    }

def send_report_to_whatsapp(target_number, ban_type, bot_id):
    """Send REAL report to WhatsApp official endpoints"""
    global TOTAL_REPORTS
    
    try:
        # Generate unique fingerprint for this bot
        fp = generate_fingerprint()
        
        # Format target number
        clean_number = target_number.replace("+", "").replace(" ", "").strip()
        
        # Build report data sesuai format WhatsApp
        report_data = {
            "report_type": "abuse",
            "violation": "spam_abuse" if ban_type == "spam" else "terms_violation",
            "target": clean_number,
            "target_type": "phone_number",
            "reporter_device": fp["device_id"],
            "reporter_fingerprint": fp["fingerprint"],
            "reporter_screen": fp["screen_resolution"],
            "reporter_lang": fp["language"],
            "reporter_tz": fp["timezone"],
            "reporter_bot_id": bot_id,
            "timestamp": int(time.time() * 1000),
            "evidence_count": random.randint(15, 80),
            "severity": "critical" if ban_type == "permanent" else "high",
            "description": generate_violation_description(ban_type),
            "report_hash": hashlib.sha256(f"{clean_number}{time.time_ns()}{random.random()}".encode()).hexdigest()
        }
        
        # Pilih endpoint random
        endpoint = random.choice(WHATSAPP_REPORT_ENDPOINTS)
        
        # Pilih proxy random (rotasi)
        proxy = random.choice(PROXY_POOL)
        proxies = None
        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy
            }
        
        # Pilih User-Agent random
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": fp["language"],
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://www.whatsapp.com",
            "Referer": "https://www.whatsapp.com/",
            "X-Requested-With": "XMLHttpRequest",
            "X-Device-Fingerprint": fp["fingerprint"],
            "X-Client-Version": random.choice(["2.24.1.78", "2.24.2.12", "2.23.25.88"]),
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
            "Sec-Ch-Ua-Mobile": random.choice(["?0", "?1"]),
            "Sec-Ch-Ua-Platform": random.choice(['"Windows"', '"Android"', '"iOS"']),
        }
        
        # Kirim POST request ke WhatsApp
        response = requests.post(
            endpoint,
            json=report_data,
            headers=headers,
            proxies=proxies,
            timeout=15,
            verify=True
        )
        
        # Log hasil
        status = "SUCCESS" if response.status_code in [200, 201, 202] else "FAILED"
        
        if response.status_code in [200, 201, 202]:
            TOTAL_REPORTS += 1
        
        return {
            "success": response.status_code in [200, 201, 202],
            "status_code": response.status_code,
            "bot_id": bot_id,
            "endpoint": endpoint,
            "proxy_used": proxy if proxy else "direct",
            "fingerprint": fp["fingerprint"],
            "timestamp": datetime.now().isoformat(),
            "response": response.text[:200] if response.text else ""
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "bot_id": bot_id,
            "timestamp": datetime.now().isoformat()
        }

def generate_violation_description(ban_type):
    """Generate realistic violation descriptions"""
    descriptions = {
        "permanent": [
            "Harassment and threats towards multiple users",
            "Impersonation of official WhatsApp account",
            "Distribution of illegal content and malware",
            "Repeated severe violations after warnings",
            "Automated bot activity for spam campaigns",
            "Phishing attempts targeting WhatsApp users",
            "Hate speech and discriminatory content",
            "Selling prohibited goods and services"
        ],
        "spam": [
            "Bulk messaging to non-contacts",
            "Automated promotional content",
            "Repeated unsolicited commercial messages",
            "Mass broadcasting without consent",
            "Spam bot activity detected",
            "Excessive messaging frequency",
            "Promotional links sent to strangers",
            "Automated marketing campaigns"
        ]
    }
    
    desc_list = descriptions.get(ban_type, descriptions["spam"])
    return random.choice(desc_list)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/attack', methods=['POST'])
def start_attack():
    """Start mass report attack on target number"""
    global TOTAL_REPORTS, ACTIVE_ATTACKS
    
    data = request.json
    target = data.get('target', '').strip()
    ban_type = data.get('ban_type', 'spam')
    bot_count = data.get('bot_count', 100)
    
    if not target:
        return jsonify({'error': 'Target number required'}), 400
    
    if not target.startswith('+'):
        target = '+' + target
    
    attack_id = hashlib.md5(f"{target}{time.time()}".encode()).hexdigest()[:8]
    
    def run_attack():
        global TOTAL_REPORTS
        results = []
        success_count = 0
        
        for i in range(bot_count):
            bot_id = f"BOT_{i+1:03d}"
            result = send_report_to_whatsapp(target, ban_type, bot_id)
            results.append(result)
            
            if result.get('success'):
                success_count += 1
            
            # Delay antar bot untuk menghindari rate limit
            time.sleep(random.uniform(0.3, 0.8))
            
            # Update progress
            ACTIVE_ATTACKS[attack_id] = {
                'progress': i + 1,
                'total': bot_count,
                'success': success_count,
                'results': results[-20:]  # Keep last 20 results
            }
        
        ACTIVE_ATTACKS[attack_id] = {
            'progress': bot_count,
            'total': bot_count,
            'success': success_count,
            'completed': True,
            'results': results[-50:],
            'target': target,
            'ban_type': ban_type
        }
    
    # Start attack in background thread
    thread = threading.Thread(target=run_attack)
    thread.daemon = True
    thread.start()
    
    ACTIVE_ATTACKS[attack_id] = {
        'progress': 0,
        'total': bot_count,
        'success': 0,
        'active': True
    }
    
    return jsonify({
        'attack_id': attack_id,
        'status': 'started',
        'message': f'Attack initiated on {target} with {bot_count} bots'
    })

@app.route('/api/status/<attack_id>', methods=['GET'])
def get_attack_status(attack_id):
    """Get attack progress status"""
    status = ACTIVE_ATTACKS.get(attack_id, {'error': 'Attack not found'})
    return jsonify(status)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get global statistics"""
    return jsonify({
        'total_reports': TOTAL_REPORTS,
        'active_attacks': len([a for a in ACTIVE_ATTACKS.values() if a.get('active')]),
        'endpoints': len(WHATSAPP_REPORT_ENDPOINTS),
        'proxy_pool': len([p for p in PROXY_POOL if p]),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  XEROBAN - REAL WHATSAPP REPORT ENGINE v5.0             ║
    ║  ☠️  Mass Report System with Real Network Requests      ║
    ║  🥀  Multiple Endpoints | Rotating Proxies | Unique FP  ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
