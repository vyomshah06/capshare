from main import app, db
import jwt
from datetime import datetime, timedelta

class Users(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    username = db.Column(db.String(30), nullable=False, unique=True)
    email_id = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        """Return the representation of a User instance"""
        return "<User: {}>".format(self.username)

    def generate_token(self, user_id):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=30),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                app.secret_key,
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, app.secret_key)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"


class Category(db.Model):
    """This class defines the category table."""

    __tablename__ = 'category'

    # define the columns of the table, starting with its primary key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_name = db.Column(db.String(20))

    def save(self):
        # Inserting new row to Category
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        """Return a representation of a category instance."""
        return "<Category: {}>".format(self.category_name)

class Captions(db.Model):
    """This class defines the captions table."""

    __tablename__ = 'captions'

    # define the columns of the table, starting with its primary key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    category_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    caption = db.Column(db.String(1000))
    like_count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def delete(self):
        """Deletes a given caption."""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Return a representation of a caption instance."""
        return "<Caption: {}>".format(self.caption)
    
class Like(db.Model):
    """This class defines the like table."""

    __tablename__ = 'like'

    # define the columns of the table, starting with its primary key
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    caption_id = db.Column(db.Integer, db.ForeignKey(Captions.id))
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def delete(self):
        """Deletes a like to a given caption."""
        db.session.delete(self)
        db.session.commit()
