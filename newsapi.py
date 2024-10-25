from flask import Flask, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  

def recommend(liked_news, lst):
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(lst)
    tfidf_matrix2 = tfidf_vectorizer.transform(liked_news)
    cosine_similarities = cosine_similarity(tfidf_matrix2, tfidf_matrix)
    avg_cosine_similarities = np.mean(cosine_similarities, axis=0)
    top_indices = avg_cosine_similarities.argsort()[-15:][::-1]
    recommended_articles = [lst[i] for i in top_indices]
    return recommended_articles

@app.route('/recommend', methods=['POST'])
def recommend_articles():
    data = request.json
    print("dta using post"+str(data))
    liked_news = data.get('liked_news', [])

    if not liked_news:
        return jsonify({"error": "No liked news articles provided"}), 400

    # Generating recommendations
    recommendations = recommend(liked_news, lst)

    return jsonify({"recommended_articles": recommendations})

@app.route('/', methods=['GET'])
def scrape():
    global lst
    lst = []
    for i in range(2, 10):
        url = f'https://timesofindia.indiatimes.com/india/{i}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            bs4 = BeautifulSoup(response.content, 'html.parser')
            articles = bs4.find_all('span', class_="w_tle")
            for article in articles:
                anchor_tag = article.find('a')
                pg_attribute = anchor_tag.get('pg', '')
                if not pg_attribute.startswith("SEO"):
                    data_title = anchor_tag['title']
                    lst.append(data_title)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            continue
        break
    return jsonify(lst)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
