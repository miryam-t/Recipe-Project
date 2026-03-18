# # ----------------- ייבוא ספריות (Imports) -----------------
#
# Flask: המנוע הראשי של השרת.
# send_from_directory: פונקציה המאפשרת להחזיר קבצים פיזיים (כמו תמונות) כתגובה לבקשת HTTP.
# # נדרש לייבא את db ואת המודלים כדי ליצור את הטבלאו
from flask import Flask, send_from_directory
# Flask-CORS: הכרחי כדי לאפשר לדפדפן (בו רץ ה-Angular) לקבל נתונים מהשרת (שיושב בפורט אחר).
from flask_cors import CORS

# ייבוא האובייקטים שהגדרנו במודל הנתונים (ORM).
# SQLAlchemy הופך טבלאות במסד הנתונים לאובייקטים של פיתון.
# ייבוא ה-DB והמודלים (הטבלאות) שיצרנו בקובץ models.py
from models import db, User, Recipe, IngredientEntry

# Blueprints: מאפשר לנו לפצל את הנתיבים לקבצים נפרדים כדי שהקוד יהיה קריא ומאורגן.
from user_routes import user_bp
from recipe_routes import recipes_bp

# JWT (JSON Web Token): טכנולוגיה לאימות משתמשים.
# השרת מנפיק "כרטיס כניסה" (Token) חתום למשתמש, והוא שולח אותו בכל בקשה.
from flask_jwt_extended import JWTManager

# werkzeug: ספריית עזר של פלאסק הכוללת פונקציות אבטחה.
# generate_password_hash: הופכת סיסמה גלויה (כמו "123") למחרוזת מוצפנת שאי אפשר לקרוא.
from werkzeug.security import generate_password_hash
import os


# ----------------- 1. הגדרת האפליקציה -----------------
# יצירת המופע המרכזי של אפליקציית ה-Flask
app = Flask(__name__)

#  הגדרת תיקיית ההעלאות כנתיב סטטי שפתוח לכולם
# # הגדרת נתיב אבסולוטי לתיקיית העלאות הקבצים (תמונות המתכונים)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')


# הגדרת CORS מפורטת:
# origins="*": מאפשר לכל דומיין לגשת (בייצור נגביל זאת רק לכתובת של האנגולר).
# expose_headers: חושף את ה-Header של ה-Authorization כדי שהאנגולר יוכל לקרוא את הטוקן.
# supports_credentials: מאפשר מעבר של עוגיות ומידע מאובטח.
# מאפשר לאנגולר לשלוח Headers של אבטחה
CORS(app, resources={r"/*": {"origins": "*"}},
     supports_credentials=True,
     expose_headers=["Authorization"],
     allow_headers=["Content-Type", "Authorization", "user-id"])

# הגדרות קונפיגורציה של האפליקציה (Configuration)
app.config['SECRET_KEY'] = 'your_strong_secret_key_here'  #  מפתח להצפנת סשנים פנימיים (לניהול Session והודעות)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'  # הגדרת סוג מסד הנתונים ומיקומו: שימוש ב-SQLite, הקובץ יישמר בשם recipes.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False# כיבוי התראות מערכת לחיסכון במשאבים

# # הגדרת מפתח סודי לחתימה על טוקנים של JWT - קריטי לאבטחה!
# המפתח שבו השרת משתמש כדי "לחתום" על הטוקן. רק מי שיש לו את המפתח יכול לאמת את הטוקן.
app.config['JWT_SECRET_KEY'] = 'my_super_secret_jwt_key'

# אתחול רכיבי המערכת\ה-JWT על האפליקציה שלנו
jwt = JWTManager(app) # חיבור מנגנון ה-JWT
db.init_app(app) # חיבור מסד הנתונים

# פונקציה ש"מייבאת" את הנתיבים שכתבי בקבצים אחרים (כמו דלפק קבלה שמפנה למחלקות שונות).
# 3. רישום ה-Blueprints: מחבר את נתיבי המשתמשים והמתכונים לשרת הראשי
app.register_blueprint(user_bp)
app.register_blueprint(recipes_bp)


# ----------------- 2. נתיב (Route) להגשת קבצים -----------------

# נתיב GET המקבל פרמטר משתנה <filename>.
# משמש להצגת תמונות המתכונים בדפדפן של המשתמש.
@app.route('/uploads/<filename>', methods=['GET'])
def get_image(filename):
    # הפונקציה מחפשת את הקובץ בתיקיית uploads ושולחת אותו כ-Response
    return send_from_directory('uploads', filename)

# @jwt.expired_token_loader
# @jwt.invalid_token_loader
# @jwt.unauthorized_loader
# def my_status_callback(err_str):
#     # אם הטוקן פג תוקף או לא תקין, במקום לקרוס, נתנהג כאילו אין משתמש
#     return None

# # ----------------- 3. אתחול והרצת השרת -----------------

#         # לוגיקה ליצירת משתמש מנהל (Admin) ראשוני אם המערכת ריקה
#         if not User.query.filter_by(username='admin').first():
#             admin_user = User(
#                 username='מנהל',
#                 email='admin@test.com',
#                 # אבטחה: לעולם לא נשמור סיסמה כטקסט פשוט, אלא רק את ה-Hash שלה
#                 password=generate_password_hash('123'),
#                 role='Admin',
#                 is_approved_uploader=True
#            )
#             admin_user.save() # שמירה לתוך מסד הנתונים
#             print("Admin user created with encrypted password!")
#
#     # הרצת השרת במצב debug=True:
#     # 1. טעינה אוטומטית של השרת בכל פעם שהקוד משתנה.
#     # 2. הצגת שגיאות מפורטות בדפדפן/טרמינל במקרה של תקלה.
#     app.run(debug=True)


# ----------------- 3. אתחול והרצת השרת -----------------

if __name__ == '__main__':
    # שימוש ב-app_context כדי לאפשר גישה למסד הנתונים לפני שהשרת עולה
    with app.app_context():
        # יצירת הקובץ recipes.db והטבלאות בתוכו לפי המודלים (רק אם אינם קיימים)
        db.create_all()
        print("Database tables created successfully!")

        # לוגיקה ליצירת משתמש מנהל (Admin) ראשוני אם המערכת ריקה
        if not User.query.filter_by(username='מנהל').first():
            admin_user = User(
                username='מנהל',
                email='admin@gmail.com',
                # אבטחה: לעולם לא נשמור סיסמה כטקסט פשוט, אלא רק את ה-Hash שלה
                password=generate_password_hash('123'),
                role='Admin',
                is_approved_uploader=True
            )
            admin_user.save()  # שמירה לתוך מסד הנתונים
            print("Admin user created with encrypted password!")

    # הרצת השרת במצב debug=True:
    # 1. טעינה אוטומטית של השרת בכל פעם שהקוד משתנה.
    # 2. הצגת שגיאות מפורטות בדפדפן/טרמינל במקרה של תקלה.
    app.run(debug=True)