# EasyKakeibo

・テストユーザー情報

<家計簿id関係>

 id |               book_id                | book_name |     email      | permission
 
----+--------------------------------------+-----------+----------------+------------

  1 | 5916da9f-c03f-409d-852c-7954171e0b73 | newbook2  | test1@test.com |          1
  
  2 | 5916da9f-c03f-409d-852c-7954171e0b73 | newbook2  | test2@test.com |          2
  
  3 | 5916da9f-c03f-409d-852c-7954171e0b73 | newbook2  | test3@test.com |          3


・使用技術
flask(Webフレームワーク)
heroku(サーバー)
postgresql(データベース)
html
css
d3.js


仕様
- 買ったものと値段の閲覧・入力・更新・削除　permission<=2
- 設定機能（費目の追加・削除機能）permission<=2
- 家計簿の削除　permission=1
- 費目別集計 permission<=3
- 日次集計 permission<=3
- 期間集計 permission<=3
- 円グラフ、棒グラフ出力 permission<=3
- 複数人での共有機能（ログイン機能・グループ機能等々） permission=1は他者にpermissionを与えたり変更したりできる
