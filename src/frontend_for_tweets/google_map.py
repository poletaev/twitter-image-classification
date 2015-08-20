from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask_googlemaps import Map

google_map = Blueprint('google_map', __name__, template_folder='templates')

@google_map.route("/4maps")
def four_mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers={'http://maps.google.com/mapfiles/ms/icons/green-dot.png':[(37.4419, -122.1419)],
                 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png':[(37.4300, -122.1400)]}
    )

    try:
        return render_template('four_google_map.html', mymap=mymap, sndmap=sndmap)
    except TemplateNotFound:
        abort(404)

@google_map.route("/")
def mapview():
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        style="height:100%; width:100%; top:0; left:0; position:absolute; z-index:200;",
        zoom=12,
        maptype="TERRAIN",  # "ROADMAP"
        infobox=[
            "<img src='https://pbs.twimg.com/media/CM2tF0AWIAAMtJG.jpg' height=100 width=100>"
            "<p>SOME TEXT</p>"
            "<a href='http://google.com'>visit google.com</a>",
            "<img src='https://pbs.twimg.com/media/CM2tF5hUkAA-bs6.jpg' height=100 width=100>"
            "<ul>"
            "<li>Coffee</li>"
            "<li>Tea</li>"
            "<li>Milk</li>"
            "</ul>"
        ],
        markers={'http://maps.google.com/mapfiles/ms/icons/blue-dot.png':
                     [(37.4300, -122.1400), (37.4419, -122.1419)]}
    )

    try:
        return render_template('google_map.html', sndmap=sndmap)
    except TemplateNotFound:
        abort(404)

