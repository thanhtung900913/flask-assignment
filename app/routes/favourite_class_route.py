from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.db.connection import get_connection
from app.models.favourite_class_model import FavouriteClassDTO

favourite_class_bp = Blueprint('favourite_class', __name__, url_prefix='/favourites')

@favourite_class_bp.route('', methods=['POST'])
@jwt_required()
def add_favourite_class():
    conn = None
    cur = None
    try:
        favourite_class= FavouriteClassDTO(**request.json)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO user_favourite_classes (user_id, class_id)
            VALUES (%s, %s)
            """, (favourite_class.user_id, favourite_class.class_id)
        )
        conn.commit()
        # Logic to add a favourite class for the user
        return {"message": "Favourite class added successfully"}, 201
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@favourite_class_bp.route('/', methods=['GET'])
@jwt_required()
def get_favourite_classes():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        user_id = get_jwt_identity()
        cur.execute(
            """
            SELECT class_id FROM user_favourite_classes WHERE user_id = %s
            """, (user_id,)
        )
        favourite_classes = cur.fetchall()
        return jsonify({
            "data": favourite_classes,
            "message": "Favourite classes retrieved successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
@favourite_class_bp.route('/<class_id>', methods=['DELETE'])
@jwt_required()
def delete_favourite_class(class_id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        user_id = get_jwt_identity()
        cur.execute(
            """
            DELETE FROM user_favourite_classes WHERE user_id = %s AND class_id = %s
            """, (user_id, class_id)
        )
        conn.commit()
        return jsonify({
            "message": "Favourite class deleted successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()