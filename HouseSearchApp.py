import streamlit as st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
import numpy as np

st.set_page_config(page_title="物件検索", page_icon="🌍")

st.markdown("# 物件検索")
st.sidebar.header("検索条件")
st.write()


@st.cache_data
def from_data_file(filename):
    url = (
        "http://raw.githubusercontent.com/streamlit/"
        "example-data/master/hello/v1/%s" % filename
    )
    return pd.read_json(url)


try:
    ALL_LAYERS = {
        "Bike Rentals": pdk.Layer(
            "HexagonLayer",
            data=from_data_file("bike_rental_stats.json"),
            get_position=["lon", "lat"],
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            extruded=True,
        ),
        "Bart Stop Exits": pdk.Layer(
            "ScatterplotLayer",
            data=from_data_file("bart_stop_stats.json"),
            get_position=["lon", "lat"],
            get_color=[200, 30, 0, 160],
            get_radius="[exits]",
            radius_scale=0.05,
        ),
        "Bart Stop Names": pdk.Layer(
            "TextLayer",
            data=from_data_file("bart_stop_stats.json"),
            get_position=["lon", "lat"],
            get_text="name",
            get_color=[0, 0, 0, 200],
            get_size=15,
            get_alignment_baseline="'bottom'",
        ),
        "Outbound Flow": pdk.Layer(
            "ArcLayer",
            data=from_data_file("bart_path_stats.json"),
            get_source_position=["lon", "lat"],
            get_target_position=["lon2", "lat2"],
            get_source_color=[200, 30, 0, 160],
            get_target_color=[200, 30, 0, 160],
            auto_highlight=True,
            width_scale=0.0001,
            get_width="outbound",
            width_min_pixels=3,
            width_max_pixels=30,
        ),
    }
    st.sidebar.markdown("### エリア")
    selected_layers = [
        layer
        for layer_name, layer in ALL_LAYERS.items()
        if st.sidebar.checkbox(layer_name, True)
    ]
    if selected_layers:
        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state={
                    "latitude": 37.76,
                    "longitude": -122.4,
                    "zoom": 11,
                    "pitch": 50,
                },
                layers=selected_layers,
            )
        )
    else:
        st.error("Please choose at least one layer above.")
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )

# サイドバーに表示するウィジェットを追加
st.sidebar.markdown("### 家賃")

# 下限と上限の初期値
default_min_value = 0.0
default_max_value = 100.0

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
    value=selected_range[0],
    key="min_value_input",
)
max_value_input = col2.number_input(
    "Enter maximum value",
    min_value=default_min_value,
    max_value=default_max_value,
    value=selected_range[1],
    key="max_value_input",
)

# 下限と上限の値を更新
selected_range = (min_value_input, max_value_input)

# メインエリアに選択された値を表示
st.write("選択されたレンジの値:", selected_range)


# 表
df = pd.DataFrame(np.random.randn(50, 7), columns=("col %d" % i for i in range(7)))

selected_column = st.selectbox("ソートする列を選択", df.columns)
sorted_df = df.sort_values(by=selected_column)

st.dataframe(sorted_df)


# チェックボックス

st.sidebar.markdown("### 間取り")
data_df = pd.DataFrame(
    {
        "favorite": [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ],
        "widgets": ["1R", "1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3K", "3DK", "4K"],
    }
)

st.sidebar.data_editor(
    data_df,
    column_config={
        "favorite": st.column_config.CheckboxColumn(
            "チェック",
            help="Select your **favorite** widgets",
            default=False,
        )
    },
    disabled=["間取り"],
    hide_index=True,
)

# 2列に分割
col1, col2 = st.sidebar.columns(2)

# ボタンがクリックされたかどうかを取得する
reset_clicked = col1.button("リセット", key="reset_button")
search_clicked = col2.button("検索", key="search_button")

# ボタンがクリックされた場合の処理
if reset_clicked:
    st.warning("リセットボタンがクリックされました")
elif search_clicked:
    st.success("検索ボタンがクリックされました")
