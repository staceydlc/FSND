
class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete="CASCADE"))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete="CASCADE"))

    def __repr__(self):
        return (self.name)

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))

    def __repr__(self):
        return (self.name)

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))

    def __repr__(self):
        return (self.name)
