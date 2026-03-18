# # --- פונקציית עזר לשליפת המשתמש הנוכחי ---
# def get_current_user():
#     """
#     פונקציה זו מחזירה את אובייקט המשתמש (User Model) מתוך הטוקן.
#     היא שימושית כשרוצים לדעת בתוך נתיב מי המשתמש (למשל, כדי לשייך לו מתכון).
#     """
#     try:
#         # מוודא שיש טוקן תקין בבקשה
#         verify_jwt_in_request()
#         # שליפת המזהה (ID) שנשמר בתוך הטוקן
#         user_id = get_jwt_identity()
#         # שליפת המשתמש ממסד הנתונים
#         return User.query.get(user_id)
#     except Exception:
#         # במקרה שאין טוקן או שהוא לא תקין
#         return None
#
#
# # --- הדקורטור הראשי: בדיקת הרשאות ---
# def role_required(required_role):
#     """
#     דקורטור שבודק האם למשתמש יש את ההרשאה הנדרשת (או גבוהה ממנה).
#     סדר הכוח: Admin > Uploader > Reader
#     """
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             # 1. אימות טוקן מול Flask-JWT-Extended
#             try:
#                 verify_jwt_in_request()
#             except Exception as e:
#                 return jsonify({"message": "Token is missing, invalid or expired"}), 401
#
#             # 2. שליפת ה-Claims (המידע הנוסף) מתוך הטוקן
#             claims = get_jwt()
#             user_role = claims.get("role")  # התפקיד נשמר בטוקן בעת ה-Login
#
#             # 3. הגדרת היררכיית התפקידים
#             # האינדקס קובע את החוזק: Reader=0, Uploader=1, Admin=2
#             roles_hierarchy = ['Reader', 'Uploader', 'Admin']
#
#             if user_role not in roles_hierarchy:
#                 return jsonify({"message": "Access denied: Unknown role"}), 403
#
#             # 4. בדיקת חוזק התפקיד
#             # אם נדרש Uploader (1), ולי יש Admin (2) -> 2 >= 1 -> עובר
#             if roles_hierarchy.index(user_role) < roles_hierarchy.index(required_role):
#                 return jsonify({"message": "Access denied: Insufficient permissions"}), 403
#
#             # 5. אם הכל תקין, הרצת הפונקציה המקורית
#             return f(*args, **kwargs)
#
#         return decorated_function
#     return decorator
#
#
# # --- קיצור דרך למנהלים ---
# def admin_required(f):
#     """דקורטור שדורש ספציפית הרשאת מנהל"""
#     return role_required('Admin')(f)


# ---------------------
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from models import User


# --- פונקציית עזר לשליפת המשתמש הנוכחי ---
def get_current_user():
    """
    פונקציה זו מחזירה את אובייקט המשתמש (User Model) מתוך הטוקן.
    היא שימושית כשרוצים לדעת בתוך נתיב מי המשתמש (למשל, כדי לשייך לו מתכון).
    """
    try:
        # מוודא שיש טוקן תקין בבקשה
        verify_jwt_in_request()
        # שליפת המזהה (ID) שנשמר בתוך הטוקן
        user_id = get_jwt_identity()
        # שליפת המשתמש ממסד הנתונים
        return User.query.get(user_id)
    except Exception:
        # במקרה שאין טוקן או שהוא לא תקין
        return None


# --- הדקורטור הראשי: בדיקת הרשאות ---
def role_required(required_role):
    """
דקורטור שבודק האם למשתמש יש את ההרשאה הנדרשת (או גבוהה ממנה).
    סדר הכוח:        Admin > Uploader > Reader
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. אימות טוקן מול Flask-JWT-Extended
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({"message": "Token is missing, invalid or expired"}), 401

            # 2. שליפת ה-Claims (המידע הנוסף) מתוך הטוקן
            claims = get_jwt()
            user_role = claims.get("role")  # התפקיד נשמר בטוקן בעת ה-Login

            # 3. הגדרת היררכיית התפקידים
            # האינדקס קובע את החוזק: Reader=0, Uploader=1, Admin=2
            roles_hierarchy = ['Reader', 'Uploader', 'Admin']

            if user_role not in roles_hierarchy:
                return jsonify({"message": "Access denied: Unknown role"}), 403

            # 4. בדיקת חוזק התפקיד
            # אם נדרש Uploader (1), ולי יש Admin (2) -> 2 >= 1 -> עובר
            if roles_hierarchy.index(user_role) < roles_hierarchy.index(required_role):
                return jsonify({"message": "Access denied: Insufficient permissions"}), 403

            # 5. אם הכל תקין, הרצת הפונקציה המקורית
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# # --- קיצור דרך למנהלים ---
def admin_required(f):
    """דקורטור שדורש ספציפית הרשאת מנהל"""
    return role_required('Admin')(f)
