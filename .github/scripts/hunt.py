#!/usr/bin/env python3
import json, os, urllib.request

try:
    with open('.github/lead-tracker.json') as f:
        tracker = json.load(f)
except:
    tracker = {'processed': []}
processed = set(tracker.get('processed', []))

req = urllib.request.Request(
    'https://api.github.com/repos/NanmiCoder/MediaCrawler/issues?state=open&per_page=30&sort=created&direction=desc',
    headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(req, timeout=30) as resp:
    issues = json.loads(resp.read())

keywords = ['需要','定制','外包','求助','哪里','谁能','收费','付费','求','想要','开发','爬取','可以实现','帮我','请问能']
new_leads = []

for i in issues:
    issue_id = str(i['id'])
    if issue_id in processed:
        continue
    title = i.get('title', '')
    body = (i.get('body') or '')[:300]
    user = i.get('user', {}).get('login', '')
    url = i.get('html_url', '')
    created = i.get('created_at', '')[:10]
    full_text = (title + body).lower()
    matched = [k for k in keywords if k in full_text]
    if matched:
        new_leads.append({'id': issue_id, 'user': user, 'title': title, 'url': url, 'created': created, 'matched': matched})
        processed.add(issue_id)

print("发现 " + str(len(new_leads)) + " 条新需求")

if new_leads:
    lines = ["全自动猎客报告", "="*50, "发现 " + str(len(new_leads)) + " 条新需求", ""]
    for idx, lead in enumerate(new_leads, 1):
        lines.extend([str(idx) + ". @" + lead['user'] + " | " + lead['created'], "   " + lead['title'], "   " + lead['url'], "   匹配: " + ", ".join(lead['matched']), ""])

    lines.extend(["="*50, "回复模板:", "你好，看到你的问题。我提供付费技术定制开发服务，", "50元起，当天交付。承接各类数据采集、爬虫定制、报错修复。", "GitHub: https://github.com/liuyuzhe530", "系统: GitHub Actions 全自动猎客"])

    payload = {
        "sender": {"name": os.environ['BREVO_SENDER_NAME'], "email": os.environ['BREVO_SENDER_EMAIL']},
        "to": [{"email": os.environ['NOTIFY_EMAIL']}],
        "subject": "【需求线索】发现 " + str(len(new_leads)) + " 条新需求",
        "textContent": "\n".join(lines)
    }

    req = urllib.request.Request(
        'https://api.brevo.com/v3/smtp/email',
        data=json.dumps(payload).encode(),
        headers={'api-key': os.environ['BREVO_API_KEY'], 'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        if result.get('messageId'):
            print("邮件发送成功: " + result['messageId'])
            tracker['processed'] = list(processed)[-200:]
            with open('.github/lead-tracker.json', 'w') as f:
                json.dump(tracker, f, ensure_ascii=False, indent=2)
            print("tracker已更新")
        else:
            print("发送失败: " + str(result))
else:
    print("无新需求")
