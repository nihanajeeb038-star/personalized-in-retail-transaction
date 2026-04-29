import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------ DATA ------------------
data = {
    'item': [
        'T-Shirt','Jeans','Jacket','Sneakers',
        'Laptop','Smartphone','Headphones',
        'Watch','Backpack','Sunglasses'
    ],
    'category': [
        'clothing','clothing','clothing','footwear',
        'electronics','electronics','electronics',
        'accessory','accessory','accessory'
    ],
    'tags': [
        'clothing casual cotton fashion',
        'clothing denim casual fashion',
        'clothing winter fashion warm',
        'footwear casual sports fashion',
        'electronics computer work tech',
        'electronics mobile communication tech',
        'electronics audio music tech',
        'accessory fashion wearable time',
        'accessory bag travel fashion',
        'accessory fashion summer style'
    ],
    'price': [500,1200,2500,2000,60000,30000,2500,1500,1800,800],
    'rating': [4.2,4.5,4.3,4.4,4.8,4.7,4.3,4.2,4.1,4.0]
}

df = pd.DataFrame(data)

# ------------------ RECOMMENDATION ------------------
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['tags'])
similarity = cosine_similarity(tfidf_matrix)

def recommend(item):
    idx = df[df['item'] == item].index[0]
    selected_category = df.iloc[idx]['category']

    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:]

    # ✅ Filter by similarity + category
    filtered = [
        (i, score) for i, score in scores
        if score > 0.2 and df.iloc[i]['category'] == selected_category
    ]

    return [(df.iloc[i], score) for i, score in filtered[:5]]

# ------------------ UI ------------------
st.set_page_config(page_title="Retail Dashboard", layout="wide")

# Title
st.markdown(
    "<h1 style='text-align:center; color:#6a11cb;'>🛒 Smart Retail Recommendation</h1>",
    unsafe_allow_html=True
)

# Dropdown
item = st.selectbox("Select a Product", df['item'])

# Button
if st.button("Show Similar Products"):

    st.markdown(f"### 🛍️ Similar Products for **{item}**")

    results = recommend(item)

    if not results:
        st.warning("No strong recommendations found.")
    else:
        cols = st.columns(len(results))

        for i, (row, score) in enumerate(results):
            with cols[i]:
                st.markdown(f"""
                <div style="
                    padding:20px;
                    border-radius:12px;
                    background: linear-gradient(135deg, #1e1e2f, #2a2a40);
                    box-shadow:0 4px 15px rgba(0,0,0,0.4);
                    text-align:center;
                    color:white;
                ">
                    <h3>{row['item']}</h3>
                    <p style="color:#dddddd;">💲 ₹{row['price']}</p>
                    <p style="color:#dddddd;">⭐ {row['rating']}</p>
                    <p style="color:#00ff9c;"><b>Match: {round(score,2)}</b></p>
                </div>
                """, unsafe_allow_html=True)
