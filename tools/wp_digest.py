"""その日にInstagramへ投稿した内容を1本のまとめ記事にして、公式サイト（WordPress）の「最新情報」に投稿する。

usage:
  python3 -I tools/wp_digest.py [--date YYYY-MM-DD] [--dry-run] [--status publish|draft]

環境変数（GitHub Actions の Secrets から渡す）:
  WP_USER          投稿専用ユーザーのユーザー名
  WP_APP_PASSWORD  そのユーザーのアプリケーションパスワード
  WP_API           省略時 https://ebikani.jp/wp-json/wp/v2
標準ライブラリのみ使用。
"""
import argparse, base64, datetime, html, json, os, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.environ.get("WP_API", "https://ebikani.jp/wp-json/wp/v2").rstrip("/")
JST = datetime.timezone(datetime.timedelta(hours=9))
WEEK = "月火水木金土日"
TYPE_LABEL = {"news": "ニュース", "furusato": "ふるさと納税", "tabehoudai": "食べ放題"}
NOTE = {
    "furusato": "※内容・寄附額は変更になる場合があります。最新情報は各ページでご確認ください。",
    "tabehoudai": "※料金・内容は変わる場合があります。最新情報は公式サイトでご確認ください。",
}
IG_URL = "https://www.instagram.com/ebikani_fes/"


def auth_header():
    u, p = os.environ.get("WP_USER"), os.environ.get("WP_APP_PASSWORD")
    if not u or not p:
        sys.exit("WP_USER / WP_APP_PASSWORD が設定されていません")
    return "Basic " + base64.b64encode(f"{u}:{p}".encode()).decode()


def req(method, path, data=None, headers=None, raw=None):
    h = {"Authorization": auth_header(), "User-Agent": "ebikani-digest/1.0"}
    h.update(headers or {})
    body = raw
    if data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(API + path, data=body, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=60) as res:
        return json.load(res)


def title_for(d):
    return f"エビカニニュース｜{d.month}月{d.day}日（{WEEK[d.weekday()]}）のまとめ"


def build_content(entries, media_urls):
    e = html.escape
    parts = [
        f'<p>今日、エビカニフェス公式Instagram（<a href="{IG_URL}">@ebikani_fes</a>）で紹介した'
        f"エビ・カニの話題を{len(entries)}本まとめてお届けします。</p>"
    ]
    notes = []
    for i, x in enumerate(entries):
        label = TYPE_LABEL.get(x.get("type", "news"), "ニュース")
        parts.append(f"<h3>【{label}】{e(x['title'])}</h3>")
        if media_urls[i]:
            parts.append(f'<figure><img src="{e(media_urls[i])}" alt="{e(x["title"])}" /></figure>')
        if x.get("summary"):
            parts.append(f"<p>{e(x['summary'])}</p>")
        src = x.get("source_url", "")
        name = x.get("source_name") or urllib.parse.urlparse(src).netloc
        if src:
            parts.append(f'<p>出典：<a href="{e(src)}" target="_blank" rel="noopener">{e(name)}</a></p>')
        n = NOTE.get(x.get("type"))
        if n and n not in notes:
            notes.append(n)
    for n in notes:
        parts.append(f"<p><small>{e(n)}</small></p>")
    parts.append(f'<p>毎日のエビ・カニ情報はInstagram <a href="{IG_URL}">@ebikani_fes</a> でも発信中です。</p>')
    return "\n".join(parts)


def already_posted(title):
    q = urllib.parse.urlencode({"search": "エビカニニュース", "status": "publish,draft,pending,future",
                                "context": "edit", "per_page": 20, "_fields": "id,title"})
    for p in req("GET", "/news?" + q):
        if p["title"].get("raw") == title:
            return p["id"]
    return None


def upload(path, alt):
    name = os.path.basename(path)
    with open(path, "rb") as f:
        m = req("POST", "/media", raw=f.read(), headers={
            "Content-Type": "image/jpeg",
            "Content-Disposition": f"attachment; filename*=UTF-8''{urllib.parse.quote(name)}"})
    try:
        req("POST", f"/media/{m['id']}", data={"alt_text": alt})
    except Exception:
        pass
    return m["id"], m["source_url"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--status", default="publish", choices=["publish", "draft"])
    a = ap.parse_args()
    d = datetime.date.fromisoformat(a.date) if a.date else datetime.datetime.now(JST).date()
    posted = json.load(open(os.path.join(ROOT, "posted.json"), encoding="utf-8"))
    entries = [x for x in posted if x.get("date") == d.isoformat()]
    if not entries:
        print(f"{d}: Instagram投稿なし。まとめ記事は作りません。")
        return
    title = title_for(d)
    if a.dry_run:
        urls = ["https://raw.githubusercontent.com/ebikanifes/ebikani-news/main/" + x["image"] if x.get("image") else None for x in entries]
        print(title)
        print(build_content(entries, urls))
        return
    if already_posted(title):
        print(f"すでに投稿済み：{title}")
        return
    ids, urls = [], []
    for x in entries:
        p = os.path.join(ROOT, x.get("image", ""))
        if x.get("image") and os.path.exists(p):
            mid, url = upload(p, x["title"])
            ids.append(mid); urls.append(url)
        else:
            ids.append(None); urls.append(None)
    post = {"title": title, "content": build_content(entries, urls), "status": a.status}
    first = next((i for i in ids if i), None)
    if first:
        post["featured_media"] = first
    r = req("POST", "/news", data=post)
    print(f"投稿しました：{title} {r.get('link')}")


if __name__ == "__main__":
    main()
