#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate
from datetime import datetime  # FIX: Imported datetime to handle database types

from models import db, Article, User, ArticleSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# =====================================================================
# GUARANTEED SEEDING ON LAUNCH
# =====================================================================
with app.app_context():
    db.create_all()
    if not Article.query.first():
        for i in range(1, 5):
            db.session.add(Article(
                id=i,
                author="Test Author",
                title=f"Test Title {i}",
                content="This is the full length body content of the article.",
                preview="This is the full...",
                minutes_to_read=5,
                date=datetime.now()  # FIX: Using actual datetime object instead of string
            ))
        db.session.commit()

# =====================================================================
# ROUTES
# =====================================================================

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles')
def index_articles():
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return make_response(articles)

@app.route('/articles/<int:id>')
def show_article(id):
    if not session.get('page_views'):
        session['page_views'] = 0
    session['page_views'] += 1

    if session['page_views'] > 3:
        return make_response(
            jsonify({'message': 'Maximum pageview limit reached'}), 
            401
        )

    article = Article.query.filter(Article.id == id).first()
    if not article:
        return make_response(jsonify({'message': 'Article not found'}), 404)

    article_json = ArticleSchema().dump(article)
    return make_response(jsonify(article_json), 200)


if __name__ == '__main__':
    app.run(port=5555)

