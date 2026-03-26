from flask import Flask, render_template, request, redirect
import pickle
from database import db

app = Flask(__name__)

# DB Connection
conn = db.get_connection()
cursor = conn.cursor()

# Load ML Model
movies = pickle.load(open("models/content.pkl", "rb"))
similarity = pickle.load(open("models/similarity.pkl", "rb"))


# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    cursor.execute("SELECT * FROM content")
    data = cursor.fetchall()
    return render_template("index.html", movies=data)


# ---------------- MOVIE DETAILS ----------------
@app.route("/movie/<int:id>")
def movie(id):

    # Get selected movie
    cursor.execute("SELECT * FROM content WHERE content_id=%s", (id,))
    movie = cursor.fetchone()

    # Find index in ML dataset
    index = movies[movies["content_id"] == id].index[0]

    distances = similarity[index]

    movie_list = sorted(list(enumerate(distances)),
                        reverse=True,
                        key=lambda x: x[1])[1:6]

    recommendations = []

    for i in movie_list:
        rec_id = int(movies.iloc[i[0]].content_id)

        cursor.execute("SELECT * FROM content WHERE content_id=%s", (rec_id,))
        rec_movie = cursor.fetchone()

        if rec_movie:
            recommendations.append(rec_movie)

    return render_template("movie.html",
                           movie=movie,
                           rec=recommendations)


# ---------------- LIKE CONTENT ----------------
@app.route("/like/<int:id>", methods=["POST"])
def like(id):

    userid = 1   # later replace with session user

    # Prevent duplicate likes
    cursor.execute(
        "SELECT * FROM likes WHERE user_id=%s AND content_id=%s",
        (userid, id)
    )
    already = cursor.fetchone()

    if not already:
        cursor.execute(
            "INSERT INTO likes(content_id, user_id) VALUES(%s, %s)",
            (id, userid)
        )
        conn.commit()

    return redirect(f"/recommend/{userid}")


# ---------------- PERSONALIZED RECOMMENDATION ----------------
@app.route("/recommend/<int:userid>")
def recommend_user(userid):

    # Step 1: Get liked content
    cursor.execute("SELECT content_id FROM likes WHERE user_id=%s", (userid,))
    liked = cursor.fetchall()

    liked_ids = [x["content_id"] for x in liked]

    all_recommendations = []

    # Step 2: Get similar content for each liked item
    for cid in liked_ids:

        index = movies[movies["content_id"] == cid].index[0]

        distances = similarity[index]

        movie_list = sorted(list(enumerate(distances)),
                            reverse=True,
                            key=lambda x: x[1])[1:6]

        for i in movie_list:
            rec_id = int(movies.iloc[i[0]].content_id)
            all_recommendations.append(rec_id)

    # Step 3: Remove duplicates & already liked
    final_ids = list(set(all_recommendations) - set(liked_ids))

    recommendations = []

    # Step 4: Fetch data from DB
    for rid in final_ids[:10]:
        cursor.execute("SELECT * FROM content WHERE content_id=%s", (rid,))
        rec_movie = cursor.fetchone()

        if rec_movie:
            recommendations.append(rec_movie)

    return render_template("recommend.html", rec=recommendations)


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
