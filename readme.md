DB_make_auto.pyの仕様
## ★DB_make_auto.pyでできること
Slackのエクスポートデータから「message_table」「reaction_table」「channel_table」「user_table」「join_table」「statistics」「network」の7種類のファイルを作成することができます。
## ★DB_make_auto.pyの使い方
①生データと同じ階層にDB_make_auto.py移動させます。
②MacOSならターミナル、Windowsならコマンドプロンプトを開き、このファイルが置いてある階層まで移動してください。
③以下を実行し、表示される指示に従って下さい。
('ModuleNotFoundError'が発生した場合、ファイルで使用されていないモジュールがインストールされていません。'pip install'等でインストールしてからもう一度実行して下さい。)
'''
python3 DB_make_auto.py
'''
④DB_make_auto.pyと同じ階層に7つのファイルが作成されているのを確認して下さい。
