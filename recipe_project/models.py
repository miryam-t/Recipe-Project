#
# # # # --- מחלקת מתכון (Recipe) ---
# # # class Recipe(BaseModel):
# # #     __tablename__ = 'recipes'
# # #
# # #     title = db.Column(db.String, nullable=False)  # שם המתכון (חובה לוגית, למרות שלא צוין בטבלה, חייב כותרת)
# # #     image_path = db.Column(db.String)  # הנתיב לתמונה המקורית [cite: 39]
# # #     # נתיבים ל-3 תמונות וריאציה (שחור לבן וכו'). נשמר כ-JSON [cite: 39]
# # #     variation_paths = db.Column(db.String)
# # #
# # #     recipe_type = db.Column(
# # #         db.String)  # Dairy, Meat, Parve [cite: 39] (נקרא type בדרישות, עדיף שם אחר כי type שמורה בפייתון)
# # #     instructions = db.Column(db.Text, nullable=False)  # טקסט ארוך, חובה למלא
# # #     # קשר לטבלת הרכיבים (One-to-Many) [cite: 37]
# # #     ingredients = db.relationship('IngredientEntry', backref='recipe', lazy=True)
# # #     # קישור למשתמש שהעלה את המתכון (Foreign Key)
# # #     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
# # #
# # #     # הוספה של שדה ה-is_deleted כפי שמופיע ב-Routes
# # #     is_deleted = db.Column(db.Boolean, default=False)
# # #     # פונקציות עזר לטיפול ב-JSON של התמונות
# # #     def set_variations(self, paths_list):
# # #         self.variation_paths = json.dumps(paths_list)
# # #
# # #     def get_variations(self):
# # #         return json.loads(self.variation_paths) if self.variation_paths else []
# # #
# # #
# # # # --- מחלקת רכיב (IngredientEntry) ---
# # # class IngredientEntry(BaseModel):
# # #     __tablename__ = 'ingredients'
# # #
# # #     product = db.Column(db.String, nullable=False)  # שם הרכיב [cite: 39]
# # #     amount = db.Column(db.Float, nullable=False)  # כמות עשרונית [cite: 39]
# # #     unit = db.Column(db.String, nullable=False)  # יחידת מידה [cite: 39]
# # #     # המפתח הזר שמקשר למתכון
# # #     recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
# # from flask_sqlalchemy import SQLAlchemy
# # import json
# #
# # db = SQLAlchemy()
# #
# # # טבלה מקשרת למועדפים (ללא מודל, רק טבלה)
# # favorites_table = db.Table('favorites',
# #                            db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
# #                            db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
# #                            )
# #
# #
# # class BaseModel(db.Model):
# #     __abstract__ = True
# #     id = db.Column(db.Integer, primary_key=True)
# #
# #     def save(self):
# #         db.session.add(self)
# #         db.session.commit()
# #
# #
# # class User(BaseModel):
# #     __tablename__ = 'users'
# #     username = db.Column(db.String(80), nullable=False)
# #     email = db.Column(db.String, unique=True, nullable=False)
# #     password = db.Column(db.String, nullable=False)
# #     role = db.Column(db.String, default='Reader')
# #     is_approved_uploader = db.Column(db.Boolean, default=False)
# #     has_requested_upgrade = db.Column(db.Boolean, default=False)
# #
# #     # קשר למועדפים: יאפשר לנו לגשת ל-user.favorite_recipes
# #     favorite_recipes = db.relationship('Recipe', secondary=favorites_table, backref='favorited_by')
# #
# #
# # class Recipe(BaseModel):
# #     __tablename__ = 'recipes'
# #     title = db.Column(db.String, nullable=False)
# #     image_path = db.Column(db.String)
# #     variation_paths = db.Column(db.String)
# #     recipe_type = db.Column(db.String)
# #     instructions = db.Column(db.Text, nullable=False)
# #     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
# #     is_deleted = db.Column(db.Boolean, default=False)
# #
# #     ingredients = db.relationship('IngredientEntry', backref='recipe', lazy=True)
# #     # קשר לדירוגים
# #     ratings = db.relationship('Rating', backref='recipe', lazy=True)
# #
# #     # פונקציה לחישוב ממוצע דירוג
# #     @property
# #     def average_rating(self):
# #         if not self.ratings:
# #             return 0
# #         total = sum([r.score for r in self.ratings])
# #         return round(total / len(self.ratings), 1)
# #
# #
# # class Rating(BaseModel):
# #     __tablename__ = 'ratings'
# #     score = db.Column(db.Integer, nullable=False)  # 1-5
# #     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
# #     recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
# #
# #
# # class IngredientEntry(BaseModel):
# #     __tablename__ = 'ingredients'
# #     product = db.Column(db.String, nullable=False)
# #     amount = db.Column(db.Float, nullable=False)
# #     unit = db.Column(db.String, nullable=False)
# #     recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
# from flask_sqlalchemy import SQLAlchemy
# import json
# # # # יצירת אובייקט ה-DB (יוזם את הקשר למסד הנתונים)
# db = SQLAlchemy()
#
# # טבלה מקשרת למועדפים (Many-to-Many)
# favorites_table = db.Table('favorites',
#                            db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
#                            db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
#                            )
#
# # # # --- מחלקת הבסיס (BaseModel) ---
# # # # דרישה: מורישה את id ואת מתודת save לכל המחלקות [cite: 37]
# class BaseModel(db.Model):
#     __abstract__ = True# אומר ל-SQLAlchemy לא ליצור טבלה למחלקה הזו, היא רק להורשה
#     id = db.Column(db.Integer, primary_key=True) # מזהה ייחודי [cite: 39]
#     #  דרישה: מתודת save הממירה אובייקט לשורה ב-DB
#     def save(self):
#         """שמירה פיזית למסד הנתונים"""
#         db.session.add(self)
#         db.session.commit()
#
# # # # --- מחלקת משתמש (User) ---
# class User(BaseModel): # יורש מ-BaseModel
#     __tablename__ = 'users'
#     username = db.Column(db.String(80), nullable=False)
#     email = db.Column(db.String, unique=True, nullable=False) # לא יכולות להיות 2 כתובות זהות [cite: 39]
#     password = db.Column(db.String, nullable=False)
#     role = db.Column(db.String, default='Reader')  # Admin, Uploader, Reader
#     is_approved_uploader = db.Column(db.Boolean, default=False)# האם המנהל אישר [cite: 39]
#     has_requested_upgrade = db.Column(db.Boolean, default=False)#הגיש בקשה
#     # קשר למועדפים
#     # favorite_recipes = db.relationship('Recipe', secondary=favorites_table, backref='favorited_by')
#
#
# class Recipe(BaseModel):
#     __tablename__ = 'recipes'
#     title = db.Column(db.String, nullable=False)
#     image_path = db.Column(db.String)
#     variation_paths = db.Column(db.String)
#     recipe_type = db.Column(db.String)  # חלבי, בשרי, פרווה
#     instructions = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     is_deleted = db.Column(db.Boolean, default=False)
#
#     # --- שדות חדשים לסינון ומיון מקצועי ---
#     prep_time = db.Column(db.Integer, default=0)  # זמן הכנה בדקות
#     avg_rating = db.Column(db.Float, default=0.0)  # שמירת הממוצע לביצועים מהירים
#
#     # ingredients = db.relationship('IngredientEntry', backref='recipe', lazy=True, cascade="all, delete-orphan")
#     # ratings = db.relationship('Rating', backref='recipe', lazy=True, cascade="all, delete-orphan")
#
#     # def update_avg_rating(self):
#     #     """מחשבת מחדש את הממוצע ומעדכנת את העמודה בשביל המיון בגלריה"""
#     #     if not self.ratings:
#     #         self.avg_rating = 0
#     #     else:
#     #         total = sum([r.score for r in self.ratings])
#     #         self.avg_rating = round(total / len(self.ratings), 1)
#     #     self.save()
#
#
# class Rating(BaseModel):
#     __tablename__ = 'ratings'
#     score = db.Column(db.Integer, nullable=False)  # 1-5
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
#
# class IngredientEntry(BaseModel):
#     __tablename__ = 'ingredients'
#     product = db.Column(db.String, nullable=False)
#     amount = db.Column(db.Float, nullable=False)
#     unit = db.Column(db.String, nullable=False)
#     recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

from flask_sqlalchemy import SQLAlchemy
import json

# # # יצירת אובייקט ה-DB (יוזם את הקשר למסד הנתונים)
db = SQLAlchemy()

# טבלה מקשרת למועדפים (Many-to-Many)
favorites_table = db.Table('favorites',
                           db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                           db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
                           )


# # # --- מחלקת הבסיס (BaseModel) ---
# # # דרישה: מורישה את id ואת מתודת save לכל המחלקות [cite: 37]
class BaseModel(db.Model):
    __abstract__ = True  # אומר ל-SQLAlchemy לא ליצור טבלה למחלקה הזו, היא רק להורשה
    id = db.Column(db.Integer, primary_key=True)  # מזהה ייחודי [cite: 39]

    # דרישה: מתודת save הממירה אובייקט לשורה ב-DB
    def save(self):
        # """שמירה פיזית למסד הנתונים """
        db.session.add(self)
        db.session.commit()


# # # --- מחלקת משתמש (User) ---
class User(BaseModel):  # יורש מ-BaseModel
    __tablename__ = 'users'
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)  # לא יכולות להיות 2 כתובות זהות [cite: 39]
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default='Reader')  # Admin, Uploader, Reader
    is_approved_uploader = db.Column(db.Boolean, default=False)  # האם המנהל אישר [cite: 39]
    has_requested_upgrade = db.Column(db.Boolean, default=False)  # הגיש בקשה
    favorite_recipes = db.relationship('Recipe', secondary=favorites_table, backref='favorited_by')  # קשר למועדפים


class Recipe(BaseModel):
    __tablename__ = 'recipes'
    title = db.Column(db.String, nullable=False)
    image_path = db.Column(db.String)
    variation_paths = db.Column(db.String)
    recipe_type = db.Column(db.String)  # חלבי, בשרי, פרווה
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)

    # --- שדות חדשים לסינון ומיון מקצועי ---
    prep_time = db.Column(db.Integer, default=0)  # זמן הכנה בדקות
    avg_rating = db.Column(db.Float, default=0.0)  # שמירת הממוצע לביצועים מהירים

    ingredients = db.relationship('IngredientEntry', backref='recipe', lazy=True, cascade="all, delete-orphan")
    ratings = db.relationship('Rating', backref='recipe', lazy=True, cascade="all, delete-orphan")

    def update_avg_rating(self):
        # """מחשבת מחדש את הממוצע ומעדכנת את העמודה בשביל המיון בגלריה"""
        if not self.ratings:
            self.avg_rating = 0
        else:
            total = sum([r.score for r in self.ratings])
            self.avg_rating = round(total / len(self.ratings), 1)
        self.save()


class Rating(BaseModel):
    __tablename__ = 'ratings'
    score = db.Column(db.Integer, nullable=False)  # 1-5
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)


class IngredientEntry(BaseModel):
    __tablename__ = 'ingredients'
    product = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
