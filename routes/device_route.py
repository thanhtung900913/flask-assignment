from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from db import get_connection, release_connection
from models.device_DTO import DeviceDTO

device_bp = Blueprint('device', __name__, url_prefix='/devices')

@device_bp.route('', methods = ['GET'])
@jwt_required()
def get_devices():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            select id, device_name, device_info, device_id
            from public.devices
            """
        )
        devices = cur.fetchall()
        
        return jsonify(
            {
            "data": devices,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Devices retrieved successfully"
            }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 400
        
    finally:
        if conn is not None:
            release_connection(conn)
        if cur is not None:
            cur.close()
            
@device_bp.route('/<id>', methods=['PATCH'])
@jwt_required()
def update_device(id):
    conn = None
    cur = None
    try:
        device = DeviceDTO(**request.json)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            update public.devices
            set device_info = %s, is_disabled = %s
            where id = %s
            """
        , (device.device_info, device.is_disabled, id))
        conn.commit()
        
        return jsonify({
            "message": "Device updated successfully for device id: " + id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        if conn is not None:
            conn.rollback()
        return jsonify({
            'error': str(e)
        }), 400
        
    finally:
        if conn is not None:
            release_connection(conn)
        if cur is not None:
            cur.close()
            
@device_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_device(id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            update public.user_devices
            set is_disabled = true
            where id = %s
            """, (id,)
        )
        cur.execute(
            """
            update refresh_tokens
            set is_revoked = true
            where device_id = %s and is_revoked = false
            """, (id,)
        )
        conn.commit()
        
        return jsonify({
            "message": "Device disabled successfully for device id: " + id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        if conn is not None:
            conn.rollback()
        return jsonify({
            'error': str(e)
        }), 400
        
    finally:
        if conn is not None:
            release_connection(conn)
        if cur is not None:
            cur.close()