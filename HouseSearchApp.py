import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import gspread
from google.oauth2 import service_account
import folium


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SERVICE_ACCOUNT_FILE = "/Users/Hironori/Python.py/service_account.json"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
client = gspread.authorize(credentials)

# Google SheetsのURLまたはシート名を指定
sheet_url = "https://docs.google.com/spreadsheets/d/1jmFtkvFg2sO39LZUaiet-uX-7OoydqDBQZlr3SxXd0g/edit#gid=1480819835"  # Google SheetsのURL
# シートを開く
sheet = client.open_by_url(sheet_url)
worksheet = sheet.get_worksheet(2)  # シート番号を指定してワークシートを取得

# データをDataFrameに読み込む
data = worksheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])
df["家賃"] = df["家賃"].astype(int)

# Streamlitでデータを表示
# st.write(df)


st.markdown("# 物件検索")
st.sidebar.header("検索条件")
st.write()


# サイドバーに表示するウィジェットを追加
st.sidebar.write("ここで検索条件を選択します。")

# サイドバーに表示するウィジェットを追加
st.sidebar.markdown("### 家賃")

# 下限と上限の初期値
default_min_value = 0
default_max_value = 1000000

# 2列に分割
col1, col2 = st.sidebar.columns(2)

# 1列目にスライダーを配置
selected_range = col1.slider(
    "Select a range of values",
    default_min_value,
    default_max_value,
    (default_min_value, default_max_value),
    key="range_slider_col",
)

# 2列目に数値入力ボックスを配置
min_value_input = col2.number_input(
    "Enter minimum value",
    min_value=default_min_value,
    max_value=default_max_value,
    value=int(selected_range[0]),  # 整数型にキャスト
    key="min_value_input",
)
max_value_input = col2.number_input(
    "Enter maximum value",
    min_value=default_min_value,
    max_value=default_max_value,
    value=int(selected_range[1]),  # 整数型にキャスト
    key="max_value_input",
)

# 下限と上限の値を更新
selected_range = (min_value_input, max_value_input)


# サイドバーに間取りのチェックボックスを追加
st.sidebar.markdown("### 間取り")
# 間取りのチェックボックスを追加し、選択状態を取得
selected_layouts = st.sidebar.checkbox("ワンルーム")
selected_layouts2 = st.sidebar.checkbox("1K")
selected_layouts3 = st.sidebar.checkbox("1DK")
selected_layouts4 = st.sidebar.checkbox("1LDK")
selected_layouts5 = st.sidebar.checkbox("2K")
selected_layouts6 = st.sidebar.checkbox("2DK")
selected_layouts7 = st.sidebar.checkbox("2LDK")
selected_layouts8 = st.sidebar.checkbox("3K")
selected_layouts9 = st.sidebar.checkbox("4K")


layout_options = {
    "ワンルーム": selected_layouts,
    "1K": selected_layouts2,
    "1DK": selected_layouts3,
    "1LDK": selected_layouts4,
    "2K": selected_layouts5,
    "2DK": selected_layouts6,
    "2LDK": selected_layouts7,
    "3K": selected_layouts8,
    "4K": selected_layouts9,
}

selected_layout_list = [
    layout for layout, selected in layout_options.items() if selected
]

# 2列に分割
col1, col2 = st.sidebar.columns(2)


# ボタンがクリックされたかどうかを取得する
search_clicked = col2.button("検索", key="search_button")
reset_clicked = col1.button("リセット", key="reset_button")

# ボタンがクリックされた場合の処理
if reset_clicked:
    st.warning("リセットボタンがクリックされました")
    # リセットボタンがクリックされた場合は、ボタンとフィルタリングをリセット
    selected_layouts = [False, False, False, False, False, False, False, False]
    min_value_input = default_min_value
    max_value_input = default_max_value
    filtered_df = df

# ボタンがクリックされた場合の処理
if search_clicked:
    st.success("検索ボタンがクリックされました")

    # 絞り込み条件に基づいてデータをフィルタリング
    filtered_df = df[(df["家賃"] >= min_value_input) & (df["家賃"] <= max_value_input)]
    if selected_layout_list:
        filtered_df = filtered_df[filtered_df["間取り"].isin(selected_layout_list)]

    # フィルタリングされたデータを新しいDataFrameに格納
    result_df = filtered_df

elif reset_clicked:
    st.warning("リセットボタンがクリックされました")
    # リセットボタンがクリックされた場合は、元のデータを表示
    result_df = df

# Reset index and rename the column
result_df = result_df.reset_index(drop=True).reset_index()
result_df.rename(columns={"index": "New Index"}, inplace=True)


# Streamlitのウェブページを表示
st.write("## 物件検索")


# pydeck layer with tooltip
layer = pdk.Layer(
    "ScatterplotLayer",
    data=result_df,
    get_position=["経度", "緯度"],
    get_color=[255, 140, 0],
    get_radius=100,
    pickable=True,
    auto_highlight=True,
    # Add tooltip to display index
    tooltip={"text": "Index: {New Index}"},
)


# pydeckの地図を作成
view_state = pdk.ViewState(
    latitude=35.6895,
    longitude=139.6917,
    zoom=11,
)

# 地図にピンを追加
map_deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    layers=[layer],
    initial_view_state=view_state,
)


# Streamlitに地図を表示
st.pydeck_chart(map_deck)
# 表

# 表示したい列をリストとして定義します
columns_to_display = ["New Index", "物件名", "家賃", "住所", "階", "間取り"]
selected_df = result_df[columns_to_display]

selected_column = st.selectbox(
    "ソートする列を選択", selected_df.columns, index=0, key="sort_column"
)

sorted_df = selected_df.sort_values(by=selected_column)

st.dataframe(sorted_df)
