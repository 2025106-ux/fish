import streamlit as st
import json
import requests
import time
from datetime import datetime

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="포근한 수산물 도감", page_icon="🌊", layout="centered")

if "encyclopedia" not in st.session_state:
    st.session_state.encyclopedia = {}
if "current_search" not in st.session_state:
    st.session_state.current_search = None

# --- STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Pen+Script&family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    .stApp {
        background-color: #fdfaf6;
    }
    
    h1 {
        font-family: 'Nanum+Pen+Script', cursive;
        color: #4a7c59;
        font-size: 3.5rem !important;
        text-align: center;
    }

    .seafood-card {
        background: white;
        padding: 30px;
        border-radius: 25px;
        border: 2px dashed #d1e8e2;
        box-shadow: 10px 10px 0px #efefef;
        margin-bottom: 25px;
        line-height: 1.6;
    }
    
    .section-title {
        color: #c94c4c;
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 15px;
        border-bottom: 1px solid #eee;
        display: inline-block;
    }

    .badge {
        background-color: #ffecd2;
        color: #fc4a1a;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GEMINI API INTEGRATION ---
def fetch_seafood_data(query):
    """Gemini API를 사용하여 상세한 수산물 정보를 가져옵니다."""
    api_key = "" # 환경에서 자동으로 제공됨
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    system_prompt = """
    당신은 수산물 전문가이자 전문 요리사입니다. 사용자가 입력한 수산물에 대해 아주 상세하고 포근한 어조로 정보를 제공하세요.
    반드시 다음 구조의 JSON 형식으로만 응답하세요:
    {
        "name": "수산물 이름 (학명 포함)",
        "season": "가장 맛있는 구체적인 시기",
        "flavor": "맛의 특징 (식감, 풍미 등 상세히)",
        "cleaning": "손질하는 법 또는 고르는 팁",
        "cooking": ["추천 요리 1", "추천 요리 2", "요리 비법"],
        "pairing": "함께 먹으면 좋은 음식이나 술",
        "nutrition": "주요 영양소와 건강 효능",
        "warning": "섭취 시 주의사항 (알레르기, 기생충 등)",
        "story": "수산물에 얽힌 짧은 이야기나 상식"
    }
    """
    
    payload = {
        "contents": [{"parts": [{"text": f"수산물 '{query}'에 대해 상세히 설명해줘."}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"responseMimeType": "application/json"}
    }

    # Exponential Backoff Retry Logic
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return json.loads(response.json()['candidates'][0]['content']['parts'][0]['text'])
        except:
            time.sleep(delay)
    return None

# --- UI LAYOUT ---
st.title("🐚 포근한 수산물 도감")

search_query = st.text_input("궁금한 수산물 이름을 입력해 보세요", placeholder="예: 고등어, 전복, 멍게...")

if st.button("바닷속 정보 찾아보기 🔍"):
    if search_query:
        with st.spinner(f"🌊 {search_query}의 이야기를 바다에서 건져올리고 있어요..."):
            data = fetch_seafood_data(search_query)
            if data:
                st.session_state.current_search = data
            else:
                st.error("정보를 가져오는 데 실패했습니다. 잠시 후 다시 시도해 주세요.")

# Display Search Result
if st.session_state.current_search:
    res = st.session_state.current_search
    
    st.markdown(f"""
    <div class="seafood-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 style="margin:0; color:#2c3e50;">✨ {res['name']}</h2>
            <span class="badge">📅 제철: {res['season']}</span>
        </div>
        
        <p class="section-title">👅 맛의 풍경</p>
        <p>{res['flavor']}</p>
        
        <p class="section-title">🔪 전문가의 손길 (손질 & 고르기)</p>
        <p>{res['cleaning']}</p>
        
        <p class="section-title">🍳 맛있게 즐기는 법</p>
        <ul>
            {"".join([f"<li>{item}</li>" for item in res['cooking']])}
        </ul>
        <p>💡 <b>찰떡궁합:</b> {res['pairing']}</p>
        
        <div style="background:#f0f7f4; padding:15px; border-radius:15px; margin-top:15px;">
            <p style="margin:0;"><b>💪 건강 한 스푼:</b> {res['nutrition']}</p>
        </div>
        
        <p class="section-title">⚠️ 주의하세요</p>
        <p style="font-size:0.9rem; color:#666;">{res['warning']}</p>
        
        <p class="section-title">📖 바다 이야기</p>
        <p style="font-style: italic; color:#555;">"{res['story']}"</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Register Button
    if res['name'] not in st.session_state.encyclopedia:
        if st.button(f"📖 {res['name']} 도감에 등재하기"):
            st.session_state.encyclopedia[res['name']] = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "season": res['season']
            }
            st.balloons()
            st.rerun()
    else:
        st.success("✅ 이미 도감에 등재된 소중한 정보입니다.")

# --- SIDEBAR: ENCYCLOPEDIA ---
with st.sidebar:
    st.markdown("### 📜 나의 소중한 도감")
    if not st.session_state.encyclopedia:
        st.info("아직 도감이 비어있어요.\n수산물을 검색하고 지식을 채워보세요!")
    else:
        st.write(f"총 **{len(st.session_state.encyclopedia)}개**의 정보가 수집됨")
        for name, info in st.session_state.encyclopedia.items():
            with st.expander(f"🐟 {name}"):
                st.caption(f"등재일: {info['date']}")
                st.write(f"제철: {info['season']}")
        
        if st.button("도감 초기화 🗑️"):
            st.session_state.encyclopedia = {}
            st.rerun()

st.markdown("---")
st.caption("따뜻한 바다의 마음을 담아 정보를 전달합니다. 제철 수산물로 건강을 챙기세요! 🌊")
