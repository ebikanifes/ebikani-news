# ebikani-news
エビカニフェス（@ebikani_fes）Instagram 自動ニュース投稿用。
- images/ : 投稿画像（BASEが自動生成）
- tools/make_card.py : 画像生成スクリプト（python3 -I tools/make_card.py spec.json out.jpg）
- posted.json : 投稿済みニュースの記録（重複投稿防止）
- spec.json の "theme" で背景色を指定（"blue"＝紺・既定 / "red"＝赤）。投稿ごとに交互に使う
