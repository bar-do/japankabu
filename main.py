import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('日本株価可視化アプリ')

st.sidebar.write("""
# 東証株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.selectbox(
    "日数",
    ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y'))

st.write(f"""
### 過去のGAFA株価
""")

@st.cache_resource
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}')
        hist.index = hist.index.strftime("%d %B %Y")
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try: 
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 5000.0, (0.0, 5000.0)
    )

    tickers = {
        'トヨタ自動車': '7203.T',
        '(株)三菱ＵＦＪフィナンシャル・グループ': '8306.T',
        '(株)日立製作所': '6501.T',
        'ソニーグループ(株)': '6758.T',
        '(株)キーエンス': '6861.T',
        '(株)リクルートホールディングス': '6098.T'
    }
    df = get_data(days, tickers)
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['トヨタ自動車', '(株)三菱ＵＦＪフィナンシャル・グループ', '(株)日立製作所', 'ソニーグループ(株)']
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価 (JSD)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(JSD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(JSD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "おっと！なにかエラーが起きているようです。"
    )