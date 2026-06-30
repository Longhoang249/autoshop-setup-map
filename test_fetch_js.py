import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://autoshop-setup-map.pages.dev"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'SiteCheck/1.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
        html = response.read().decode('utf-8')
        # Find script tag src
        match = re.search(r'src="(/assets/index-[^"]+\.js)"', html)
        if match:
            js_path = match.group(1)
            js_url = url + js_path
            print("Found JS Path:", js_path)
            # Fetch JS
            req_js = urllib.request.Request(js_url, headers={'User-Agent': 'SiteCheck/1.0'})
            with urllib.request.urlopen(req_js, context=ctx, timeout=8) as response_js:
                print("JS Status:", response_js.status)
                print("JS length:", len(response_js.read()))
        else:
            print("No JS src found in HTML!")
except Exception as e:
    print("Error:", e)
