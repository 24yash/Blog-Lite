from flask_restful import Api, Resource, reqparse
from models import *

api = Api()

parser = reqparse.RequestParser()
parser.add_argument("post_title")
parser.add_argument("post_content")

class API_R(Resource):
  def get(self):
    post_json = {}
    all_post = Post.query.all()
    for post in all_post:
      post_json[post.id] = post.title

    return post_json

class API_UD(Resource):
  def get(self, post_id):
    post_id_json = {}
    this_post = Post.query.get(post_id)
    post_id_json["id"] = this_post.id
    post_id_json["title"] = this_post.title
    post_id_json["creator"] = this_post.creator
    post_id_json["content"] = this_post.content
    return post_id_json

  def put(self, post_id):
    args = parser.parse_args()
    this_post = Post.query.get(post_id)
    if this_post is None:
       return 'Post Not Found', 404
    this_post.title=args['post_title']
    this_post.content=args['post_content']
    db.session.commit()
    return '', 201

  def delete(self, post_id):
        this_post = Post.query.get(post_id)
        db.session.delete(this_post)
        db.session.commit()
        return '', 201
    
    
api.add_resource(API_R, "/all_post")
api.add_resource(API_UD, "/api_post/<int:post_id>")
    