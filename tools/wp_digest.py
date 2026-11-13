"""公式サイト用に選んだその日の話題（site_posts.json）を1本のまとめ記事にして、公式サイト（WordPress）の「最新情報」に投稿する。
（Instagram の投稿記録 posted.json とは別。サイト独自の話題だけを使う）

usage:
  python3 -I tools/wp_digest.py [--date YYYY-MM-DD] [--dry-run] [--status publish|draft]

環境変数（GitHub Actions の Secrets から渡す）:
  WP_USER          投稿専用ユーザーのユーザー名
  WP_APP_PASSWORD  そのユーザーのアプリケーションパスワード
  WP_API           省略時 https://ebikani.jp/wp-json/wp/v2
標準ライブラリのみ使用。
"""
import argparse, base64, datetime, html, json, os, sys, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.environ.get("WP_API", "https://ebikani.jp/wp-json/wp/v2").rstrip("/")
JST = datetime.timezone(datetime.timedelta(hours=9))
WEEK = "月火水木金土日"
TYPE_LABEL = {"news": "ニュース", "furusato": "ふるさと納税", "tabehoudai": "食べ放題", "gourmet": "グルメ情報"}
NOTE = {
    "furusato": "※内容・寄附額は変更になる場合があります。最新情報は各ページでご確認ください。",
    "tabehoudai": "※料金・内容は変わる場合があります。最新情報は公式サイトでご確認ください。",
    "gourmet": "※料金・内容は変わる場合があります。最新情報は公式サイトでご確認ください。",
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
    try:
        with urllib.request.urlopen(r, timeout=60) as res:
            return json.load(res)
    except urllib.error.HTTPError as err:
        print(f"{method} {path} -> HTTP {err.code}: {err.read()[:500].decode('utf-8','replace')}", file=sys.stderr)
        raise


def title_for(d):
    return f"エビカニニュース｜{d.month}月{d.day}日（{WEEK[d.weekday()]}）のまとめ"


def build_content(entries, media_urls, first=False):
    e = html.escape
    ig = f'<a href="{IG_URL}">@ebikani_fes</a>'
    if first:
        parts = [
            "<p>エビカニフェス公式サイトでは、本日から「エビカニニュース」をお届けします。</p>",
            "<p>全国の旬のエビ・カニのニュースをはじめ、エビ・カニが返礼品にあるふるさと納税の自治体、"
            "エビ・カニの食べ放題が楽しめるお店、エビ・カニ料理のグルメ情報などを、"
            "毎日1本のまとめ記事にしてこちらに掲載していきます。フェスは終わっても、エビ・カニの楽しみはまだまだ続きます！</p>",
            f"<p>記念すべき第1回は、{len(entries)}本の話題をお届けします。</p>",
        ]
    else:
        parts = [
            "<p>エビカニニュースでは、エビ・カニのニュースやふるさと納税、食べ放題、グルメ情報を毎日まとめてお届けしています。"
            f"今日の話題は{len(entries)}本です。</p>"
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


def find_digests(title):
    """同じタイトルの記事のID（なければNone）と、ほかに公開済みのエビカニニュースがあるかを返す。"""
    q = urllib.parse.urlencode({"search": "エビカニニュース", "status": "publish,draft,pending,future",
                                "context": "edit", "per_page": 50, "_fields": "id,title,status"})
    same, others = None, False
    for p in req("GET", "/news?" + q):
        t = p["title"].get("raw", "")
        if t == title:
            same = p["id"]
        elif t.startswith("エビカニニュース") and p.get("status") == "publish":
            others = True
    return same, others


def find_media(name):
    stem = os.path.splitext(name)[0]
    q = urllib.parse.urlencode({"search": stem, "per_page": 20, "_fields": "id,source_url"})
    for m in req("GET", "/media?" + q):
        if os.path.basename(m["source_url"]).startswith(stem):
            return m["id"], m["source_url"]
    return None


def upload(path, alt):
    name = os.path.basename(path)
    found = find_media(name)
    if found:
        return found
    with open(path, "rb") as f:
        m = req("POST", "/media", raw=f.read(), headers={
            "Content-Type": "image/jpeg",
            "Content-Disposition": f'attachment; filename="{name}"'})
    try:
        req("POST", f"/media/{m['id']}", data={"alt_text": alt})
    except Exception:
        pass
    return m["id"], m["source_url"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--first", action="store_true", help="dry-run で初回の書き出しを確認する")
    ap.add_argument("--status", default="publish", choices=["publish", "draft"])
    a = ap.parse_args()
    d = datetime.date.fromisoformat(a.date) if a.date else datetime.datetime.now(JST).date()
    path = os.path.join(ROOT, "site_posts.json")
    posted = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    order = {"news": 0, "furusato": 1, "tabehoudai": 2, "gourmet": 3}
    entries = sorted((x for x in posted if x.get("date") == d.isoformat()),
                     key=lambda x: order.get(x.get("type", "news"), 9))
    if not entries:
        print(f"{d}: site_posts.json にこの日の話題がありません。まとめ記事は作りません。")
        return
    title = title_for(d)
    if a.dry_run:
        urls = ["https://raw.githubusercontent.com/ebikanifes/ebikani-news/main/" + x["image"] if x.get("image") else None for x in entries]
        print(title)
        print(build_content(entries, urls, first=a.first))
        return
    same, others = find_digests(title)
    first = not others
    ids, urls = [], []
    for x in entries:
        p = os.path.join(ROOT, x.get("image", ""))
        if x.get("image") and os.path.exists(p):
            mid, url = upload(p, x["title"])
            ids.append(mid); urls.append(url)
        else:
            ids.append(None); urls.append(None)
    post = {"title": title, "content": build_content(entries, urls, first=first), "status": a.status}
    fm = next((i for i in ids if i), None)
    if fm:
        post["featured_media"] = fm
    if same:
        # 同じ日の記事がすでにあれば、その日の最新の内容で上書きする（夜の実行で昼以降の投稿も反映）
        r = req("POST", f"/news/{same}", data=post)
        print(f"更新しました：{title} {r.get('link')}")
    else:
        r = req("POST", "/news", data=post)
        print(f"投稿しました：{title} {r.get('link')}")


if __name__ == "__main__":
    main()
