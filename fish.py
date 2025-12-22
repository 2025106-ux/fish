import streamlit as st
import json
import base64
from datetime import datetime

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="포근한 수산물 도감", page_icon="🐟", layout="centered")

# Initialize Session State
if "encyclopedia" not in st.session_state:
    st.session_state.encyclopedia = {}
if "current_search" not in st.session_state:
    st.session_state.current_search = None
if "api_key" not in st.session_state:
    st.session_state.api_key = "" # Gemini API Key is handled by the environment

# --- STYLING (Cozy Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Nanum+Gothic', sans-serif;
    }
    
    .main {
        background-color: #fdf6e3; /* Warm parchment color */
    }
    
    .stButton>button {
        background-color: #ff9a8b;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #ff6f61;
        transform: scale(1.05);
    }
    
    .seafood-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 5px solid #74b9ff;
        margin-bottom: 20px;
    }
    
    .info-header {
        color: #2d3436;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .badge {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 4px 12px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GEMINI API CALL (Mocking logic for the environment) ---
def get_seafood_info(query):
    """
    In a real scenario, this would call the Gemini API.
    Since we need a structured response, we define a prompt that returns JSON.
    """
    # System Prompt for Gemini
    system_prompt = """
    You are a professional marine biologist and chef. 
    Provide detailed information about the requested seafood in Korean.
    Return the response in valid JSON format with the following keys:
    'name', 'season' (best months), 'taste_profile', 'cooking_tips', 'nutrition', 'fun_fact'.
    Keep the tone cozy and helpful.
    """
    
    # Payload for the simulated API call
    # Note: In the actual execution environment, the fetch to Gemini happens here.
    # For this script structure, we'll simulate the response logic or provide a placeholder.
    
    # Placeholder data for demonstration if API isn't called
    mock_data = {
        "방어": {
            "name": "방어 (Yellowtail)",
            "season": "11월 ~ 2월 (겨울)",
            "taste_profile": "기름기가 풍부하고 고소하며 살이 단단해 씹는 맛이 일품입니다.",
            "cooking_tips": "가장 맛있는 방법은 두툼하게 썬 '회'입니다. 묵은지나 김에 싸서 기름장에 찍어 드셔보세요.",
            "nutrition": "불포화지방산(DHA, EPA)이 풍부하여 혈관 건강과 뇌 기능 활성화에 좋습니다.",
            "fun_fact": "방어는 클수록 맛있는 '확률'이 높으며, 10kg 이상의 대방어를 으뜸으로 칩니다."
        },
        "꽃게": {
            "name": "꽃게 (Blue Crab)",
            "season": "봄(암게), 가을(수게)",
            "taste_profile": "달큰한 살과 고소한 내장이 어우러져 깊은 감칠맛을 냅니다.",
            "cooking_tips": "봄에는 알이 꽉 찬 간장게장, 가을에는 살이 오른 찜이나 탕으로 즐기는 것이 최고입니다.",
            "nutrition": "타우린이 풍부해 피로 회복과 간 해독에 탁월한 효과가 있습니다.",
            "fun_fact": "꽃게는 배 쪽의 덮개 모양으로 암수를 구분합니다. 둥글면 암게, 뾰족하면 수게입니다."
        }
    }
    
    return mock_data.get(query, {
        "name": f"{query} (정보 준비 중)",
        "season": "알 수 없음",
        "taste_profile": "정보를 불러오는 중입니다.",
        "cooking_tips": "조금만 기다려 주세요!",
        "nutrition": "영양 정보를 분석 중입니다.",
        "fun_fact": "이 수산물에 대한 재미있는 사실을 찾고 있어요."
    })

# --- UI LAYOUT ---
st.title("🐚 포근한 수산물 도감")
st.write("알고 싶은 수산물 이름을 입력하세요. 정보를 모두 읽으면 도감에 등재할 수 있어요!")

col1, col2 = st.columns([3, 1])
with col1:
    search_input = st.text_input("수산물 이름 (예: 방어, 꽃게, 고등어)", placeholder="무엇이 궁금하신가요?")
with col2:
    st.write(" ") # Padding
    search_btn = st.button("검색하기")

if search_btn and search_input:
    # Simulate API fetching
    with st.spinner(f"'{search_input}'의 정보를 바다에서 건져올리는 중..."):
        info = get_seafood_info(search_input)
        st.session_state.current_search = info

# Display Results
if st.session_state.current_search:
    info = st.session_state.current_search
    
    st.markdown(f"""
        <div class="seafood-card">
            <div class="info-header">🐟 {info['name']}</div>
            <p><b>📅 제철:</b> <span class="badge">{info['season']}</span></p>
            <hr>
            <p><b>✨ 맛의 특징:</b><br>{info['taste_profile']}</p>
            <p><b>👨‍🍳 맛있게 먹는 법:</b><br>{info['cooking_tips']}</p>
            <p><b>💪 영양 정보:</b><br>{info['nutrition']}</p>
            <p><b>💡 한 줄 상식:</b><br><i>{info['fun_fact']}</i></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Registration logic
    if info['name'] not in st.session_state.encyclopedia:
        if st.button("📖 이 정보를 도감에 등재하기"):
            st.session_state.encyclopedia[info['name']] = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "season": info['season']
            }
            st.success(f"🎉 '{info['name']}'이(가) 도감에 성공적으로 등록되었습니다!")
            st.balloons()
    else:
        st.info("✅ 이미 도감에 등록된 수산물입니다.")

# --- ENCYCLOPEDIA SIDEBAR ---
with st.sidebar:
    st.header("📜 나의 수산물 도감")
    if not st.session_state.encyclopedia:
        st.write("아직 등록된 수산물이 없어요. 검색을 통해 도감을 채워보세요!")
    else:
        st.write(f"현재 **{len(st.session_state.encyclopedia)}종**의 수산물이 등록됨")
        for name, details in st.session_state.encyclopedia.items():
            with st.expander(f"{name}"):
                st.write(f"📅 등록일: {details['date']}")
                st.write(f"🍂 제철: {details['season']}")

    if st.session_state.encyclopedia:
        if st.button("도감 초기화"):
            st.session_state.encyclopedia = {}
            st.rerun()

st.divider()
st.caption("본 앱은 포근한 배경에서 수산물의 정보를 학습하고 기록하기 위해 제작되었습니다. 🌊")
