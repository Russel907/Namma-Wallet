
import os
import logging
import requests
from urllib.parse import urlencode
from decouple import config

logger = logging.getLogger(__name__)

MESSAGECENTRAL_BASE = config("MESSAGECENTRAL_BASE", default="https://cpaas.messagecentral.com")
MESSAGECENTRAL_CUSTOMER_ID = config("MESSAGECENTRAL_CUSTOMER_ID", default=None)
MESSAGECENTRAL_BASE64_KEY = config("MESSAGECENTRAL_BASE64_KEY", default=None)
MESSAGECENTRAL_DEFAULT_COUNTRY = config("MESSAGECENTRAL_COUNTRY_CODE", default="91")

def _get_auth_token(country=MESSAGECENTRAL_DEFAULT_COUNTRY, scope="NEW", email=None, timeout=10):
    if not MESSAGECENTRAL_CUSTOMER_ID or not MESSAGECENTRAL_BASE64_KEY:
        return False, {"error": "missing_credentials"}
    path = "/auth/v1/authentication/token"
    params = {
        "customerId": MESSAGECENTRAL_CUSTOMER_ID,
        "key": MESSAGECENTRAL_BASE64_KEY,
        "scope": scope,
        "country": country,
    }
    if email:
        params["email"] = email
    url = f"{MESSAGECENTRAL_BASE}{path}?{urlencode(params)}"
    resp = requests.get(url, headers={"accept": "*/*"}, timeout=timeout)
    if resp.status_code != 200:
        return False, {"status": resp.status_code, "body": resp.text}
    token = resp.json().get("token")
    if not token:
        return False, {"error": "no_token"}
    return True, token

def send_otp_via_messagecentral(mobile_number, country_code=MESSAGECENTRAL_DEFAULT_COUNTRY, timeout=10):
    ok, token_or_err = _get_auth_token(country=country_code)
    if not ok:
        return False, token_or_err
    auth_token = token_or_err
    path = "/verification/v3/send"
    params = {
        "countryCode": country_code,
        "flowType": "SMS",
        "mobileNumber": mobile_number,
    }
    url = f"{MESSAGECENTRAL_BASE}{path}?{urlencode(params)}"
    headers = {
        "authToken": auth_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    resp = requests.post(url, headers=headers, timeout=timeout)
    if resp.status_code == 200:
        return True, resp.json()
    return False, {"status": resp.status_code, "body": resp.text}

def verify_otp_via_messagecentral(mobile_number, otp_code, verification_id, country_code=MESSAGECENTRAL_DEFAULT_COUNTRY, timeout=10):
    ok, token_or_err = _get_auth_token(country=country_code)
    if not ok:
        return False, token_or_err

    auth_token = token_or_err
    params = {
        "countryCode": country_code,
        "mobileNumber": mobile_number,
        "verificationId": verification_id,
        "customerId": MESSAGECENTRAL_CUSTOMER_ID,
        "code": otp_code
    }

    url = f"{MESSAGECENTRAL_BASE}/verification/v3/validateOtp?{urlencode(params)}"
    headers = {
        "authToken": auth_token,
        "Accept": "application/json"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
    except Exception as e:
        return False, {"error": str(e)}

    try:
        j = resp.json()
    except ValueError:
        j = {}

    if resp.status_code == 200 and j.get("message") == "SUCCESS":
        return True, j

    return False, j