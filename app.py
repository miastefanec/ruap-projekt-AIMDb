from operator import pos
from os import environ
from flask import Flask , render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import urllib
import urllib.request as urlrequest
import json

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql://qvutdjklfelrgc:9be0a435bb0ae05135cbb9b6307103e381ab282e944de7dade48cc4e04f73798@ec2-52-2-118-38.compute-1.amazonaws.com:5432/d3aucjtkjokd27'

db = SQLAlchemy(app)

class Review(db.Model):
    __tablename__ = "review"

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    movie = db.Column(db.String(100), nullable=False)
    review = db.Column(db.String(10000), nullable=False)
    sentiment = db.Column(db.String(10), nullable=False)
    probability = db.Column(db.String(10), nullable=False)
    
    def __init__(self, name, movie, review, sentiment, probability):
        self.name = name
        self.movie = movie
        self.review = review
        self.sentiment = sentiment
        self.probability = probability

@app.route("/")
def home():
    return redirect(url_for('index'))


@app.route("/index", methods = ["GET", "POST"])
def index():
    if request.method == 'POST': 
        data = request.form 
        name = data["name"]
        review = data["review"]
        movie = data["movie"]
        sentiment = None
        probability = None

        data = { 
            "Inputs": {
                "input1":
                {
                    "ColumnNames": ["review", "sentiment"],
                    "Values": [ [ review, "positive" ] ]
                },        
            },
            "GlobalParameters": {
            }
        }

        body = str.encode(json.dumps(data))

        url = 'https://ussouthcentral.services.azureml.net/workspaces/ffa2c4d70c674d649a8b986af42c6930/services/669d74ed59ef483da6a15d864661ca89/execute?api-version=2.0&details=true'
        api_key = '+Puh5B7R/secvB4xEs8N9U4Ua03e0ZGfyRyRxdoIVnOiwKbZQMrFxfZzpgGFD9Q0aC/sr3Oq0mL1eEEMJocc7Q==' # Replace this with the API key for the web service
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

        req = urlrequest.Request(url, body, headers) 

        try:
            response = urlrequest.urlopen(req)

            result = json.loads(response.read())
            sentiment = result['Results']['output1']['value']['Values'][0][0]
            probability = float(result['Results']['output1']['value']['Values'][0][1])
            if(probability < 0.5):
                probability = 1 - probability
            probability = str("{:.2f}".format(probability * 100)) + "%"
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            print(error.info())

            print(json.loads(error.read()))         

        new_data = Review(name, movie, review, sentiment, probability)
        db.session.add(new_data)
        db.session.commit()       

        return render_template("index.html", sentiment = sentiment, probability = probability)

    return render_template("index.html")

@app.route('/reviews', methods = ["GET", "POST"])
def reviews():
    review_data = Review.query.all()
    positive = Review.query.filter_by(sentiment="positive").count()
    negative = Review.query.filter_by(sentiment="negative").count()
    if request.method == "POST":
        data = request.form
        if "showAll" not in data:
            if data["filter"] == "author":
                review_data = Review.query.filter(Review.name.ilike(data["term"])).order_by(data["sort"])
            else:
                review_data = Review.query.filter(Review.movie.ilike(data["term"])).order_by(data["sort"])
            positive = review_data.filter_by(sentiment="positive").count()
            negative = review_data.filter_by(sentiment="negative").count()
        else:
            review_data = Review.query.order_by(data["sort"]).all()
    return render_template('reviews.html', review_data = review_data, positive = positive, negative = negative)
    

if __name__=="__main__":
    db.create_all()
    app.run(debug=True)