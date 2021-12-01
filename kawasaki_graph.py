import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go




filename = r"summary.xlsx"
df = pd.read_excel(filename)
#データ成形
df["児童数"]=df["児童数"].replace("廃校",np.nan)
df["内特別支援学級児童数"] = df["内特別支援学級児童数"].replace("-",np.nan)
df["内特別支援学級数"]=df["内特別支援学級数"].fillna(0)
df["内特別支援学級数"] = df["内特別支援学級数"].replace("-",np.nan)
df = df.fillna(0)
df[["児童数","内特別支援学級児童数","学級数","内特別支援学級数"]] = df[["児童数","内特別支援学級児童数","学級数","内特別支援学級数"]].astype(int)


#関数の定義

def judge():
    if finish_n - start_n > 0:
        up_or_down = "増加"
    else:
        up_or_down = "減少"
    return(up_or_down)





#グラフ化
st.title("Kawasaki目線")
st.write('''
 川崎市が公表しているオープンデータを基にインタラクティブな分析を行うことができます。
 分析を行いたい内容について、下記のボタンを押してください。
 ''')




#全体の集計
st.subheader("■市全体の集計・分析内容")
df_chart_summary = df.pivot_table(values=["児童数","内特別支援学級児童数","学級数","内特別支援学級数"],index="集計年",aggfunc=sum)



fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Bar(x=df_chart_summary.index, y=df_chart_summary["児童数"], name="児童数"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df_chart_summary.index, y=df_chart_summary["学級数"], name="学級数"),
    secondary_y=True,
)



fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(
    go.Bar(x=df_chart_summary.index, y=df_chart_summary["内特別支援学級児童数"], name="特別支援学級児童数"),
    secondary_y=False,
)

fig2.add_trace(
    go.Scatter(x=df_chart_summary.index, y=df_chart_summary["内特別支援学級数"], name="特別支援学級数"),
    secondary_y=True,
)



st.plotly_chart(fig)


#<<<<市全体の分析結果
#全期間における児童生徒数の増加数・増加率→コメント　＋　一覧表
students_n = (df_chart_summary.iloc[-1][0])-(df_chart_summary.iloc[0][0])
students_s = (df_chart_summary.iloc[-1][1])-(df_chart_summary.iloc[0][1])

if students_n > 0:
    st.write("過去" + str(len(df_chart_summary)) + "年間で、児童生徒数は" + str(students_n) + "人増加しました")
    st.write(str(students_n/df_chart_summary.iloc[0][0]*100) + "%増加したことになります。")
else:
    st.write("過去" + str(len(df_chart_summary)) + "年間で、児童生徒数は" + str(students_n) + "人減少しました。")
    st.write(str(round(students_n/df_chart_summary.iloc[0][0]*100,2)) + "%減少したことになります。")
    st.write("児童生徒数が減少している背景としては、少子化の影響が考えられます。")



st.plotly_chart(fig2)



if students_s > 0:
    st.write("過去" + str(len(df_chart_summary)) +"年間で、特別支援学級の児童数は" + str(students_s) + "人増加しました")
    st.write(str(round(students_s/df_chart_summary.iloc[0][1]*100,2)) + "%増加したことになります。")
    st.write("特別支援学級の児童が増加している背景としては、医療の発達が考えられます。")
else:
    st.write("過去" + str(len(df_chart_summary)) +"で、特別支援学級の児童数は" + str(students_s) + "人減少しました")
    st.write(str(round(students_s/df_chart_summary.iloc[0][1]*100,2)) + "%減少したことになります。")


st.write("（注意）特別支援学級の児童数・学級数は、上記児童数・学級数の再掲値です。")

#過去５年間における児童生徒数の増加数・増加率→コメント　＋　一覧表




#行政区単位の児童数推移
st.subheader("■各学校ごとの集計・分析")
st.sidebar.write("個別集計を表示することができます")

genre = st.sidebar.selectbox("表示したい集計内容を選択してください",
options=["児童数","内特別支援学級児童数","学級数","内特別支援学級数"])



gyosei_list = st.sidebar.selectbox("推移を見たい行政区を選択してください",
options=df["行政区"].unique()
)

df_chart = df[(df["行政区"]==gyosei_list)]

school_list = st.sidebar.selectbox("学校を選択してください",
options=df_chart["学校名"].unique())

df_chart = df_chart[(df_chart["学校名"]==school_list)]

min_year = df_chart["集計年"].min().item()
max_year = df_chart["集計年"].max().item()
year = st.sidebar.slider("表示する年数を選択してください",
min_value=min_year,max_value=max_year,step=1,value=(min_year,max_year))

edu_chart=px.bar(df_chart,
x= "集計年",
y=genre,
range_x=year
)

st.plotly_chart(edu_chart)


#<<<<学校ごとの分析内容
#step1 該当の学校の、指定のジャンルのデータフレームを生成する
#（df_chartの集計年をインデックスに設定し、locアトリビュートで、指定の期間・指定の列名を抽出する。
#その後、最初と最後の年の数の比較をする

df_chart = df_chart.set_index("集計年")
df_analy_school = df_chart.loc[year[0]:year[1],[genre]]
start_n = df_analy_school.iloc[0][0]
finish_n = df_analy_school.iloc[-1][0]

st.write(gyosei_list + school_list + "の" + genre + "を表示しています")
#表示されている最初と最後の年の比較
st.write("表示されている" + str(year[1]-year[0]) + "年間において、" + str(genre) + "は" + str(finish_n - start_n) + "人" + judge() + "しました")
#増減率
st.write("増減率は" + str(round((finish_n-start_n)/start_n*100,2)) + "%です")
#表示されている期間のうち、最も多かった年と数

#表示されている期間のうち、最も少なかった年と数

#表示されている期間の平均値

#学校の連絡先・所在地

#学校のURL


#学校配置図
#緯度・経度情報取得→なぜか表示されない・・・。いったん保留。
# filename_public =r"C:\Users\ryohe_iyzrwas\Desktop\MyPythonProject\01Python開発\02川崎市児童生徒数等グラフ化\public_facility_school.xlsx"
# df_public = pd.read_excel(filename_public)
# df_public =df_public[["経度","緯度"]]
# df_public = df_public.rename(columns={"緯度":"lon","経度":"lat"})


# st.map(df_public,1,use_container_width=False)










st.subheader("補足")
st.write("本サイトは川崎市が公表しているオープンデータを加工しています")
st.write("出典：川崎市オープンデータ  https://www.city.kawasaki.jp/shisei/category/51-7-0-0-0-0-0-0-0-0.html")