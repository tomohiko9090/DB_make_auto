# DB_make_auto.pyの説明
## 👉DB_make_auto.pyでできること
Slackからエクスポートされたjsonファイルから「message_table.csv」「reaction_table.csv」「channel_table.csv」「user_table.csv」「join_table.csv」「statistics.csv」「network.png」の7種類のファイルを作成することができます。  
(network.pngでは、Slack内の人間関係を可視化することができます！）  
## 👉データテーブルの設計
設計書のリンク
https://drawsql.app/--109/diagrams/database  

## 👉DB_make_auto.pyの使い方
使い方の動画↓  
https://www.youtube.com/watch?v=wZYC4_E3i6c   
1. Slackからjson形式のデータ(生データ)をエクスポートします。  
1. 生データと同じ階層にDB_make_auto.py移動させます。  
1. MacOSならターミナル、Windowsならコマンドプロンプトを開き、このファイルが置いてある階層まで移動してください。  
1. 'python3 DB_make_auto.py'を実行し、表示される指示に従って下さい。  
('ModuleNotFoundError'が発生した場合、ファイルで使用されていないモジュールがインストールされていません。'pip install'等でインストールしてからもう一度実行して下さい。)  
1. DB_make_auto.pyと同じ階層に7つのファイルが作成されているのを確認して下さい。(最初にnetworkのファイルを確認してください。人間関係が可視化されていればOKです)

