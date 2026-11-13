# ebikani-news
エビカニフェス（@ebikani_fes）Instagram 自動ニュース投稿用。
- images/ : 投稿画像（BASEが自動生成）
- tools/make_card.py : 画像生成スクリプト（python3 -I tools/make_card.py spec.json out.jpg）
- posted.json : 投稿済みニュースの記録（重複投稿防止）
- spec.json の "theme" で背景色を指定（"blue"＝紺・既定 / "red"＝赤）。投稿ごとに交互に使う
- site_posts.json : 公式サイト（ebikani.jp）用の話題の記録。Instagramとは別に、毎日の定期実行で4〜5本（ニュース・ふるさと納税・食べ放題・グルメ情報）を選んで追記する
- tools/wp_digest.py : site_posts.json のその日の話題を1本のまとめ記事にして公式サイトに投稿（GitHub Actions。定期実行からの呼び出し＋毎日22:41の予備実行。同じ日の記事は上書き）
