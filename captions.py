from flask import Flask, make_response, jsonify, request
from models import Users, Category, Captions, Like
from main import app, db
import json

category = Category.query.all()
if not category:
    import categories

@app.route('/register', methods=['POST'])
def register():
    # Query to see if the user already exists
    user = Users.query.filter_by(email_id=request.data['email']).first()

    if not user:

        # Query to see if username already exists
        username = Users.query.filter_by(username=request.data['username']).first()

        if not username:
            # Register the new user
            try:                
                data = request.data
                fname = data['fname']
                lname = data['lname']
                username = data['username']
                email = data['email']
                password = data['password']
                confirm_password = data['confirm_pwd']

                if(password == confirm_password):
                    user = Users(first_name=fname, last_name=lname, username=username, email_id=email, password=password)
                    db.session.add(user)
                    db.session.commit()

                    response = {
                        'message': 'Registeration done successfully! Please login.'
                    }
                    
                    # return a response notifying the user that they registered successfully
                    return make_response(jsonify(response)), 201
                else:
                    response = {
                        'message': 'Password does not match.'
                    }
                    
                    # return a response notifying that the password does not match
                    return make_response(jsonify(response)), 400
            except Exception as e:
                # An error occured, return the error message
                response = {
                    'message': str(e)
                }
                    
                # return a response notifying the error message
                return make_response(jsonify(response)), 500
        else:            
            response = {
                'message': 'Username already exists. Please try another.'
            }
                    
            # return a response notifying the error message
            return make_response(jsonify(response)), 400        
    else:
        response = {
           'message': 'User already exists. Please login.'
        }
                    
        # return a response notifying the error message
        return make_response(jsonify(response)), 400   


@app.route('/login', methods=['POST'])
def login():
    try:
        # Get the user object using their email (unique to every user)
        user = Users.query.filter((Users.email_id == request.data['login_id']) | (Users.username == request.data['login_id'])).first()

        # Try to authenticate the found user using their password
        if user and user.password == request.data['password']:
            # Generate the access token. This will be used as the authorization header
            access_token = user.generate_token(user.id)            
            if access_token:
                response = {
                  'message': 'You logged in successfully.',
                  'access_token': access_token.decode(),                  
                  'first_name': user.first_name,
                  'last_name': user.last_name,
                  'username': user.username,
                  'email_id': user.email_id
                }
                return make_response(jsonify(response)), 200
        else:
            # User does not exist. Therefore, we return an error message
            response = {
                'message': 'Invalid credentials, Please try again.'
            }
            return make_response(jsonify(response)), 401

    except Exception as e:
        # Create a response containing an string error message
        response = {
            'message': str(e)
        }
        # Return a server error using the HTTP Error Code 500 (Internal Server Error)

        return make_response(jsonify(response)), 500


@app.route('/categories', methods=['GET'])
def categories_all():
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        user = Users.query.filter_by(id=user_id).first()
        if user:
            # User is authenticated, GET all the captions and categories
            category = Category.query.all()
            cat_list = []
            for c in category:
                cat_dict = {
                        'id': c.id,
                        'category_name': c.category_name
                    }
                cat_list.append(cat_dict)
                response = {                
                'category': cat_list                
            }
            return make_response(jsonify(response)), 200
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401



@app.route('/captions', methods=['GET', 'POST'])
def captions():
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        userid = Users.decode_token(access_token)
        user = Users.query.filter_by(id=userid).first()
        if user:
            # User is authenticated
            if request.method == "GET":
                # GET all captions with corresponding category and username
                captions = Captions.query.join(Users, Captions.user_id == Users.id)\
                           .join(Category, Captions.category_id == Category.id)\
                           .add_columns(Captions.id, Captions.caption, Captions.user_id, Users.username,\
                            Category.category_name, Captions.like_count, Captions.timestamp)\
                           .order_by(Captions.id.asc()).all()
                
                cap_list = []
                for c in captions:                    
                    cap_dict = {
                            'id': c.id,
                            'caption': c.caption,
                            'user_id': c.user_id,
                            'username': c.username,
                            'category_name': c.category_name,
                            'like_count': c.like_count,
                            'timestamp': c.timestamp
                        }
                    cap_list.append(cap_dict)
                    
                response = {                                
                    'captions': cap_list
                }
                return make_response(jsonify(response)), 200

            elif request.method == "POST":
                # POST the caption to the database
                data = request.data
                cap = str(data.get('caption', ''))
                if cap:                    
                    caption = Captions(user_id=userid, category_id=data['category_id'], caption=cap)
                    db.session.add(caption)
                    db.session.commit()

                    response = {                                
                        'message': 'Caption was posted successfully!'
                    }
                    return make_response(jsonify(response)), 201
                else:
                    response = {                                
                        'message': 'Invalid caption text!' 
                    }
                    return make_response(jsonify(response)), 401
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401



@app.route('/category/captions', methods=['POST'])
def category_captions():
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        user = Users.query.filter_by(id=user_id).first()
        if user:
            # User is authenticated, GET the captions based on the categories selected
            data = request.get_json()
            categories = data['categories']            
            captions = Captions.query.filter(Captions.category_id.in_(categories))\
                       .join(Users, Captions.user_id == Users.id)\
                       .join(Category, Captions.category_id == Category.id)\
                       .add_columns(Captions.id, Captions.caption, Captions.user_id, Users.username,\
                        Category.category_name, Captions.like_count, Captions.timestamp)\
                       .order_by(Captions.id.desc()).all()
            
            cap_list = []
            for c in captions:
                cap_dict = {
                        'id': c.id,
                        'caption': c.caption,
                        'user_id': c.user_id,
                        'username': c.username,
                        'category_name': c.category_name,
                        'like_count': c.like_count,
                        'timestamp': c.timestamp
                    }
                cap_list.append(cap_dict)
                
            response = {                                
                'captions': cap_list
            }
            return make_response(jsonify(response)), 200
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401


@app.route('/captions/search/<string:searchQuery>', methods=['GET'])
def search_captions(searchQuery, **kwargs):
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        user = Users.query.filter_by(id=user_id).first()
        if user:
            # User is authenticated, GET the captions based on the categories selected                    
            captions = Captions.query.filter(Captions.caption.like('%' + searchQuery + '%'))\
                       .join(Users, Captions.user_id == Users.id)\
                       .join(Category, Captions.category_id == Category.id)\
                       .add_columns(Captions.id, Captions.caption, Captions.user_id, Users.username,\
                        Category.category_name, Captions.like_count, Captions.timestamp)\
                       .order_by(Captions.id.desc()).all()
            
            cap_list = []
            for c in captions:
                cap_dict = {
                        'id': c.id,
                        'caption': c.caption,
                        'user_id': c.user_id,
                        'username': c.username,
                        'category_name': c.category_name,
                        'like_count': c.like_count,
                        'timestamp': c.timestamp
                    }
                cap_list.append(cap_dict)
                
            response = {                                
                'captions': cap_list
            }
            return make_response(jsonify(response)), 200
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401



@app.route('/user/captions', methods=['GET'])
def user_captions():
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        userid = Users.decode_token(access_token)
        user = Users.query.filter_by(id=userid).first()
        if user:
            # User is authenticated, GET the captions and categories posted by logged in user            
            captions = Captions.query.filter_by(user_id=userid)\
                       .join(Users, Captions.user_id == Users.id)\
                       .join(Category, Captions.category_id == Category.id)\
                       .add_columns(Captions.id, Captions.caption, Captions.user_id, Users.username,\
                        Category.category_name, Captions.like_count, Captions.timestamp)\
                       .order_by(Captions.id.desc()).all()
            
            cap_list = []
            for c in captions:
                cap_dict = {
                        'id': c.id,
                        'caption': c.caption,
                        'user_id': c.user_id,
                        'username': c.username,
                        'category_name': c.category_name,
                        'like_count': c.like_count,
                        'timestamp': c.timestamp
                    }
                cap_list.append(cap_dict)
                
            response = {                                
                'captions': cap_list
            }
            return make_response(jsonify(response)), 200
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401



@app.route('/users/captions/<int:uid>', methods=['GET'])
def users_captions(uid, **kwargs):
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        user_id = Users.decode_token(access_token)
        user = Users.query.filter_by(id=user_id).first()
        if user:
            # User is authenticated, GET the captions and categories posted by user            
            captions = Captions.query.filter_by(user_id=uid)\
                       .join(Users, Captions.user_id == Users.id)\
                       .join(Category, Captions.category_id == Category.id)\
                       .add_columns(Captions.id, Captions.caption, Captions.user_id, Users.username,\
                        Category.category_name, Captions.like_count, Captions.timestamp)\
                       .order_by(Captions.id.desc()).all()
            
            cap_list = []
            for c in captions:
                cap_dict = {
                        'id': c.id,
                        'caption': c.caption,
                        'user_id': c.user_id,
                        'username': c.username,
                        'category_name': c.category_name,
                        'like_count': c.like_count,
                        'timestamp': c.timestamp
                    }
                cap_list.append(cap_dict)
                
            response = {                                
                'captions': cap_list
            }
            return make_response(jsonify(response)), 200
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401



@app.route('/caption/<int:cid>', methods=['PUT', 'DELETE'])
def caption_operations(cid, **kwargs):
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        userid = Users.decode_token(access_token)
        user = Users.query.filter_by(id=userid).first()
        if user:
            # User is authenticated
            caption = Captions.query.filter_by(id=cid).first()

            if not caption:
                # There is no caption with this ID for this User, so
                # Raise an HTTPException with a 404 not found status code
                abort(404)
                
            if request.method == "DELETE":
                # DELETE the caption 
                likes = Like.query.filter_by(caption_id=cid).all()
                
                for like in likes:
                    like.delete()

                caption.delete()                    
                response = {                                
                    'message': 'Caption Deleted!'
                }
                return make_response(jsonify(response)), 200

            if request.method == "PUT":
                #UPDATE the caption
                caption_text = request.data['caption_text'];
                caption.caption = caption_text;
                db.session.add(caption)
                db.session.commit()
                
                response = {
                    'message': 'Caption Updated!'
                }
                return make_response(jsonify(response)), 200
                    
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401



@app.route('/caption/like', methods=['GET'])
def caption_like():
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        userid = Users.decode_token(access_token)
        user = Users.query.filter_by(id=userid).first()
        if user:
            # User is authenticated
                
            if request.method == "GET":
                #GET all captions user liked
                liked_captions = Like.query.filter_by(user_id=userid).all()

                cap_list = []

                for x in liked_captions:
                    cap_dict = {
                        'id': x.id,
                        'caption_id': x.caption_id,
                        'user_id': x.user_id,
                        'timestamp': x.timestamp
                    }
                    cap_list.append(cap_dict)

                response = {
                    'liked_captions': cap_list
                }
                return make_response(jsonify(response)), 200
            
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401



@app.route('/caption/like/<int:cid>', methods=['POST', 'DELETE'])
def like_operations(cid, **kwargs):
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
         # Attempt to decode the token and get the User ID
        userid = Users.decode_token(access_token)
        user = Users.query.filter_by(id=userid).first()
        if user:
            # User is authenticated
            caption = Captions.query.filter_by(id=cid).first()
            like = Like.query.filter_by(caption_id=cid).first()

            if not caption and not like:
                # There is no caption with this ID for this User, so
                # Raise an HTTPException with a 404 not found status code
                abort(404)
                
            if request.method == "POST":
                like = Like(caption_id=cid, user_id=userid)
                db.session.add(like)
                caption.like_count = caption.like_count + 1                
                db.session.add(caption)
                db.session.commit()
                
                response = {                                
                    'message': 'Like Added!'
                }
                return make_response(jsonify(response)), 200

            if request.method == "DELETE":
                # DELETE the caption                                
                like.delete()
                caption.like_count = caption.like_count - 1                
                db.session.add(caption)
                db.session.commit()

                response = {                                
                    'message': 'Like Deleted!'
                }
                return make_response(jsonify(response)), 200            
            
        else:
            # User does not exists, return error message
            response = {
                'message': 'User does not exists, please register/login.'
            }
            return make_response(jsonify(response)), 401
    else:
        # No access token found, return error message
            response = {
                'message': 'Invalid token found, please login again.'
            }
            return make_response(jsonify(response)), 401
