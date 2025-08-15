import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime
from src.global_settings import SCORES_FILE
import plotly.graph_objects as go
import src.sidebar as sidebar

st.set_page_config(layout="wide")

# Hàm đọc dữ liệu từ file JSON
def load_scores(file, specific_username):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file, 'r') as f:
            data = json.load(f)

        # Ensure data is a list of records (each record is a dictionary)
        if isinstance(data, dict):
            data = [data]  # Wrap single record in a list

        df = pd.DataFrame(data)
        new_df = df[df["username"] == specific_username]
        return new_df
    else:
        return pd.DataFrame(columns=["username", "Time", "Score", "Content", "Total guess"])

def score_to_numeric(score):
    score = score.lower()
    if score == "bad":
        return 1
    elif score == "average":
        return 2
    elif score == "quite good":
        return 3
    elif score == "good":
        return 4

def plot_scores(df):
    # Chuyển đổi cột 'Time' thành kiểu datetime
    df['Time'] = pd.to_datetime(df['Time'])

    # Lọc dữ liệu trong vòng 7 ngày từ ngày gần nhất
    recent_date = df['Time'].max()
    start_date = recent_date - pd.Timedelta(days=6)
    df_filtered = df[(df['Time'] >= start_date) & (df['Time'] <= recent_date)]

    # Sắp xếp dữ liệu theo thời gian
    df_filtered = df_filtered.sort_values(by='Time')

    # Định nghĩa bảng màu
    color_map = {
        'bad': 'red',
        'average': 'orange',
        'quite Good': 'yellow',
        'good': 'green'
    }

    # Ánh xạ các giá trị 'Score' tới màu sắc
    df_filtered['color'] = df_filtered['Score'].map(color_map)
    
    # Tạo biểu đồ sử dụng Plotly
    fig = go.Figure()

    # Vẽ đường nối giữa các điểm theo thời gian
    fig.add_trace(go.Scatter(
        x=df_filtered['Time'],
        y=df_filtered['Score_num'],
        mode='lines+markers',
        marker=dict(size=24, color=df_filtered['color']),
        text=df_filtered['Score'],
        line=dict(width=2)
    ))

    # Cài đặt các thông số cho biểu đồ
    fig.update_layout(
        xaxis_title='Day',
        yaxis_title='Score',
        xaxis=dict(tickformat='%Y-%m-%d'),
        yaxis=dict(tickvals=[1, 2, 3, 4], ticktext=['Bad', 'Average', 'Quite Good', 'Good']),
        hovermode='x unified'
    )

    # Sử dụng Streamlit để hiển thị biểu đồ
    st.plotly_chart(fig)
    
def main():
    sidebar.show_sidebar()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        # Tạo giao diện với Streamlit
        st.markdown('# Track your mental health information')
        
        # Lấy dữ liệu từ file
        df = load_scores(SCORES_FILE, st.session_state.username)
        if not df.empty:
            df["Time"] = pd.to_datetime(df["Time"])
            df["Score_num"] = df["Score"].apply(score_to_numeric)
            df["Score"] = df["Score"].str.lower()
            # Hiển thị biểu đ�� sức kh��e tinh thần
            st.markdown("## Your mental health past 7 days")
            plot_scores(df)
        # Chọn ngày để truy xuất thông tin
        st.markdown("## Query for daily mental health")
        date = st.date_input("Pick Date", datetime.now().date())
        selected_date = pd.to_datetime(date)
        if not df.empty:
            filtered_df = df[df["Time"].dt.date == selected_date.date()]

            if not filtered_df.empty:
                st.write(f"Information on {selected_date.date()}:")
                for index, row in filtered_df.iterrows():
                    st.markdown(f"""
                    **Time:** {row['Time']}  
                    **Score:** {row['Score']}  
                    **Content:** {row['Content']}  
                    **Total guess:** {row['Total guess']}  
                    """)
            else:
                st.write(f"No data for {selected_date.date()}")
        st.markdown("## Detailed Information")
        st.table(df)    

if __name__ == "__main__":
    main()
