import streamlit as st
import base64
import os
import requests
from io import BytesIO

# --- 音声読み上げ（Text-to-Speech）関数の定義 ---
# ここでは、gTTSライブラリ（Google Text-to-Speech）を簡易的にシミュレートするため、
# あらかじめ生成したMP3ファイルをbase64で埋め込む、または外部APIを使う形式にする。
# 初回起動時は「gTTS」と「Base64」を使った最もシンプルな方法が動かしやすい。

def text_to_speech(text, lang='ja'):
    # 本来は gTTS(text=text, lang=lang).save("speech.mp3") とする。
    # ここではStreamlitの要件上、base64エンコードされたMP3データを埋め込む。
    
    # --- 重要: プロトタイプ用の音声埋め込み ---
    # もし「gTTS」を使える環境なら、以下をコメント解除して使う：
    # from gtts import gTTS
    # tts = gTTS(text=text, lang=lang)
    # tts.save("speech.mp3")
    # with open("speech.mp3", "rb") as f:
    #     data = f.read()
    # base64_audio = base64.b64encode(data).decode()
    # os.remove("speech.mp3") # ファイルを削除
    
    # --- 簡易実装（もしgTTSがうまく動かない場合、または今すぐ動かしたい場合） ---
    # ここにbase64データを直接貼ることもできる。今回はbase64を生成する。
    # (注意: この簡易実装では、実際にはgTTSに接続しない)
    
    # 実際にはgTTS APIを叩く：
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang)
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
        base64_audio = base64.b64encode(data).decode()
        os.remove("speech.mp3") # ファイルを削除
        
    except ImportError:
        # gTTSがない場合は、無音を再生する仮のbase64を返す（エラー防止）
        print("Error: gTTS is not installed. Falling back to dummy sound.")
        base64_audio = "T3BlbkNDQQ" # Dummy minimal Base64 file string for testing

    return base64_audio

# --- メインウィンドウの設定 ---
st.set_page_config(page_title="Study Buddy - 学習習慣化サポート相棒", page_icon="🤖", layout="wide")

# 全体を左右に分ける（ロボットエリア vs ダッシュボードエリア）
col_left, col_right = st.columns([1, 1], gap="large")

# --- 左側：ロボット・メッセージエリア ---
with col_left:
    st.caption("🔊 音声生成中...")
    st.subheader("ロボットエージェント「スマート・バディ」")
    
    # --- 重要: ロボットの顔画像（笑顔）を埋め込む ---
    # 先ほどの画像生成結果（笑顔）をロボットの顔として使う。
    # ここでは、画像ファイルを埋め込む（画像ファイルを保存して st.image とする）。
    # もし画像がまだない場合は、URLを指定する（今回は画像URLを埋め込むと仮定）
    
    # プロトタイプ用の笑顔画像URL（先ほどの画像と異なる、笑顔の仮画像を指定）
    ROBOT_FACE_URL = "https://i.imgur.com/vH9XgGf.png" # 簡易画像：笑顔
    # (注意: このURLは簡易画像です。もし先ほどの画像があるなら st.image("robot_smile.png") としてください)
    
    # ロボットの顔画像を表示（中央寄せ）
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        st.image(ROBOT_FACE_URL, width=300, caption="Study Buddy")

    # --- メッセージ欄（ナッジテキスト） ---
    nudge_text = "「まずは5分だけ教科書を開いてみよう！最初の1問だけでいいよ！」"
    
    st.text_area(label="Study Buddy からの言葉", value=nudge_text, height=100)

    # --- 音声再生ボタンの機能実装 ---
    if st.button("🔊 音声を再生"):
        with st.spinner("音声を生成・読み込み中..."):
            audio_base64 = text_to_speech(nudge_text)
            
            if audio_base64:
                # Streamlitのオーディオプレイヤー（base64埋め込み）を使って再生
                audio_html = f'<audio autoplay="True" src="data:audio/mp3;base64,{audio_base64}" />'
                st.markdown(audio_html, unsafe_allow_html=True)
                st.success("音声を再生しました。")
            else:
                st.error("音声の生成に失敗しました。gTTSライブラリを確認してください。")

# --- 右側：ダッシュボードエリア（可視化） ---
with col_right:
    st.caption("ダッシュボードエリア")
    st.subheader("📊 本日の集中力推移（フリーズ検知時間）")
    
    # 仮のデータを作成してグラフにする
    import pandas as pd
    import numpy as np

    data = pd.DataFrame({
        "時間帯": ["10m", "20m", "30m", "40m"],
        "集中度 (%)": [100, 95, 55, 10], # 集中力低下タイマー作動時を表現
        "状態": ["集中", "集中", "フリーズ検知", "スマホ逃避"] # ラベル
    })

    # 棒グラフを表示（オレンジ・赤の部分を強調）
    import plotly.express as px
    fig = px.bar(data, x="時間帯", y="集中度 (%)", color="状態",
                 color_discrete_map={"集中": "#0071E3", "フリーズ検知": "#FF9F40", "スマホ逃避": "#FF3B30"},
                 title="開始からの集中度の推移")
    st.plotly_chart(fig, use_container_size=True)

    # --- スマートフォン逃避タイマーとログ ---
    st.divider()
    st.subheader("⏱️ スマートフォン逃避タイマー")
    col_log1, col_log2 = st.columns([1, 1])
    
    with col_log1:
        st.metric(label="着席から逃避までの平均時間", value="35分", delta="-10分 (昨日比)", help="あなたの集中が切れやすい時間です")
        st.warning("⚠️ 35分経過：スマホ逃避を検知しました。")
    
    with col_log2:
        st.caption("検知ログ履歴")
        st.write("- 21:05 学習開始（ナッジ成功）")
        st.write("- 21:35 集中力低下（スマホ逃避）")
        st.write("- 21:40 フリーズ検知 ➔ 休憩提案")
