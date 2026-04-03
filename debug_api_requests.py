#!/usr/bin/env python3
"""
Debug script to test what data produces HIGH vs LOW risk
"""
import requests
import json

API_URL = "https://fraud-detection-api-production-2c2f.up.railway.app/api/v1/predict"
API_KEY = "TRIAL_Qaa0NiEHiqYOpCO3Py0oww"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Test data from CSV row 2 (should be LOW RISK - $50 gmail.com)
test_low_risk = {
    "merchant_id": "MERCH001",
    "amount": 50.0,
    "payment_method": "credit_card",
    "user_id_hash": "user456",
    "ip_hash": "192.168.1.2",
    "email_domain": "gmail.com",
    "is_new_user": False,  # CSV has "false"
    "device_type": "desktop",
    "billing_shipping_match": True,  # CSV has "true"
    "hour_of_day": 14,
    "day_of_week": 2,
    "items_count": 3
}

# Test data from CSV row 1 (should be HIGH RISK - $5000 tempmail.com)
test_high_risk = {
    "merchant_id": "MERCH001",
    "amount": 5000.0,
    "payment_method": "credit_card",
    "user_id_hash": "user123",
    "ip_hash": "192.168.1.1",
    "email_domain": "tempmail.com",
    "is_new_user": True,  # CSV has "true"
    "device_type": "mobile",
    "billing_shipping_match": False,  # CSV has "false"
    "hour_of_day": 3,
    "day_of_week": 1,
    "items_count": 1
}

print("="*60)
print("Testing CSV Row 2 - Should be LOW RISK")
print("="*60)
print("Request data:")
print(json.dumps(test_low_risk, indent=2))
print()

response = requests.post(API_URL, headers=headers, json=test_low_risk)
print("Response:")
result = response.json()
print(json.dumps(result, indent=2))
print(f"\nLabel: {result.get('label')}")
print(f"Confidence: {result.get('confidence')*100:.2f}%")
print()

print("="*60)
print("Testing CSV Row 1 - Should be HIGH RISK")
print("="*60)
print("Request data:")
print(json.dumps(test_high_risk, indent=2))
print()

response = requests.post(API_URL, headers=headers, json=test_high_risk)
print("Response:")
result = response.json()
print(json.dumps(result, indent=2))
print(f"\nLabel: {result.get('label')}")
print(f"Confidence: {result.get('confidence')*100:.2f}%")
