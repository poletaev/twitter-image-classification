from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound
from flask_googlemaps import Map

from models import Tweets

google_map = Blueprint('google_map', __name__, template_folder='templates')

def split_tweets(tweets_list):
    coordinates = map(lambda x: (x.latitude, x.longitude), tweets_list)
    #text = map(lambda x: x.text, tweets_list)
    photo = map(lambda x: u"<img src='{}' style='width:200px;height:200px;'>".format(x.photo_url),
                tweets_list)
    classes = map(lambda x: x.classes, tweets_list)
    photo_with_classes = map(lambda x, y:  x + u' ' + y,
                             photo, classes)
    return coordinates, classes, photo, photo_with_classes


@google_map.route("/")
def mapview():

    t = current_app.db_session.query(Tweets).limit(100).all()
    coordinates, _, _, photo_with_classes = split_tweets(t)
    sndmap = Map(
        identifier="sndmap",
        lat=54.59,
        lng=73.22,
        style="height:100%; width:100%; top:0; left:0; position:absolute; z-index:200;",
        zoom=2,
        maptype="TERRAIN",  # "ROADMAP", "SATELLITE", "HYBRID", "TERRAIN"
        infobox=photo_with_classes,
        markers={'http://maps.google.com/mapfiles/ms/icons/blue-dot.png':
                 coordinates}
    )

    try:
        return render_template('google_map.html', sndmap=sndmap)
    except TemplateNotFound:
        abort(404)

