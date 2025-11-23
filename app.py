# Movie Recommender App — Dark Mode (Neon Blue Glow)
# Drop your artifacts (movies.pkl, vectorizer.joblib, similarity.joblib) in the same folder or artifacts/.
# Optional: set TMDB API key in env var OMDB_API_KEY or Streamlit secrets under [TMDB].

import os
import streamlit as st
import pandas as pd
import joblib
import requests
from difflib import get_close_matches

# -----------------------------
# Config + Page
# -----------------------------
st.set_page_config(page_title="Neon Movie Recommender", layout="wide", initial_sidebar_state="expanded")

# custom CSS for neon dark theme
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"]  {font-family: Inter, sans-serif; background: #03040a; color: #cce7ff;}
    .neon-card {background: linear-gradient(135deg, rgba(6,18,36,0.6), rgba(2,6,23,0.6)); border-radius: 14px; padding: 12px; box-shadow: 0 6px 30px rgba(0,140,255,0.08), 0 0 18px rgba(0,140,255,0.06) inset; border: 1px solid rgba(0,140,255,0.18);} 
    .neon-title {color: #9be6ff; font-weight:800; font-size:26px}
    .neon-sub {color: #bfeeff; opacity:0.9}
    .poster {border-radius: 8px; box-shadow: 0 10px 30px rgba(0,140,255,0.12);} 
    .hint {color:#7fb9d9; font-size:13px}
    .pill {background: rgba(0,140,255,0.12); padding:6px 10px; border-radius:999px; color:#bfeeff; font-weight:600}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div style="display:flex;align-items:center;gap:18px"><div class="neon-title">⚡ Neon Movie Recommender</div><div class="neon-sub">AI vibes • Dark mode • Neon blue</div></div>', unsafe_allow_html=True)
st.markdown('<div class="hint">Tip: use the search box or pick from the dropdown. If posters are missing, add a TMDB API key in env or secrets.</div>', unsafe_allow_html=True)
st.write('')

# -----------------------------
# Load Artifacts (cached)
# -----------------------------
@st.cache_resource
def load_artifacts():
    # try in artifacts/ first
    movies_path = 'artifacts/movies.pkl' if os.path.exists('artifacts/movies.pkl') else 'movies.pkl'
    vec_path = 'vectorizer.joblib'
    sim_path = 'artifacts/similarity.joblib' if os.path.exists('artifacts/similarity.joblib') else 'similarity.joblib'

    movies = pd.read_pickle(movies_path)
    vectorizer = joblib.load(vec_path)
    similarity = joblib.load(sim_path)

    # ensure a title column exists and is string
    movies['title'] = movies['title'].astype(str)
    return movies, vectorizer, similarity

movies, vectorizer, similarity = load_artifacts()

# -----------------------------
# Poster helper (TMDB)
# -----------------------------
OMDB_API_KEY = "7fbc8cb0"

@st.cache_resource
def get_poster_url(title):
    if not OMDB_API_KEY:
        return None

    params = {
        "apikey": OMDB_API_KEY,
        "t": title
    }

    try:
        res = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
        data = res.json()

        poster = data.get("Poster")
        if poster and poster != "N/A":
            return poster
        
        return None
    except Exception as e:
        return None

# -----------------------------
# Recommend function with fuzzy fallback
# -----------------------------

def recommend(movie_title, topn=5):
    title = str(movie_title).strip()
    df = movies

    # exact match first (case-insensitive)
    mask = df['title'].str.lower() == title.lower()
    matches = df[mask]

    # contains match
    if matches.empty:
        mask = df['title'].str.lower().str.contains(title.lower(), na=False)
        matches = df[mask]

    # fuzzy fallback using difflib
    if matches.empty:
        choices = df['title'].values.tolist()
        close = get_close_matches(title, choices, n=1, cutoff=0.6)
        if close:
            matches = df[df['title'] == close[0]]

    if matches.empty:
        return []

    idx = matches.index[0]
    distances = similarity[idx]
    scored = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:topn+1]

    recs = []
    for i, score in scored:
        recs.append({'title': df.iloc[i]['title'], 'score': float(score)})
    return recs

# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.markdown('### 🔎 Search or pick')
    query = st.text_input('Type movie name (fuzzy search ok)', '')
    topn = st.slider('Number of recommendations', 3, 10, 5)
    st.markdown('---')
    st.markdown('### ⚙️ App Controls')
    if OMDB_API_KEY:
        st.markdown('<div class="pill">TMDB Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pill">TMDB not connected</div>', unsafe_allow_html=True)
    st.caption('Add TMDB API key to streamlit secrets or environment variable OMDB_API_KEY')

# Main selection
col1, col2 = st.columns([3,1])
with col2:
    movie_name = st.selectbox('Choose from titles', movies['title'].values, index=0)
    if query:
        movie_name = query

with col1:
    st.markdown('<div class="neon-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between"><div style="font-weight:700;color:#9be6ff">Selected: {movie_name}</div><div style="color:#7fb9d9">AI-vibe mode</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Recommend button
if st.button('Generate Recommendations ⚡'):
    with st.spinner('Thinking like an AI...'):
        results = recommend(movie_name, topn=topn)

    if not results:
        st.error('No match found. Try different spelling or pick from dropdown.')
    else:
        # display in horizontal cards
        cols = st.columns(len(results))
        for c, item in zip(cols, results):
            title = item['title']
            # score = item['score']
            poster = get_poster_url(title)

            with c:
                st.markdown('<div class="neon-card">', unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_container_width=True, caption=title, output_format='auto')
                else:
                    # fallback poster: small title card
                    st.markdown(f"<div style='height:260px;display:flex;align-items:center;justify-content:center;border-radius:8px;background:#04122a'><div style='text-align:center;font-weight:700;color:#9be6ff'>{title}</div></div>", unsafe_allow_html=True)

                st.markdown(f"<div style='margin-top:8px;font-weight:700;color:#bfeeff'>{title}</div>", unsafe_allow_html=True)
                # st.markdown(f"<div style='color:#86c7e6;font-size:13px'>Similarity score: {score:.3f}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('---')
st.markdown('<div style="text-align:center;color:#7fb9d9">Made with ❤️ — Neon recommender • Ask me to dockerize or HF-space this.</div>', unsafe_allow_html=True)
