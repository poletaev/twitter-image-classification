from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound
from flask_googlemaps import Map

from models import Tweets

google_map = Blueprint('google_map', __name__, template_folder='templates')

def split_tweets(tweets_list):
    coordinates = map(lambda x: (x.latitude, x.longitude), tweets_list)
    text = map(lambda x: x.text, tweets_list)
    photo = map(lambda x: x.photo_url, tweets_list)
    tweet = map(lambda x, y:
                u"<img src='{}' style='width:128px;height:128px;'>"
                u"<p>{}</p>"
                u"<ul>"
                u"<li>Coffee</li>"
                u"<li>Tea</li>"
                u"<li>Milk</li>"
                u"</ul>"
                .format(x, y),
                photo, text)
    return coordinates, tweet, photo, text

@google_map.route("/")
def mapview():

    t = current_app.db_session.query(Tweets).limit(10).all()
    coordinates, text, photo, src_txt = split_tweets(t)
    sndmap = Map(
        identifier="sndmap",
        lat=54.59,
        lng=73.22,
        style="height:100%; width:100%; top:0; left:0; position:absolute; z-index:200;",
        zoom=2,
        maptype="TERRAIN",  # "ROADMAP", "SATELLITE", "HYBRID", "TERRAIN"
        infobox=text,  # photo,
        markers={'http://maps.google.com/mapfiles/ms/icons/blue-dot.png':
                 coordinates}
    )

    try:
        return render_template('google_map.html', sndmap=sndmap)
    except TemplateNotFound:
        abort(404)

