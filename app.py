import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import requests

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Movie Engine")

# --- CSS: Dizayn ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jockey+One&display=swap');

    .stApp { 
        background: linear-gradient(180deg, #000000 0%, #050A15 40%, #0A192F 100%);
        background-attachment: fixed;
        color: #E9C46A; 
    }
    
    [data-testid="stSidebar"] { display: none !important; }

    h1 { 
        font-family: 'Jockey One', sans-serif !important; 
        text-align: center; 
        color: #E9C46A !important; 
        font-size: 90px !important; 
        text-transform: uppercase;
        margin-bottom: 5px;
        letter-spacing: 3px;
    }

    .stMultiSelect div[role="listbox"] {
        font-size: 20px !important;
        font-family: 'Jockey One', sans-serif !important;
    }
    
    label[data-testid="stWidgetLabel"] p {
        font-size: 25px !important; 
        font-family: 'Jockey One', sans-serif !important;
        color: #E9C46A !important;
    }

    .main-submit-container {
        display: flex; justify-content: center; margin: 30px 0;
    }
    
    div.stButton > button[kind="primary"] {
        background-color: #C41E3A !important;
        color: white !important;
        font-family: 'Jockey One', sans-serif !important;
        font-size: 35px !important;
        padding: 15px 100px !important;
        border: 2px solid #E9C46A !important;
        border-radius: 0px !important;
        text-transform: uppercase;
    }

    .img-container {
        position: relative;
        line-height: 0;
        border: 1px solid rgba(233, 196, 106, 0.2);
        transition: transform 0.2s;
    }
    
    .img-container:hover { transform: scale(1.02); }

    .stButton.poster-click-area > button {
        position: absolute !important; top: 0 !important; left: 0 !important;
        width: 100% !important; height: 100% !important;
        background: transparent !important; border: none !important;
        color: transparent !important; z-index: 100 !important;
    }

    .selected-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(196, 30, 58, 0.4);
        border: 4px solid #C41E3A;
        pointer-events: none; z-index: 50;
    }
    
    .check-mark {
        position: absolute; bottom: 15px; left: 15px;
        background: #C41E3A; color: white;
        padding: 5px 12px; font-family: 'Jockey One', sans-serif;
        font-size: 18px; z-index: 60;
    }

    .movie-card-title {
        font-family: 'Jockey One', sans-serif !important;
        font-size: 24px !important; text-align: center;
        text-transform: uppercase; margin-top: 15px;
        color: #E9C46A !important; min-height: 65px;
    }

    .precision-text {
        font-family: 'Jockey One', sans-serif; color: #E9C46A;
        text-align: center; font-size: 22px; margin-top: 50px;
        padding: 20px; text-transform: uppercase;
        border-top: 1px solid rgba(233, 196, 106, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    movies = pd.read_csv("https://raw.githubusercontent.com/somustafa/movierecc/main/movies.csv")
    ratings = pd.read_csv("https://raw.githubusercontent.com/somustafa/movierecc/main/ratings.csv")
    movies['clean_title'] = movies['title'].str.replace(r'\(\d{4}\)', '', regex=True).str.strip()
    pop_ids = ratings.groupby("movieId").size()[lambda x: x >= 50].index
    movies = movies[movies.movieId.isin(pop_ids)].copy().reset_index(drop=True)
    collab_matrix = ratings[ratings.movieId.isin(pop_ids)].pivot(index='movieId', columns='userId', values='rating').fillna(0)
    return movies, collab_matrix

movies_df, collab_matrix = load_data()

@st.cache_data(show_spinner=False)
def get_poster_cached(title):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        res = requests.get(url, params={"api_key": "6488d38d72a69bcb051a50e054006e51", "query": title}, timeout=1).json()
        if res["results"]: return f"https://image.tmdb.org/t/p/w300{res['results'][0]['poster_path']}"
    except: pass
    return "https://via.placeholder.com/300x450/000/C41E3A?text=FILM"

# --- Session States ---
if 'selected_ids' not in st.session_state: st.session_state.selected_ids = set()
if 'main_pool' not in st.session_state: st.session_state.main_pool = movies_df.sample(20)
if 'page' not in st.session_state: st.session_state.page = "home"

# --- HOME PAGE ---
if st.session_state.page == "home":
    st.markdown("<h1>MOVIE ENGINE</h1>", unsafe_allow_html=True)
    
    search_selection = st.multiselect("SEARCH FILMS:", options=movies_df['clean_title'].unique())
    for t in search_selection:
        m_id = movies_df[movies_df.clean_title == t]['movieId'].values[0]
        st.session_state.selected_ids.add(m_id)

    st.markdown('<div class="main-submit-container">', unsafe_allow_html=True)
    if st.button(f"SUBMIT ({len(st.session_state.selected_ids)})", key="center_run", type="primary"):
        if st.session_state.selected_ids:
            st.session_state.page = "results"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    cols = st.columns(5)
    for i, (idx, row) in enumerate(st.session_state.main_pool.iterrows()):
        m_id = row['movieId']
        with cols[i % 5]:
            is_sel = m_id in st.session_state.selected_ids
            st.markdown('<div class="img-container">', unsafe_allow_html=True)
            if is_sel:
                st.markdown('<div class="selected-overlay"></div><div class="check-mark">SELECTED</div>', unsafe_allow_html=True)
            st.image(get_poster_cached(row['clean_title']), use_container_width=True)
            st.markdown('<div class="poster-click-area">', unsafe_allow_html=True)
            if st.button("", key=f"p_{m_id}"):
                if m_id in st.session_state.selected_ids: st.session_state.selected_ids.remove(m_id)
                else: st.session_state.selected_ids.add(m_id)
                st.rerun()
            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown(f"<div class='movie-card-title'>{row['clean_title']}</div>", unsafe_allow_html=True)

# --- RESULTS PAGE ---
else:
    st.markdown("<h1>RECOMMENDATIONS</h1>", unsafe_allow_html=True)
    
    knn = NearestNeighbors(metric='cosine', algorithm='brute').fit(collab_matrix.values)
    scores = np.zeros(len(movies_df))
    
    # KNN ilə oxşarları tap
    for m_id in st.session_state.selected_ids:
        if m_id in collab_matrix.index:
            idx = collab_matrix.index.get_loc(m_id)
            _, ind = knn.kneighbors(collab_matrix.iloc[idx, :].values.reshape(1, -1), n_neighbors=40)
            for i in ind[0]:
                midx = movies_df.index[movies_df.movieId == collab_matrix.index[i]].tolist()
                if midx: scores[midx[0]] += 1
    
    # --- FILTR: Seçilmiş filmləri nəticələrdən silirik ---
    for m_id in st.session_state.selected_ids:
        midx = movies_df.index[movies_df.movieId == m_id].tolist()
        if midx: scores[midx[0]] = 0 
    
    recs = movies_df.iloc[scores.argsort()[-10:][::-1]]
    
    if st.button("⬅ BACK", key="back", type="primary"):
        st.session_state.page = "home"
        st.rerun()

    st.write("---")
    r_cols = st.columns(5)
    for j, (idx, row) in enumerate(recs.iterrows()):
        with r_cols[j % 5]:
            st.image(get_poster_cached(row['clean_title']), use_container_width=True)
            st.markdown(f"<div class='movie-card-title'>{row['clean_title']}</div>", unsafe_allow_html=True)

    # Precision Score (Genre Match)
    user_movie_data = movies_df[movies_df.movieId.isin(st.session_state.selected_ids)]
    user_genres_list = "|".join(user_movie_data['genres']).split("|")
    unique_user_genres = set(user_genres_list)
    hits = sum(1 for g_str in recs['genres'] if unique_user_genres.intersection(set(g_str.split("|"))))
    
    st.markdown(f"<div class='precision-text'>PRECISION SCORE: {(hits/10)*100:.0f}%</div>", unsafe_allow_html=True) 