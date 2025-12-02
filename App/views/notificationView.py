from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.controllers.notification import (
    get_user_notifications, 
    mark_as_read,
    clear_notifications
)

notification_views = Blueprint('notification_views', __name__)

# Get all notifications for logged-in staff member
@notification_views.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    
    try:
        staff_id = int(get_jwt_identity())
        notifications = get_user_notifications(staff_id)
        return jsonify([n.to_json() for n in notifications]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 16b: Mark notification as read
@notification_views.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    try:
        staff_id = int(get_jwt_identity())
        notification = mark_as_read(notification_id)
        
        if not notification:
            return jsonify({"error": "Notification not found"}), 404
            
        # Only owner can mark as read
        if notification.receiver_id != staff_id:
            return jsonify({"error": "Unauthorized"}), 403
            
        return jsonify(notification.to_json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Clear all notifications for user
@notification_views.route('/api/notifications', methods=['DELETE'])
@jwt_required()
def clear_user_notifications():
    try:
        staff_id = int(get_jwt_identity())
        clear_notifications(staff_id)
        return jsonify({"message": "All notifications cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500