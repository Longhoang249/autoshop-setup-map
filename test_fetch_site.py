import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://autoshop-setup-map.pages.dev"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'SiteCheck/1.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
        print("Status:", response.status)
        html = response.read().decode('utf-8')
        print("HTML length:", len(html))
        print("HTML snippet:")
        print(html[:600])
except Exception as e:
    print("Error fetching site:", e)
