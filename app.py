from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from forms import *
from flask_wtf import FlaskForm
import dateutil.parser
import babel
import config
import datetime

app = Flask(__name__)

database_name = "eventapp"
database_path = "postgresql://postgres:eazye5000@{}/{}".format('localhost:5432', database_name)
app.config["SQLALCHEMY_DATABASE_URI"] = database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
moment = Moment(app)

migrate = Migrate(app, db)


# --Models--

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(250))

    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f"<Venue {self.id} name: {self.name}>"

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f"<Artis {self.id} name: {self.name}>"

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f"<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>"



# --Filters--

# format datetime
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

# --Controllers--

# index page

@app.route('/')
def index():
    return render_template('pages/home.html')

# Venues
@app.route('/venues')
def venues():
    data = []
    # get all venues
    venues = Venue.query.all()

    # Use set so there are no duplicate venues
    locations = set()

    for venue in venues:
        # add city / state tuples
        locations.add((venue.city, venue.state))

    # for each unique city / state, add venues
    for location in locations:
        data.append({
            "city": location[0],
            "state": location[1],
            "venues": []
            })

    for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()
        # get current date to filter num_upcoming_shows
        current_date = datetime.now()

        for show in shows:
            if show.start_time > current_date:
                num_upcoming += 1

        for venue_location in data:
            if venue.state == venue_location['state'] and venue.city == venue_location['city']:
                venue_location['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming_shows
                    })
    return render_template('pages/venues.html', areas=data)


# --Launch--

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
