import re
import urllib.request

html = urllib.request.urlopen("http://127.0.0.1:5000/register/seeker").read().decode("utf-8", "replace")
css = urllib.request.urlopen("http://127.0.0.1:5000/static/css/main.css").read()

print("HTML size:", len(html))
print("CSS size:", len(css), "nulls:", css.count(b"\x00"))
print("form-step in html:", html.count("form-step"))
print("active steps:", len(re.findall(r'class="form-step step-content active"', html)))
print("css in head:", ".form-step" in html[:html.find("</head>")])
print("showStep:", "function showStep" in html)

for m in re.finditer(r'<div class="([^"]*)" id="(step-\d)"([^>]*)>', html):
    print(m.group(2), m.group(1)[:60], m.group(3)[:40])
