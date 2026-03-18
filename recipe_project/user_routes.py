# from flask import Blueprint, request, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from models import User
# from decorators import get_current_user, admin_required, role_required
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
#
# # יצירת Blueprint - למה זה מקצועי?
# # במקום להעמיס את כל הנתיבים בקובץ הראשי, אנחנו יוצרים "שלוחה".
# # url_prefix='/users' חוסך כתיבה של /users לפני כל נתיב ושומר על סדר.
# user_bp = Blueprint('users', __name__, url_prefix='/users')
#
# # --- נתיב הרשמה ---
#
# @user_bp.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     # בדיקת כפילות: מונע שגיאות בסיס נתונים (Integrity Error) ומחזיר הודעה ברורה למשתמש.
#     if User.query.filter_by(email=data['email']).first():
#         return jsonify({"message": "משתמש עם אימייל זה כבר קיים"}), 409
#
#     # למה generate_password_hash?
#     # לעולם לא שומרים סיסמה גלויה! אם בסיס הנתונים ייפרץ, הסיסמאות יישארו מוגנות.
#     hashed_password = generate_password_hash(data['password'])
#
#     new_user = User(
#         username=data['username'],
#         email=data['email'],
#         password=hashed_password,
#         role='Reader',
#         is_approved_uploader=False
#     )
#     new_user.save()
#     return jsonify({"message": "המשתמש נרשם בהצלחה!"}), 201
#
#
# # --- נתיב כניסה (Login) ---
# @user_bp.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     user = User.query.filter_by(username=data['username']).first()
#
#     # check_password_hash: משווה בין הסיסמה הגלויה ל-Hash המוצפן.
#     if not user or not check_password_hash(user.password, data['password']):
#         return jsonify({"message": "שם משתמש או סיסמה שגויים"}), 401
#
#     # למה JWT (access_token)?
#     # בניגוד ל-Session, טוקן הוא Stateless. השרת לא צריך לזכור מי מחובר.
#     # המידע (ID ותפקיד) נמצא בתוך הטוקן החתום. זה מאפשר לאפליקציה לגדול (Scalability).
#     access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
#
#     return jsonify({
#         "message": "התחברת בהצלחה!",
#         "token": access_token,
#         "user_id": user.id,
#         "username": user.username,
#         "role": user.role,
#         "has_requested_upgrade": user.has_requested_upgrade
#     }), 200
#
#
# # --- בקשת שדרוג למעלה מתכונים ---
# @user_bp.route('/request_uploader', methods=['POST'])
# @jwt_required()  # מבטיח שרק משתמש מחובר (עם טוקן תקף) יכול לגשת.
# def request_uploader_status():
#     # get_jwt_identity: שולף את ה-ID ישירות מהטוקן. מאובטח מאוד - המשתמש לא יכול "לזייף" ID של מישהו אחר.
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
#
#     if not user:
#         return jsonify({"message": "משתמש לא נמצא"}), 404
#
#     user.has_requested_upgrade = True
#     user.save()
#     return jsonify({"message": "בקשתך נשלחה למנהל המערכת"}), 200
#
#
# # --- נתיבים למנהל בלבד ---
# @user_bp.route('/pending_uploaders', methods=['GET'])
# @admin_required  # שימוש ב-Decorator מותאם אישית (Custom Decorator).
# # למה זה טוב? זה מפריד את הלוגיקה של האבטחה מהלוגיקה של הפונקציה.
# # זה הופך את הקוד לקריא (Clean Code) ומונע שכפול קוד בכל נתיב של מנהל.
# def get_pending_uploaders():
#     users = User.query.filter_by(role='Reader', is_approved_uploader=False, has_requested_upgrade=True).all()
#     output = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
#     return jsonify(output), 200
#
#
# @user_bp.route('/approve/<int:user_id>', methods=['POST'])
# @admin_required
# def approve_user(user_id):
#     # get_or_404: קיצור דרך מקצועי - אם ה-ID לא קיים, הוא מחזיר אוטומטית שגיאה 404.
#     user = User.query.get_or_404(user_id)
#     user.role = 'Uploader'
#     user.is_approved_uploader = True
#     user.save()
#     return jsonify({"message": f"המשתמש {user.username} אושר כמעלה מתכונים"}), 200

# ----------------------
# # from flask import Blueprint, request, jsonify
# # from werkzeug.security import generate_password_hash, check_password_hash
# # from models import User
# # from decorators import get_current_user # נשתמש רק ב-get_current_user אם צריך
# # from decorators import admin_required, role_required
# # from flask_jwt_extended import create_access_token # ייבוא הפונקציה ליצירת טוקן
# # # הגדרת Blueprint: כל הנתיבים יתחילו ב-/users
# # user_bp = Blueprint('users', __name__, url_prefix='/users')
# #
# #
# # # נתיב הרשמה
# # @user_bp.route('/register', methods=['POST'])
# # def register():
# # data = request.json
# #
# # # 1. בדיקת קיום (עובד כבר)
# # existing_user = User.query.filter_by(email=data['email']).first()
# # if existing_user:
# # return jsonify({"message": "משתמש עם אימייל זה כבר קיים"}), 409
# #
# # # 2. הצפנת הסיסמה (עובד כבר)
# # hashed_password = generate_password_hash(data['password'])
# #
# # # 3. יצירת מופע ושמירה (התיקון כאן!)
# # new_user = User(
# # # username=data['username'], # <--- הבעיה כאן
# # # email=data['email'],
# # # *** חובה להכניס את הנתונים שנשלחו ***
# # username=data['username'], # <-- הוספנו את שם המשתמש
# # email=data['email'], # <-- הוספנו את האימייל
# # # ***********************************
# # password=hashed_password,
# # role='Reader',
# # is_approved_uploader=False
# # )
# #
# # # 4. שמירה ב-DB
# # new_user.save()
# #
# # return jsonify({"message": "המשתמש נרשם בהצלחה!"}), 201
# #
# # # נתיב כניסה
# # @user_bp.route('/login', methods=['POST'])
# # def login():
# # data = request.json
# # user = User.query.filter_by(username=data['username']).first()
# #
# # # בדיקת משתמש וסיסמה
# # if not user or not check_password_hash(user.password, data['password']):
# # return jsonify({"message": "שם משתמש או סיסמה שגויים"}), 401
# #
# # # הצלחה - **כאן צריך ליצור Session או Token (לא לפרויקט המלא, רק לשליחת User-ID)**
# # return jsonify({
# # "message": "התחברת בהצלחה!",
# # "user_id": user.id,
# # "role": user.role
# # }), 200
# # #--------------פרופיל מנהל ואישור משתמשי תוכן----------------
# #
# #
# # # 1. נתיב למשתמש רגיל לבקש להפוך למעלה מתכונים
# # @user_bp.route('/request_uploader', methods=['POST'])
# # def request_uploader_status():
# # user = get_current_user()
# # if not user:
# # return jsonify({"message": "נדרשת התחברות"}), 401
# #
# # # המשתמש נשאר Reader אבל מסומן כמי שמבקש אישור (בצד הלקוח נציג זאת למנהל)
# # # לצורך הפשטות, נשתמש בשדה קיים או נוסיף לוגיקה
# # return jsonify({"message": "בקשתך נשלחה למנהל המערכת"}), 200
# #
# # # 2. נתיב למנהל לראות את כל המשתמשים שמבקשים אישור
# # @user_bp.route('/pending_uploaders', methods=['GET'])
# # @admin_required
# # def get_pending_uploaders():
# # # שליפת כל המשתמשים שהם לא Uploader אבל ביקשו (אפשר לסנן לפי לוגיקה שתבחרי)
# # users = User.query.filter_by(role='Reader', is_approved_uploader=False).all()
# # output = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
# # return jsonify(output), 200
# #
# # # 3. נתיב למנהל לאשר משתמש
# # @user_bp.route('/approve/<int:user_id>', methods=['POST'])
# # @admin_required
# # def approve_user(user_id):
# # user = User.query.get_or_404(user_id)
# # user.role = 'Uploader'
# # user.is_approved_uploader = True
# # user.save()
# # return jsonify({"message": f"המשתמש {user.username} אושר כמעלה מתכונים"}), 200
# from flask import Blueprint, request, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from models import User
# from decorators import get_current_user, admin_required, role_required
# # ייבוא הספריה לניהול טוקנים (JWT)
# from flask_jwt_extended import create_access_token
#
# from flask_jwt_extended import jwt_required, get_jwt_identity
# user_bp = Blueprint('users', __name__, url_prefix='/users')
#
#
# # --- נתיב הרשמה (נשאר כמעט זהה, מוודא תקינות) ---
# @user_bp.route('/register', methods=['POST'])
# def register():
# data = request.json
#
# if User.query.filter_by(email=data['email']).first():
# return jsonify({"message": "משתמש עם אימייל זה כבר קיים"}), 409
#
# hashed_password = generate_password_hash(data['password'])
#
# new_user = User(
# username=data['username'],
# email=data['email'],
# password=hashed_password,
# role='Reader', # ברירת מחדל כפי שנדרש במסמך
# is_approved_uploader=False
# )
#
# new_user.save()
# return jsonify({"message": "המשתמש נרשם בהצלחה!"}), 201
#
#
# # --- נתיב כניסה מעודכן עם TOKEN ---
# # @user_bp.route('/login', methods=['POST'])
# # def login():
# # data = request.json
# # # חיפוש משתמש לפי שם משתמש (או אימייל, תלוי מה בחרת בטופס)
# # user = User.query.filter_by(username=data['username']).first()
# #
# # if not user or not check_password_hash(user.password, data['password']):
# # return jsonify({"message": "שם משתמש או סיסמה שגויים"}), 401
# #
# # # יצירת Access Token שמכיל את ה-ID והתפקיד של המשתמש
# # # זהו ה"מפתח" שהאנגולר ישלח בכל בקשה
# # access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
# #
# # return jsonify({
# # "message": "התחברת בהצלחה!",
# # "token": access_token, # הטוקן החדש
# # "user_id": user.id,
# # "username": user.username, # נחוץ כדי להציג "שלום admin"
# # "role": user.role
# # }), 200
# #
#
# @user_bp.route('/login', methods=['POST'])
# def login():
# data = request.json
# # חיפוש משתמש לפי שם משתמש (או אימייל, תלוי מה בחרת בטופס)
# user = User.query.filter_by(username=data['username']).first()
#
# # בדיקת סיסמה
# if not user or not check_password_hash(user.password, data['password']):
# return jsonify({"message": "שם משתמש או סיסמה שגויים"}), 401
#
# # יצירת טוקן שמכיל בתוכו את ה-ID והתפקיד של המשתמש
# access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
#
# return jsonify({
# "message": "התחברת בהצלחה!",
# "token": access_token, # <--- זה המפתח שהאנגולר צריך לשמור
# "user_id": user.id,
# "username": user.username, # נחוץ כדי להציג "שלום admin"
# "role": user.role
# }), 200
#
# # --- נתיבים נוספים (ניהול מנהל) ---
#
# @user_bp.route('/request_uploader', methods=['POST'])
# def request_uploader_status():
# user = get_current_user()
# if not user:
# return jsonify({"message": "נדרשת התחברות"}), 401
#
# # כאן כדאי להוסיף שדה ב-DB כמו 'has_requested_upgrade' אם רוצים מעקב אמיתי
# return jsonify({"message": "בקשתך נשלחה למנהל המערכת"}), 200
#
#
# @user_bp.route('/pending_uploaders', methods=['GET'])
# @admin_required
# def get_pending_uploaders():
# # שליפת משתמשים שהם Reader אבל אינם מאושרים עדיין
# users = User.query.filter_by(role='Reader', is_approved_uploader=False).all()
# output = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
# return jsonify(output), 200
#
#
# @user_bp.route('/approve/<int:user_id>', methods=['POST'])
# @admin_required
# def approve_user(user_id):
# user = User.query.get_or_404(user_id)
# user.role = 'Uploader'
# user.is_approved_uploader = True
# user.save()
# return jsonify({"message": f"המשתמש {user.username} אושר כמעלה מתכונים"}), 200
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from decorators import get_current_user, admin_required, role_required
# ייבוא הספריה לניהול טוקנים (JWT)
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

user_bp = Blueprint('users', __name__, url_prefix='/users')


# --- נתיב הרשמה ---
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "משתמש עם אימייל זה כבר קיים"}), 409

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        role='Reader',
        is_approved_uploader=False
    )
    new_user.save()
    return jsonify({"message": "המשתמש נרשם בהצלחה!"}), 201


# --- נתיב כניסה מעודכן ---
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    # check_password_hash: משווה בין הסיסמה הגלויה ל-Hash המוצפן.
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message": "שם משתמש או סיסמה שגויים"}), 401

    # למה JWT (access_token)?
    # בניגוד ל-Session, טוקן הוא Stateless. השרת לא צריך לזכור מי מחובר.
    # המידע (ID ותפקיד) נמצא בתוך הטוקן החתום. זה מאפשר לאפליקציה לגדול (Scalability).
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({
        "message": "התחברת בהצלחה!",
        "token": access_token,
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "has_requested_upgrade": user.has_requested_upgrade
    }), 200


# --- בקשת שדרוג למעלה מתכונים ---
@user_bp.route('/request_uploader', methods=['POST'])
@jwt_required()  # מבטיח שרק משתמש מחובר (עם טוקן תקף) יכול לגשת.
def request_uploader_status():
    # get_jwt_identity: שולף את ה-ID ישירות מהטוקן. מאובטח מאוד - המשתמש לא יכול "לזייף" ID של מישהו אחר.
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "משתמש לא נמצא"}), 404

    user.has_requested_upgrade = True
    user.save()
    return jsonify({"message": "בקשתך נשלחה למנהל המערכת"}), 200


# --- נתיבים למנהל בלבד ---
@user_bp.route('/pending_uploaders', methods=['GET'])
@admin_required  # שימוש ב-Decorator מותאם אישית (Custom Decorator).
# למה זה טוב? זה מפריד את הלוגיקה של האבטחה מהלוגיקה של הפונקציה.
# זה הופך את הקוד לקריא (Clean Code) ומונע שכפול קוד בכל נתיב של מנהל.
def get_pending_uploaders():
    users = User.query.filter_by(role='Reader', is_approved_uploader=False, has_requested_upgrade=True).all()
    output = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    return jsonify(output), 200


@user_bp.route('/approve/<int:user_id>', methods=['POST'])
@admin_required
def approve_user(user_id):
    # get_or_404: קיצור דרך מקצועי - אם ה-ID לא קיים, הוא מחזיר אוטומטית שגיאה 404.
    user = User.query.get_or_404(user_id)
    user.role = 'Uploader'
    user.is_approved_uploader = True
    user.save()
    return jsonify({"message": f"המשתמש {user.username} אושר כמעלה מתכונים"}), 200


# --- נתיב לקבלת פרטי פרופיל של משתמש ספציפי ---
@user_bp.route('/profile/<int:user_id>', methods=['GET', 'OPTIONS'])
@jwt_required()  # מומלץ להשאיר מאובטח כדי שרק משתמשים רשומים יראו פרופילים
def get_profile(user_id):
    # חיפוש המשתמש לפי ה-ID שהגיע מהכתובת
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "משתמש לא נמצא"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_approved_uploader": user.is_approved_uploader,
        "has_requested_upgrade": user.has_requested_upgrade
    }), 200