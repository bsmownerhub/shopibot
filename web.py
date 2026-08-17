import os, time, random, string, sys, io
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
init()
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BANNER = r"""
██╗    ██╗███████╗██████╗ ███████╗██╗  ██╗ █████╗ ██████╗ ███████╗
██║    ██║██╔════╝██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██╔════╝
██║ █╗ ██║█████╗  ██████╔╝███████╗███████║███████║██████╔╝█████╗
██║███╗██║██╔══╝  ██╔══██╗╚════██║██╔══██║██╔══██║██╔══██╗██╔══╝
╚███╔███╔╝███████╗██████╔╝███████║██║  ██║██║  ██║██║  ██║███████╗
 ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

                               Created by @Xoarch
"""

def rand_str(k=8):
    return ''.join(random.choices(string.ascii_lowercase, k=k))

def unique_email():
    existing = set()
    try:
        with open("accounts.txt") as f:
            for l in f:
                if ':' in l:
                    existing.add(l.split(':')[0].strip())
    except: pass
    while True:
        e = f"{rand_str(6)}{random.randint(100,9999)}@outlook.com"
        if e not in existing:
            return e

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def grad(text, g_start=120, g_end=255):
    lines = text.split('\n')
    n = len(lines)
    out = []
    for i, line in enumerate(lines):
        ratio = i / max(n - 1, 1)
        g = int(g_start + (g_end - g_start) * ratio)
        out.append(f"\033[38;2;0;{g};0m{line}\033[0m")
    return '\n'.join(out)

G = lambda t: f"\033[38;2;0;220;0m{t}\033[0m"
Y = lambda t: Fore.YELLOW + t + Style.RESET_ALL
R = lambda t: Fore.RED + t + Style.RESET_ALL

def gy(t, g=200):
    return f"\033[38;2;{g};{g};0m{t}\033[0m"

def gradient_banner(text):
    lines = text.strip('\n').split('\n')
    n = len(lines)
    for i, line in enumerate(lines):
        ratio = i / max(n - 1, 1)
        r, g, b = 0, int(120 + 135 * ratio), 0
        if r > 255: r = 255
        if g > 255: g = 255
        print(f"\033[38;2;{r};{g};{b}m{line}\033[0m")

def show_banner():
    clr()
    gradient_banner(BANNER)

def make_proxy_ext(ip, port, scheme):
    d = os.path.join(os.environ.get("TEMP", "/tmp"), f"ext_{rand_str()}")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "manifest.json"), "w") as f:
        f.write('{"version":"1.0","manifest_version":2,"name":"P","permissions":["proxy","webRequest","webRequestBlocking","<all_urls>"],"background":{"scripts":["b.js"]}}')
    js = 'chrome.proxy.settings.set({value:{mode:"fixed_servers",rules:{singleProxy:{scheme:"%s",host:"%s",port:%s}}}},scope:"regular"});'
    with open(os.path.join(d, "b.js"), "w") as f:
        f.write(js % (scheme, ip, port))
    return d

def make_auth_ext(ip, port, user, pwd, scheme):
    d = os.path.join(os.environ.get("TEMP", "/tmp"), f"ext_{rand_str()}")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "manifest.json"), "w") as f:
        f.write('{"version":"1.0","manifest_version":2,"name":"P","permissions":["proxy","webRequest","webRequestBlocking","<all_urls>"],"background":{"scripts":["b.js"]}}')
    js = '''var c={"mode":"fixed_servers","rules":{"singleProxy":{"scheme":"%s","host":"%s","port":%s}}};
chrome.proxy.settings.set({value:c,scope:"regular"});
chrome.webRequest.onAuthRequired.addListener(function(d){return {authCredentials:{username:"%s",password:"%s"}}},{urls:["<all_urls>"]},["blocking"]);'''
    with open(os.path.join(d, "b.js"), "w") as f:
        f.write(js % (scheme, ip, port, user, pwd))
    return d

def load_proxies_from_file(path):
    r = []
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l:
                x = l.split(":")
                if len(x) >= 2:
                    r.append(l)
    return r

def create_account(proxy_str, scheme, email=None, password=None):
    if email is None:
        email = unique_email()
    if password is None:
        password = rand_str(8) + random.choice(string.digits) + random.choice(string.ascii_uppercase) + "x"

    print()
    if proxy_str:
        print(f"{G(f'  Proxy:    {proxy_str}')}")

    sess = requests.Session()
    if proxy_str and scheme != "none":
        x = proxy_str.split(":")
        if len(x) == 4:
            sess.proxies = {"http": f"{scheme}://{x[2]}:{x[3]}@{x[0]}:{x[1]}", "https": f"{scheme}://{x[2]}:{x[3]}@{x[0]}:{x[1]}"}
        elif len(x) == 2:
            sess.proxies = {"http": f"{scheme}://{x[0]}:{x[1]}", "https": f"{scheme}://{x[0]}:{x[1]}"}

    from webdriver_manager.chrome import ChromeDriverManager
    cd_path = ChromeDriverManager().install()
    opts = uc.ChromeOptions()
    opts.add_argument("--window-size=1280,720")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--incognito")

    ext = None
    if proxy_str and scheme != "none":
        x = proxy_str.split(":")
        if len(x) == 4:
            ext = make_auth_ext(x[0], x[1], x[2], x[3], scheme)
        elif len(x) == 2:
            ext = make_proxy_ext(x[0], x[1], scheme)
        opts.add_argument(f"--load-extension={ext}")

    driver = uc.Chrome(options=opts, driver_executable_path=cd_path)
    w = WebDriverWait(driver, 20)

    try:
        driver.get("https://dashboard.webshare.io/register?source=login_signup_link")
        time.sleep(1)

        em = w.until(EC.element_to_be_clickable((By.ID, "email-input")))
        em.click()
        em.clear()
        em.send_keys(email)
        v = driver.execute_script("return arguments[0].value;", em)
        if not v:
            driver.execute_script("arguments[0].value = arguments[1];", em, email)
        time.sleep(0.3)

        pw = w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
        pw.click()
        pw.clear()
        pw.send_keys(password)
        v = driver.execute_script("return arguments[0].value;", pw)
        if not v:
            driver.execute_script("arguments[0].value = arguments[1];", pw, password)
        time.sleep(0.3)

        try:
            cb = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            if not cb.is_selected(): cb.click()
        except: pass

        time.sleep(0.3)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print(f"  {G('[*] Sign Up clicked')}")
        print(f"  {gy('[!] Solve captcha manually...', 200)}")

        token = None
        for _ in range(120):
            time.sleep(1)
            try:
                t = driver.execute_script("return grecaptcha.getResponse();")
                if t: token = t; break
            except: pass

        if not token:
            print(f"  {R('[-] Captcha not solved')}")
            return False

        print(f"  {G('[+] Solved')}")

        time.sleep(2)
        current = driver.current_url
        if "register" not in current and "login" not in current:
            print(f"  {G('[*] Form submitted, fetching proxies...')}")
            at = driver.execute_script("return localStorage.getItem('token') || '';")
            if not at:
                at = driver.execute_script("return (document.cookie.match(/token=([^;]+)/)||[])[1] || '';")
            if at:
                print(f"  {G('[*] Token obtained from browser')}")
                h2 = {"Authorization": f"Token {at}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
                r2 = sess.get("https://proxy.webshare.io/api/v2/proxy/list/", headers=h2, params={"mode":"direct","page":"1","page_size":"100"}, timeout=15)
                if r2.status_code == 200:
                    results = r2.json().get("results", [])
                    if results:
                        with open("proxy.txt", "a") as f:
                            for p in results:
                                auth = f"{p['username']}:{p['password']}"
                                line = f"{p['proxy_address']}:{p['port']}:{auth}"
                                f.write(line + "\n")
                        print(f"  {G(f'[+] {len(results)} proxies saved')}")
                    else:
                        print(f"  {Y('[-] No proxies')}")
                elif r2.status_code == 403:
                    print(f"  {Y('[-] No proxy plan (403)')}")
                else:
                    print(f"  {R(f'[-] Proxy fetch: {r2.status_code}')}")
                with open("accounts.txt", "a") as f:
                    f.write(f"{email}:{password}\n")
                print(f"  {G('[+] Account saved')}")
                return True

        for _ in range(10):
            time.sleep(1)
            u = driver.current_url
            if "register" not in u and "login" not in u:
                break

        current = driver.current_url
        if "register" not in current and "login" not in current:
            print(f"  {G('[*] Form submitted, fetching proxies...')}")
            at = driver.execute_script("return localStorage.getItem('token') || '';")
            if not at:
                at = driver.execute_script("return (document.cookie.match(/token=([^;]+)/)||[])[1] || '';")
            if at:
                print(f"  {G('[*] Token from browser')}")
                h2 = {"Authorization": f"Token {at}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
                r2 = sess.get("https://proxy.webshare.io/api/v2/proxy/list/", headers=h2, params={"mode":"direct","page":"1","page_size":"100"}, timeout=15)
                if r2.status_code == 200:
                    results = r2.json().get("results", [])
                    if results:
                        with open("proxy.txt", "a") as f:
                            for p in results:
                                auth = f"{p['username']}:{p['password']}"
                                line = f"{p['proxy_address']}:{p['port']}:{auth}"
                                f.write(line + "\n")
                        print(f"  {G(f'[+] {len(results)} proxies saved')}")
                    else:
                        print(f"  {Y('[-] No proxies')}")
                elif r2.status_code == 403:
                    print(f"  {Y('[-] No proxy plan (403)')}")
                else:
                    print(f"  {R(f'[-] Proxy fetch: {r2.status_code}')}")
                with open("accounts.txt", "a") as f:
                    f.write(f"{email}:{password}\n")
                print(f"  {G('[+] Account saved')}")
                return True

        print(f"  {gy('[*] Trying API...', 180)}")
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        cs = "; ".join(f"{k}={v}" for k, v in cookies.items())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) Gecko/20100101 Firefox/153.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://dashboard.webshare.io",
            "Referer": "https://dashboard.webshare.io/",
            "Cookie": cs,
        }

        data = {"email": email, "password": password, "tos_accepted": True, "recaptcha": token}
        try:
            resp = sess.post("https://proxy.webshare.io/api/v2/register/", headers=headers, json=data, timeout=30)
            print(f"  {G(f'[*] API: {resp.status_code}')}")
        except Exception as e:
            print(f"  {R(f'[-] API: {e}')}")
            return False

        if resp.status_code in (200, 201):
            rj = resp.json()
            at = rj.get("token", "")
            with open("accounts.txt", "a") as f:
                f.write(f"{email}:{password}\n")
            print(f"  {G('[+] Account saved')}")
            if at:
                time.sleep(1)
                h2 = {"Authorization": f"Token {at}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
                r2 = sess.get("https://proxy.webshare.io/api/v2/proxy/list/", headers=h2, params={"mode":"direct","page":"1","page_size":"100"}, timeout=15)
                if r2.status_code == 200:
                    results = r2.json().get("results", [])
                    if results:
                        with open("proxy.txt", "a") as f:
                            for p in results:
                                auth = f"{p['username']}:{p['password']}"
                                line = f"{p['proxy_address']}:{p['port']}:{auth}"
                                f.write(line + "\n")
                        print(f"  {G(f'[+] {len(results)} proxies saved')}")
                    else:
                        print(f"  {Y('[-] No proxies')}")
                elif r2.status_code == 403:
                    print(f"  {Y('[-] No proxy plan (403)')}")
                else:
                    print(f"  {R(f'[-] Proxy fetch: {r2.status_code}')}")
            return True

        if 'already exists' in resp.text.lower():
            print(f"  {Y('[-] Email exists, logging in...')}")
            ld = {"email": email, "password": password}
            try:
                lr = sess.post("https://proxy.webshare.io/api/v2/auth/login/", headers=headers, json=ld, timeout=30)
                print(f"  {G(f'[*] Login: {lr.status_code}')}")
                if lr.status_code == 200:
                    at = lr.json().get("token", "")
                    if at:
                        with open("accounts.txt", "a") as f:
                            f.write(f"{email}:{password}\n")
                        print(f"  {G('[+] Account saved')}")
                        time.sleep(1)
                        h2 = {"Authorization": f"Token {at}", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
                        r2 = sess.get("https://proxy.webshare.io/api/v2/proxy/list/", headers=h2, params={"mode":"direct","page":"1","page_size":"100"}, timeout=15)
                        if r2.status_code == 200:
                            results = r2.json().get("results", [])
                            if results:
                                with open("proxy.txt", "a") as f:
                                    for p in results:
                                        auth = f"{p['username']}:{p['password']}"
                                        line = f"{p['proxy_address']}:{p['port']}:{auth}"
                                        f.write(line + "\n")
                                print(f"  {G(f'[+] {len(results)} proxies saved')}")
                            else:
                                print(f"  {Y('[-] No proxies')}")
                        elif r2.status_code == 403:
                            print(f"  {Y('[-] No proxy plan (403)')}")
                        else:
                            print(f"  {R(f'[-] Proxy fetch: {r2.status_code}')}")
                        return True
            except Exception as e:
                print(f"  {R(f'[-] Login: {e}')}")
            return False

        try:
            j = resp.json()
            if 'throttled' in j.get('detail', '').lower():
                import re
                m = re.search(r'(\d+)', j.get('detail', ''))
                if m:
                    s = int(m.group(1))
                    print(f"  {Y(f'[-] Rate limited, waiting {s}s...')}")
                    for r in range(s, 0, -1):
                        print(f"  {Y(f'{r}s...')}  ", end='\r')
                        time.sleep(1)
                    print("         ", end='\r')
                    return False
        except: pass

        print(f"  {R(f'[-] {resp.text[:200]}')}")
        return False

    finally:
        try:
            import gc
            driver.close()
            gc.collect()
        except: pass
        if ext and os.path.exists(ext):
            try:
                import shutil
                shutil.rmtree(ext, ignore_errors=True)
            except: pass


if __name__ == "__main__":
    show_banner()
    print()

    while True:
        r = input(grad('  Accounts to generate (1-10): ', 180, 180)).strip()
        try:
            cnt = int(r)
            if cnt < 1:
                print(f"  {R('[-] Minimum is 1')}")
                continue
            if cnt > 10:
                print(f"  {R('[-] Maximum is 10')}")
                continue
            break
        except:
            print(f"  {R('[-] Enter a valid number')}")

    print()
    print(f"  {grad('[1] HTTP', 120, 255)}")
    print(f"  {grad('[2] SOCKS4', 130, 255)}")
    print(f"  {grad('[3] SOCKS5', 140, 255)}")
    print(f"  {grad('[4] PROXYLESS', 150, 255)}")
    print()
    while True:
        pt = input(grad('  Choose (1-4): ', 200, 200)).strip()
        if pt in ("1","2","3","4"): break
        print(f"  {R('[-] Choose 1-4')}")

    scheme_map = {"1":"http","2":"socks4","3":"socks5","4":"none"}
    scheme = scheme_map[pt]

    proxies = []
    if scheme != "none":
        print()
        while True:
            fp = input(grad('  Enter proxy file path: ', 180, 180)).strip()
            if os.path.exists(fp):
                proxies = load_proxies_from_file(fp)
                if not proxies:
                    print(f"  {R('[-] No valid proxies found')}")
                else:
                    break
            else:
                print(f"  {R('[-] File not found')}")

    clr()
    gradient_banner(BANNER)
    print()

    accounts = []
    for i in range(cnt):
        e = unique_email()
        p = rand_str(8) + random.choice(string.digits) + random.choice(string.ascii_uppercase) + "x"
        accounts.append((e, p))
        print(f"  {G(f'[{i+1}]')}")
        print(f"  {G(f'Email: {e}')}")
        print(f"  {G(f'Pass:  {p}')}")

    ok = 0
    for i, (email, password) in enumerate(accounts):
        if cnt > 1:
            print()
            print(f"  {G('='*40)}")
            print(f"  {G(f'  Account {i+1}/{cnt}')}")
            print(f"  {G('='*40)}")
        proxy = proxies[i % len(proxies)] if proxies else None
        if create_account(proxy, scheme, email, password):
            ok += 1
        if i + 1 < cnt:
            print(f"\n  {gy('Waiting 5s...', 180)}")
            time.sleep(5)

    time.sleep(1)
