from datetime import datetime, timezone, timedelta
import os
import hashlib
from flask import Blueprint, jsonify, request
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt

from app.db.connection import get_connection, release_connection
from app.models.auth_model import  LoginRequestBody, RegisterRequestBody
from app.utils.decorators import validate_payload

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
@validate_payload(RegisterRequestBody)
def register(body: RegisterRequestBody):
    conn = None
    cur = None
    try:
        user = request.get_json(body)
        conn = get_connection()
        cur = conn.cursor()
        
        bytes_password = user.password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytes_password, salt).decode('utf-8')
        # Create user in database
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)  RETURNING id", (user.username, hashed_password))
        user_id = cur.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
            }), 201
        
    except Exception as e:
        if conn is not None:
            conn.rollback()
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
    finally:
        if conn is not None:
            release_connection(conn)
        if cur is not None:
            cur.close()
            
@auth_bp.route('/login', methods=['POST'])
def login():
    conn = None
    cur = None
    try:
        user = LoginDTO(**request.json)
        conn = get_connection()
        cur = conn.cursor()
        # Fetch user from database
        cur.execute(
            """
            select id, username, password_hash
            from public.users
            where username = %s
            """,
            (user.username,)
        )
        user_db = cur.fetchone()
        
        if not user_db:
            return jsonify({
                'message': 'user not found',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        user_id, username, password_hash = user_db   
        is_valid = bcrypt.checkpw(
            user.password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
        if not is_valid:
            return jsonify({
                'message': 'password incorrect',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
            
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        hased_refresh_token = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
        # upsert user device info
        cur.execute(
            """
            INSERT INTO user_devices (id, user_id, device_info)
            VALUES (%s, %s, %s)
            ON CONFLICT (id)
            DO UPDATE SET
                device_info = EXCLUDED.device_info
            WHERE user_devices.device_info IS DISTINCT FROM EXCLUDED.device_info;""",
            (user.device_id, user_id, user.device_info))
        # revoke old refresh token and insert new refresh token
        cur.execute(
            """
            WITH revoke_old AS (
                UPDATE public.refresh_tokens
                SET is_revoked = true
                WHERE user_id = %s
                AND device_id = %s
                AND is_revoked = false
            )
            INSERT INTO public.refresh_tokens
                (user_id, device_id, token_hash, expires_at)
            VALUES (%s, %s, %s, %s)
            """, (
            user_id,
            user.device_id,
            user_id,
            user.device_id,
            hased_refresh_token,
            (datetime.now(timezone.utc) + timedelta(seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES")))).isoformat()
            ))
        conn.commit()
        
        return jsonify({
            'message': f'login success for user {username}',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        if conn is not None:
            conn.rollback()
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 400
        
    finally:
        if conn is not None:
            release_connection(conn)
        if cur is not None:
            cur.close()

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({
        'access_token': new_access_token
    }), 200
    
@auth_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)
    return jsonify({
        'message': 'logout successful'
    }), 200