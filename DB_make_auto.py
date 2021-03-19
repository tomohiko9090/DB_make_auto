import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import datetime, os, itertools, json, glob
import warnings
import re
import matplotlib.pyplot as plt
import networkx as nx

print('「message_table」「reaction_table」「channel_table」「user_table」「join_table」「statistics」「network」の7種類のファイルが生成されます。')
data_files = input('DB作成するディレクトリ名を入力して下さい。\n例)C_Community Slack export Feb 18 2020 - Feb 10 2021  :')

# timestampを日本時間に変換してdfに結合
def timestamp(df, column, new_column):
    change = pd.to_datetime(df[column], unit='s') #変換
    lag = change + datetime.timedelta(hours=9)      #時差
    df[new_column] = lag                          #結合、

# メンバー辞書を使って、「与えられたidリスト」を新たなidに変換→「指定のリスト」に格納
# user_idを変換する場合、これを用いる(いつ新規ユーザが現れるかわからないため)
def user_id_change(変換前のリスト, 変換後のリスト):
    for ori_user in 変換前のリスト:
        #1
        if type(ori_user) == float:                                    
            変換後のリスト.append(np.nan)
        #2
        else:  
            #2.1
            value = None
            value = id_d.get(ori_user)
            if value != None:                             
                変換後のリスト.append(value)
            #2.2
            else:
                last_value = list(id_d.items())[-1][1]
                num_only = re.sub("\\D", "", last_value)              
                num_plus_one = int(num_only) + 1                      
                new_num = '%04d' % num_plus_one                   
                new_id = 'g' + new_num               
                id_d.update({ori_user:new_id})
                変換後のリスト.append(new_id)

# メンバー辞書を使って、「与えられたid単体」を新たなidに変換→「指定のリスト」に格納
def user_id_change_mini(変換前のid, 追加するリスト):
    #1
    if type(変換前のid) == float:                                    
        追加するリスト.append(np.nan)
    #2
    else:  
        #2.1
        value = None
        value = id_d.get(変換前のid)
        if value != None:                             
            追加するリスト.append(value)
        #2.2
        else:
            last_value = list(id_d.items())[-1][1]
            num_only = re.sub("\\D", "", last_value)              
            num_plus_one = int(num_only) + 1                      
            new_num = '%04d' % num_plus_one                   
            new_id = 'g' + new_num               
            id_d.update({変換前のid:new_id})
            追加するリスト.append(new_id)

# ----------------------------------------------------------------------------------------------------------------------
# メッセージテーブルの作成
# ステージ0
# ~チャネルテーブルとユーザテーブルの型を作成する~
#channel.json→各チャネル情報
channels = pd.read_json('./' + data_files + '/channels.json')

#channel_created_date_timeを追加
channel_table_nodrop = channels
timestamp(channel_table_nodrop, 'created', 'channel_created_date_time')

#データ項目名を整理
channel_table_nodrop = channel_table_nodrop.rename(columns={0:'channel_created_date_time', 'id':'original_channel_id', 'creator':'channel_cleator'})

#channel_idの作成
ch_num_list=[]
ch_num_len=np.arange(len(channel_table_nodrop))
for x in ch_num_len:
    h='%03d' % x#3桁にする
    ch_num_list.append('ch' + str(h))
channel_table_nodrop['channel_id'] = ch_num_list

#users.json→各ユーザ情報
users = pd.read_json('./' + data_files + '/users.json')

#データ項目名の整理
user_table_nodrop = users.rename(columns={'id':'user_id', 'tz':'time_zone', 'is_owner':'workspace_owner'})

#user_updated_date_timeを作成
timestamp(user_table_nodrop, 'updated', 'user_updated_date_time')

#user_fieldsを追加
field_list = []
for x in user_table_nodrop.profile:
    field_list.append(x['title'])
user_table_nodrop['user_fields'] = field_list

#bot_or_userを追加
bot_list = []
for x in user_table_nodrop.is_bot:
    if x==True:
        bot_list.append(0)
    else:
        bot_list.append(1)
user_table_nodrop['bot_or_user'] = bot_list
bot_numbers = user_table_nodrop[user_table_nodrop['bot_or_user'].astype(str).str.contains(str(0))]

#workspace_joiningを追加
joining_list = []
for x in user_table_nodrop.deleted:
    if x==True:
        joining_list.append(0)
    else:
        joining_list.append(1)
user_table_nodrop['workspace_joining'] = joining_list

#user_idを追加
id_list = []
leng = np.arange(len(user_table_nodrop))
for x in leng:
    num = '%04d' % x
    id_list.append(num)
user_table_nodrop = user_table_nodrop.rename(columns={'user_id':'original_user_id'})
user_table_nodrop['user_id'] = id_list
id_d = dict(zip(user_table_nodrop['original_user_id'], user_table_nodrop['user_id']))

########################################################
#ステージ1
warnings.filterwarnings('ignore')# 警告を出ないようにする

ms_data1 = DataFrame(index=[])
chname_chid = channel_table_nodrop.loc[:,['name','channel_id']]

#チャネルの名前を抽出
json_count_list = []
for ch in channel_table_nodrop.name:
    channel_data = DataFrame(index=[])
    files = os.listdir('./'+ data_files + '/' + ch)
    #隠しファイルを取り除く
    date_list = [i for i in files if '.json' in i]
    json_count_list.append(len(date_list))
    
    #日付ファイルを読み込む
    for date in date_list:
        json_data = pd.read_json('./'+ data_files + '/' + ch + '/' + date)
        channel_data = pd.concat([channel_data, json_data])#json_dateを中元に合体
    
    #channel_idをデータ項目に追加
    channel_id_array = []
    for i in chname_chid.values.tolist():
        if ch == i[0]:
            #データの数だけchannel_idを用意
            for _ in range(len(channel_data)):
                channel_id_array.append(i[1])
    channel_data = channel_data.join(DataFrame(channel_id_array))#データ項目(横)に追加
    #channel_dataを大元に合体
    ms_data1 = pd.concat([ms_data1, channel_data])
#データ項目名の変更
ms_data1 = ms_data1.rename(columns={0:'channel_id'})

#ソート
ms_data1 = ms_data1.sort_values('ts')
ms_data1 = ms_data1.reset_index()
#####################################################################
#ステ-ジ2
# タイムスタンプでsortしてからインデックス番号を再設定
ms_data2 = ms_data1.sort_values('ts')
ms_data2 = ms_data2.reset_index()

# thread_idを作成
# 辞書を作成
thread_unique = ms_data2['thread_ts'].dropna().unique().tolist() # nanを除外→ユニーク抽出
unique_d = {}
for ts in thread_unique:
    value = unique_d.get(ts) # getの中身がkey
    if not value: # 新規登録
        num = '%04d' % len(unique_d)
        unique_d[ts] = 'th'+ str(num)
    else:
        pass
unique_d[np.nan] = np.nan # nanだけ手動で追加

# dfから辞書を使用してthread_idを挿入
thread_id_list = []
for ts in ms_data2['thread_ts']:
    thread_id_list.append(unique_d.get(ts))
ms_data2['thread_id'] = thread_id_list

user_id_array = []
user_id_change(ms_data2.user, user_id_array)  
ms_data2['from_user_id'] = user_id_array

# thead→スレッドでない(0)、スレッド(1)、thread_broadcast(2)
th_data_new = []
for index,i in enumerate(ms_data2.thread_ts):
    # thread_tsがnan⇦botも含む
    if str(i) == str(np.nan):
        th_data_new.append(0)
    else:
        # subtypeがthread_broadcastのとき
        if ms_data2.subtype[index] == 'thread_broadcast':
            th_data_new.append(2)
        # subtypeに何も入っていないとき(つまり普通のスレッド)
        else:
            th_data_new.append(1)

ms_data2['thread'] = th_data_new

# parent_user_id→スレッドデータの場合、スレッド親のuser_idが入力される
ms_data2 = ms_data2.rename(columns = {'parent_user_id':'original_parent_user_id'})

parent_data = ms_data2.original_parent_user_id.values.tolist()
parent_arr = []
user_id_change(parent_data, parent_arr)

ms_data2['parent_user_id'] = parent_arr

#reply_user_id_listの作成
ms_data2 = ms_data2.rename(columns={'reply_users':'original_reply_users'})
reply_users_arr = []
for i in ms_data2.original_reply_users:
    if str(i)=='nan':
        reply_users_arr.append(np.nan)
    else:
        re_u = []
        user_id_change(i, re_u)#リプライしたユーザを一ずつ取り出すex)['UQF8MS7FG', 'U0K1CG4U9']   
        reply_users_arr.append(re_u)

ms_data2['reply_user_id_list'] = reply_users_arr

#　n_reactionsの作成
n_reactions_arr = []
for i in ms_data2.reactions:
    if type(i)==float:
        n_reactions_arr.append(np.nan)
    elif type(i)!=float:
        n_reactions_arr.append(sum([j['count'] for j in i]))
ms_data2['n_reactions'] = n_reactions_arr


#　msg_date_timeの作成
timestamp(ms_data2, 'ts', 'msg_date_time')

#　thread_parent_date_timeの作成
timestamp(ms_data2, 'thread_ts', 'thread_parent_date_time')

# thread_parentの作成
ms_data2['thread_parent']=[0 if str(i)=='nan' else 1 for i in ms_data2.reply_users_count]

############################################################################################################
#ステージ3
#〜メンションごとにデータを分割〜

double_table = []
text_index_number = ms_data2.columns.values.tolist().index('text') #カラムの何番目ってやつ
for index,line_total in enumerate(ms_data2.values.tolist()):
    # ①メンションありメッセージ
    text = line_total[text_index_number]
    if '<@' in text: # メンション情報があるか判定
        trans = re.findall('<@U.*>', text)                                                          # ざっくりメンション情報が入った文字列を抽出
        sp1 = "".join(map(str, trans)).split(' ')                                                   # ユーザ毎にわける
        sp2 = [re.findall('<@(.*)>', j)[0].split('>') for j in sp1 if re.findall('<@(.*)>', j)!=[]] # いらない部分を削ぐ
        one_dim = sum(sp2,[]) 
        double_table.append([line_total+re.findall('(U.*)', j) for j in one_dim])                   # one_dimの数だけデータを作成
           
    elif '<!channel>' in text: 
        double_table.append([line_total+['channel']])
    elif '<!here>' in text:
        double_table.append([line_total+['here']])
    #②メンションなしメッセージ
    else:
        double_table.append([line_total + ['NaM']])
new_table = sum(double_table, [])#original_user_idのリスト
new_df = DataFrame(new_table, columns=ms_data2.columns.values.tolist()+['original_mention_user_id'])#データ項目名のついたデータフレーム

#user_idに変換したリストを作成する
original_id_list = new_df.original_mention_user_id.values.tolist()
mention_user_id_list = []
for i in original_id_list:
#     guest_d = dict(zip(guest_df[0], guest_df[1]))
    #①メンションなし→NaM
    if i=='NaM':
        mention_user_id_list.append('NaM')
        pass
    #②channelとhereの場合
    elif i=='channel':
        mention_user_id_list.append('channel')
        pass
    elif i=='here':
        mention_user_id_list.append('here')
        pass
    #③ダイレクトメンション→user_id
    else:
        user_id_change_mini(i, mention_user_id_list)

#new_dfとmention_user_id_listを結合
new_df['mention_user_id'] = mention_user_id_list
message_table_nodrop = new_df

# subtypeからuser,botメッセージ以外をdropする(message_table_nodropはdrop前のデータを残しておくことにする)
exclusion_l = ['message_changed','channel_join','channel_topic','channel_purpose','channel_name','channel_archive','channel_unarchive',
 'group_join','group_leave','group_topic','group_purpose','group_name','group_archive','group_unarchive','file_share',
 'file_reply','file_mention','pinned_item','unpinned_item']

index_list = []
for sub in exclusion_l:
    index = list(message_table_nodrop[message_table_nodrop['subtype'].astype(str).str.contains(str(sub))].index)
    index_list.append(index)
    
index_list = sum(index_list,[])
message_table = message_table_nodrop.drop(index_list)
message_table = message_table.drop('level_0', axis=1)
message_table = message_table.reset_index()
message_table = message_table.reindex(columns=['msg_date_time', 'channel_id', 'from_user_id', 'mention_user_id', 'n_reactions', 'thread' ,'thread_parent',
                                'parent_user_id', 'reply_users_count', 'reply_user_id_list', 'thread_parent_date_time', 'thread_id', 'client_msg_id'])


# 最後にms_data3(メンションで分割せずに、メンション情報がリストになったdf)を作成
# 辞書を作成
ts_d = {}
for index, row in message_table.iterrows():
    time = row.msg_date_time
    mention = row.mention_user_id
    value_l = ts_d.get(time)
    if not value_l: #辞書に登録されてないtsだった場合
        ts_d[time] = [mention]
    elif len(value_l) > 0: #登録済みの場合
        #リストにメンションユーザを追加
        value_l.append(mention) #上書きでvalue_lにメンションidを追加

# msg_date_timeのユニーク抽出
ms_data3 = message_table.drop_duplicates(subset='msg_date_time')

# 辞書を使ってdfくっつける
ms_data3['mention_id_list'] = [ts_d.get(ts) for ts in ms_data3['msg_date_time']]
ms_data3 = ms_data3.reset_index()
ms_data3 = ms_data3.reindex(columns=['msg_date_time', 'channel_id', 'from_user_id', 'mention_id_list', 'n_reactions', 'thread' ,'thread_parent',
                                'parent_user_id', 'reply_users_count', 'reply_user_id_list', 'thread_parent_date_time', 'thread_id', 'client_msg_id'])

print('メッセージテーブルの作成完了')

# ----------------------------------------------------------------------------------------------------------------------
# リアクションテーブルの作成
# メッセージテーブル作成途中のからms_data2を使用
message_data = ms_data2.loc[:,['ts', 'from_user_id' ,'reactions', 'client_msg_id']]

# Slackオリジナルのデータ項目”reactions”が欠損値になっているところは除外
reaction_table_nodrop = message_data.dropna(subset=['reactions'])
reaction_table_nodrop = reaction_table_nodrop.reset_index()

# reaction_date_timeの作成
timestamp(reaction_table_nodrop, 'ts', 'reaction_date_time')

# reaction_user_id_listの作成
user_id_list = []
# total_user_d = dict(zip(user_table_nodrop['original_user_id'], user_table_nodrop['user_id']))
rea_id_l = [rea[0]['users'] for rea in reaction_table_nodrop.reactions]

for user_l in rea_id_l:
    user_list2 = []
    user_id_change(user_l, user_list2)
    user_id_list.append(user_list2)
reaction_table_nodrop['reaction_user_id_list'] = user_id_list

# n_reactionsの作成
n_reactions_list = [rea[0]['count'] for rea in reaction_table_nodrop.reactions]
reaction_table_nodrop['n_reactions'] = n_reactions_list

# 使用データ抽出
reaction_table = reaction_table_nodrop.reindex(columns=['reaction_date_time', 'from_user_id', 'n_reactions', 'reaction_user_id_list', 'client_msg_id'])

print('リアクションテーブルの作成完了')

# ----------------------------------------------------------------------------------------------------------------------
# チャネルテーブルの作成
# member_id_listの作成
channel_member_list = []
for id_list in channel_table_nodrop.members:
    member_list = []
    if id_list!=[]:
        user_id_change(id_list, member_list)
    channel_member_list.append(member_list)
channel_table_nodrop['member_id_list'] = channel_member_list

# number_of_memberの作成
channel_table_nodrop['number_of_member'] = [len(i) for i in channel_table_nodrop.member_id_list]

# channel_cleator_idの作成
cleator_list = []
user_id_change(channel_table_nodrop.channel_cleator, cleator_list)

channel_table_nodrop['channel_cleator_id'] = cleator_list
channel_table = channel_table_nodrop.reindex(columns=['channel_created_date_time', 'channel_id', 'original_channel_id',  
                                                      'channel_cleator_id', 'number_of_member', 'member_id_list'])

print('チャネルテーブルの作成完了')

# ----------------------------------------------------------------------------------------------------------------------
# ユーザテーブルの作成
# user_table_nodropに id_d を結合する
guest_df = DataFrame([i for i in list(id_d.items()) if 'g' in i[1]])
guest_df.columns = ['original_user_id', 'user_id']
user_table_nodrop = pd.concat([user_table_nodrop, guest_df])
user_table_nodrop = user_table_nodrop.reset_index()

#channel_listを追加
ch_menbers = channel_table.loc[:,['member_id_list','channel_id']]
menbers_ch = []
for user_id in user_table_nodrop.user_id:
    men_box = []
    for pair in ch_menbers.values.tolist():
        if user_id in pair[0]:      
            men_box.append(pair[1])
        else:
            pass
    menbers_ch.append(men_box)
user_table_nodrop['channel_id_list'] = menbers_ch

user_table = user_table_nodrop.reindex(columns=['user_id', 'original_user_id', 'workspace_owner', 'workspace_joining', 
                                                'bot_or_user', 'user_fields', 'channel_id_list', 'time_zone', 'user_updated_date_time']).reset_index(drop=True)
user_table = user_table.fillna({'bot_or_user': 1.0, 'workspace_joining': 1.0})

print('ユーザテーブルの作成完了')
# ----------------------------------------------------------------------------------------------------------------------
# ユーザテーブルの作成
# メッセージテーブルを使用
join_table_nodrop = message_table_nodrop[message_table_nodrop['subtype'].astype(str).str.contains(str('channel_join|channel_leave'))]

# user_date_timeの作成
timestamp(join_table_nodrop, 'ts', 'user_date_time')

# user_idの作成
join_table_nodrop = join_table_nodrop.rename(columns={'from_user_id':'user_id'})

# join_leaveの作成
join_leave_list = [1 if i=='channel_join' else -1 for i in join_table_nodrop.subtype]
join_table_nodrop['join_leave'] = join_leave_list

# 使用データ抽出
join_table = join_table_nodrop.reindex(columns=['user_date_time', 'channel_id', 'user_id', 'join_leave'])

print('ジョインテーブルの作成完了')

# ----------------------------------------------------------------------------------------------------------------------
# 統計量
statistics_list = []
statistics_list.append('読み込んだjsonファイル数は、{}'.format(sum(json_count_list)))

# メッセージ基本統計
statistics_list.append('')
statistics_list.append('①メッセージ基本統計')
statistics_list.append('メッセージ総数(botのmsgも含む)は、{}'.format(len(ms_data3)))
statistics_list.append('botのメッセージ数は、{}'.format(len(ms_data3[ms_data3['from_user_id'].astype(str).str.contains(str('nan'))])))
statistics_list.append('メンション分割後のメッセージ総数(botのmsgも含む)は、{}'.format(len(message_table)))
mention_of_number = len(message_table)-len(message_table[message_table['mention_user_id'].astype(str).str.contains(str('NaM'))]) #メンションメッセージ数(行分割済) / 全メッセージ数
mention_percentage = mention_of_number/len(message_table)
statistics_list.append('メンションの割合(ただし、メンションデータは分割済)は、{:.3f}'.format(mention_percentage))
thread_parent_data = ms_data2[ms_data2['thread_parent'].astype(str).str.contains(str(1))] #スレッド数=スレッド親の数
statistics_list.append('スレッド数は、{}'.format(len(thread_parent_data)))
statistics_list.append('スレッドmsg数は、{}'.format(th_data_new.count(1)))
statistics_list.append('スレッド親のユニーク数は、{}'.format(len(ms_data2.parent_user_id.unique())))
thread_of_number = ms_data2[ms_data2['thread'].astype(str).str.contains(str(1))] #(スレッドmsg数 - スレッド親の数) / スレッド数
statistics_list.append('スレッド上でのリプライ数(スレッドの子にあたる)の平均は、{:.3f}'.format((len(thread_of_number)-len(thread_parent_data)) / len(thread_parent_data)))
reply_total = thread_parent_data.reply_users_count.sum() # スレッド内で返信したユニークユーザの合計
reply_user_list = thread_parent_data.reply_user_id_list
gest_reply_of_number = []
for List in reply_user_list:
    gest_reply_of_number.append(len([user for user in List if 'g' in user]))
gest_reply_total = sum(gest_reply_of_number) # 返信した人の中からゲストの数を数え、足したもの
statistics_list.append('返信したユーザの中でWS外のユーザである割合は、{:.3f}'.format(gest_reply_total / reply_total))

# リアクション基本統計
statistics_list.append('')
statistics_list.append('②リアクション基本統計')
statistics_list.append('リアクションのついたメッセージ総数は、{}'.format(len(ms_data2) - len(ms_data2[ms_data2['n_reactions'].astype(str).str.contains(str(np.nan))])))
statistics_list.append('リアクションがあるmsgデータの平均リアクション数は、{:.3f}'.format(reaction_table.n_reactions.mean()))  

# チャネル基本統計
statistics_list.append('')
statistics_list.append('③チャネル基本統計')
statistics_list.append('チャネル総数は、{}'.format(len(channel_table_nodrop.name)))
statistics_list.append('チャネルの平均メンバー数は、{:.2f}'.format(channel_table.number_of_member.mean()))
statistics_list.append('チャネルの平均発話数は、{:.2f}'.format(len(ms_data2)/len(channel_table)))
statistics_list.append('チャネルクリエイターのユニークユーザー数は、{}'.format(len(channel_table.channel_cleator_id.unique())))
user_join_leave = []
for channel in channel_table.channel_id:
    user_join_leave.append(len(join_table[join_table['channel_id'].astype(str).str.contains(str(channel))]))
statistics_list.append('チャネルの入退室したユーザ数の平均値は、{:.2f}'.format(np.mean(user_join_leave)))

# ユーザ基本統計
statistics_list.append('')
statistics_list.append('④ユーザ基本統計')
statistics_list.append('ユーザ(bot含む)の総数は、{}'.format(len(user_table)))
statistics_list.append('botの数は、{}'.format(len(bot_numbers)))
statistics_list.append('WS内ユーザ(botも含む)の数は、{}'.format(len(users)))
statistics_list.append('WS外ユーザ数は、{}'.format(len(guest_df)))
workspace_joining_leave = user_table[user_table['workspace_joining'].astype(str).str.contains(str(0.0))]
statistics_list.append('WS脱退者数は、{}'.format(len(workspace_joining_leave)))
channel_user_list = channel_table.member_id_list #WS外のユーザ数/チャネル全ユーザ数
channel_of_gest_member = []
for List in channel_user_list:
    channel_of_gest_member.append(len([user for user in List if 'g' in user]))
gest_total = sum(channel_of_gest_member)
total = sum([len(i) for i in channel_table.member_id_list])
statistics_list.append('チャネルに参加するWS外のユーザの割合の平均は、{:.5f}'.format(gest_total / total))
ch_length = []
for i in user_table[user_table['bot_or_user'].astype(str).str.contains(str(1.0))].channel_id_list:
    ch_length.append(len(i))
statistics_list.append('1ユーザ平均チャネル所属数(bot抜き)数は、{:.2f}'.format(np.mean(ch_length)))
time_zone_unique = list(user_table.time_zone.unique())
time_zone_unique.remove(np.nan)
statistics_list.append('タイムゾーンユニーク数は、{}'.format(len(time_zone_unique)))
joining = user_table[user_table['workspace_joining'].astype(str).str.contains(str(1.0))]
joining_user = user_table[user_table['bot_or_user'].astype(str).str.contains(str(1.0))]
last_3_months = []
month_list = sorted(list(set([i.strftime('%Y-%m') for i in ms_data2.msg_date_time])))
for month in month_list[:-3]:
    last_3_months.append(len(joining_user[joining_user['user_updated_date_time'].astype(str).str.contains(str(month))]))
statistics_list.append('直近3ヶ月間何も発話していないユーザの数(ワークスペース離脱者、bot抜き)は、{:.3f}'.format(sum(last_3_months)))                       

# ジョイン基本統計
statistics_list.append('')
statistics_list.append('⑤ジョイン基本統計')
statistics_list.append('チャネルへの参加および離脱の総数は、{}'.format(len(join_table)))
channel_join_leave = []
for user in user_table.user_id:
    channel_join_leave.append(len(join_table[join_table['user_id'].astype(str).str.contains(str(user))]))
statistics_list.append('ユーザ(bot含む)のチャネル参加離脱平均数は、{:.2f}'.format(np.mean(channel_join_leave)))

pd.set_option("display.max_colwidth", 80)
statistics = Series(statistics_list).str.ljust(70)

print('統計データ集計ファイルの作成完了')

# ----------------------------------------------------------------------------------------------------------------------
# ネットワーク作図
# データの調整 
hit1 = message_table[message_table['mention_user_id']!=str('NaM')]
hit2 = hit1[hit1['mention_user_id']!=str('here')]
hit3 = hit2[hit2['mention_user_id']!=str('channel')]

# Graphオブジェクトの作成
G = nx.Graph(name=data_files)

# edgeデータの追加
to_from_list = hit3.loc[:,['from_user_id', 'mention_user_id']].values.tolist()
edge_list = [(to_from[0], to_from[1]) for to_from in to_from_list if to_from[0]!=to_from[1]]
d = dict(zip(user_table_nodrop['user_id'], user_table_nodrop['real_name']))
edge_list2 = []
for pair in edge_list:
    edge_list2.append((d.get(pair[0]), d.get(pair[1])))
G.add_edges_from(edge_list2)

# ネットワークの可視化
plt.figure(figsize=(14,14), dpi=120)
pos = nx.spring_layout(G) # springを使用 , k=1.0

plt.rcParams['font.family'] = 'MS Gothic'
nx.draw(G, pos, with_labels = True, font_family='Osaka', node_color = 'green', alpha=0.8)
print('ネットワークの描画完了')

# ------------------------------------------------------------------------------------------------------------------------------
message_table.to_csv('message_table for ' + data_files + '.csv')
reaction_table.to_csv('reaction_table for ' + data_files + '.csv')
channel_table.to_csv('channel_table for ' + data_files + '.csv')
user_table.to_csv('user_table for ' + data_files + '.csv')
join_table.to_csv('join_table for ' + data_files + '.csv')
statistics.to_csv('statistics for ' + data_files + '.csv')

plt.savefig('network for ' + data_files + '.png')