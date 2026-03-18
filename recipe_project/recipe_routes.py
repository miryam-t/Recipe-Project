# # # # # # # import os
# # # # # # # import uuid
# # # # # # # import json
# # # # # # # from flask import Blueprint, request, jsonify, current_app
# # # # # # # from werkzeug.utils import secure_filename  # חשוב לאבטחת שמות קבצים
# # # # # # # from PIL import Image, ImageEnhance, ImageFilter
# # # # # # # # from PIL import Image
# # # # # # # from models import Recipe, db, User, Rating # הניחי ש-db מיובא מ-models או מהקובץ הראשי
# # # # # # # from decorators import role_required, get_current_user
# # # # # # # from models import Recipe, IngredientEntry
# # # # # # #
# # # # # # # # from models import Recipe, User, Rating, db
# # # # # # # from flask_jwt_extended import jwt_required, get_jwt_identity
# # # # # # # from flask import send_from_directory
# # # # # # #
# # # # # # #
# # # # # # # # 1. הגדרת ה-Blueprint
# # # # # # # # כל הנתיבים בקובץ זה יתחילו בקידומת /recipes
# # # # # # # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# # # # # # #
# # # # # # #
# # # # # # # def allowed_file(filename):
# # # # # # #     """בדיקה שהקובץ הוא תמונה (סיומת תקינה)"""
# # # # # # #     ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# # # # # # #     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# # # # # # #
# # # # # # #
# # # # # # # def apply_sepia(img):
# # # # # # #     """פונקציה שמקבלת אובייקט Image ומחזירה אותו בגווני ספיה"""
# # # # # # #     width, height = img.size
# # # # # # #     # המרה ל-RGB כדי להבטיח שיש 3 ערוצי צבע
# # # # # # #     img = img.convert("RGB")
# # # # # # #     pixels = img.load()
# # # # # # #
# # # # # # #     for x in range(width):
# # # # # # #         for y in range(height):
# # # # # # #             r, g, b = pixels[x, y]
# # # # # # #             # נוסחה מתמטית סטנדרטית לעיבוד ספיה
# # # # # # #             tr = int(0.393 * r + 0.769 * g + 0.189 * b)
# # # # # # #             tg = int(0.349 * r + 0.686 * g + 0.168 * b)
# # # # # # #             tb = int(0.272 * r + 0.534 * g + 0.131 * b)
# # # # # # #
# # # # # # #             # וידוא שהערכים לא עוברים את 255
# # # # # # #             pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
# # # # # # #     return img
# # # # # # #
# # # # # # # @recipes_bp.route('/add', methods=['POST'])
# # # # # # # @role_required('Uploader')  # רק משתמש שאושר כ-Uploader או Admin יכול להעלות [cite: 15, 80]
# # # # # # # def add_recipe():
# # # # # # #     """
# # # # # # #     נתיב להוספת מתכון חדש.
# # # # # # #     כולל העלאת תמונה, יצירת 3 וריאציות, ושמירת פרטים ב-DB.
# # # # # # #     """
# # # # # # #
# # # # # # #     try:
# # # # # # #         # --- שלב 1: בדיקת קובץ תמונה ---
# # # # # # #         if 'image' not in request.files:
# # # # # # #             return jsonify({"message": "No image part in the request"}), 400
# # # # # # #
# # # # # # #         file = request.files['image']
# # # # # # #
# # # # # # #         if file.filename == '' or not allowed_file(file.filename):
# # # # # # #             return jsonify({"message": "No selected file or invalid file type"}), 400
# # # # # # #
# # # # # # #         # --- שלב 2: הכנת התיקייה והשמות ---
# # # # # # #         # שימוש בתיקייה המוגדרת בקונפיגורציה של האפליקציה (או ברירת מחדל 'uploads')
# # # # # # #         upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# # # # # # #         if not os.path.exists(upload_folder):
# # # # # # #             os.makedirs(upload_folder)
# # # # # # #
# # # # # # #         # יצירת שם ייחודי למניעת דריסת קבצים [cite: 69]
# # # # # # #         unique_id = str(uuid.uuid4())
# # # # # # #         # ניקוי שם הקובץ המקורי מתווים מסוכנים
# # # # # # #         safe_filename = secure_filename(file.filename)
# # # # # # #         extension = safe_filename.rsplit('.', 1)[1].lower()
# # # # # # #
# # # # # # #         # בניית השם לקובץ המקורי
# # # # # # #         original_filename = f"{unique_id}_original.{extension}"
# # # # # # #         original_path = os.path.join(upload_folder, original_filename)
# # # # # # #
# # # # # # #         # --- שלב 3: שמירה ועיבוד תמונה (Pillow) ---
# # # # # # #         file.save(original_path)  # שמירת המקור בדיסק
# # # # # # #
# # # # # # #         img = Image.open(original_path)
# # # # # # #         variation_paths = []  # רשימה לשמירת נתיבי הווריאציות [cite: 66]
# # # # # # #
# # # # # # #         # וריאציה 1: שחור-לבן (Black & White) [cite: 64]
# # # # # # #         bw_filename = f"{unique_id}_bw.{extension}"
# # # # # # #         bw_path = os.path.join(upload_folder, bw_filename)
# # # # # # #         img.convert('L').save(bw_path)
# # # # # # #         variation_paths.append(bw_filename)  # שומרים רק את שם הקובץ, לא את הנתיב המלא
# # # # # # #
# # # # # # #         # וריאציה 3: שיפור חדות וצבע (Vivid) - גורם לאוכל להיראות מגרה
# # # # # # #         from PIL import ImageEnhance
# # # # # # #         vivid_filename = f"{unique_id}_vivid.{extension}"
# # # # # # #         vivid_path = os.path.join(upload_folder, vivid_filename)
# # # # # # #         # שיפור צבע (Color) פי 1.5
# # # # # # #         enhancer = ImageEnhance.Color(img.copy())
# # # # # # #         vivid_img = enhancer.enhance(1.5)
# # # # # # #         vivid_img.save(vivid_path)
# # # # # #
# # # # # # import os
# # # # # # import uuid
# # # # # # import json
# # # # # # from flask import Blueprint, request, jsonify, current_app, send_from_directory
# # # # # # from werkzeug.utils import secure_filename  # הגנה על שמות קבצים מפני תווים מסוכנים
# # # # # # from PIL import Image, ImageEnhance, ImageFilter  # ספריית Pillow לעיבוד תמונה
# # # # # # from models import Recipe, db, User, Rating, IngredientEntry  # ייבוא המודלים שלנו
# # # # # # from decorators import role_required, get_current_user  # דקורטורים לאבטחה והרשאות
# # # # # # from flask_jwt_extended import jwt_required, get_jwt_identity
# # # # # # import os
# # # # # # import json
# # # # # # from flask import Blueprint, request, jsonify, current_app
# # # # # # from flask_jwt_extended import jwt_required, get_jwt_identity
# # # # # # from werkzeug.utils import secure_filename
# # # # # # from PIL import Image, ImageFilter, ImageOps  # ייבוא מחלקות לעיבוד תמונה
# # # # # # # ייבוא המודלים שלנו (ודאי שהשמות תואמים לקובץ models.py שלך)
# # # # # # # from models import db, Recipe, IngredientEntry, Ingredient, User
# # # # # # # --- הגדרת ה-Blueprint ---
# # # # # # # Blueprint מאפשר לנו לחלק את האפליקציה לקבצים נפרדים לפי נושאים (מודולריות)
# # # # # # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# # # # # #
# # # # # #
# # # # # #
# # # # # # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# # # # # #
# # # # # #
# # # # # #
# # # # # # def allowed_file(filename):
# # # # # #     """פונקציית עזר לבדיקת סיומת הקובץ - אבטחה בסיסית לוודא שזו תמונה"""
# # # # # #     ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# # # # # #     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# # # # # #
# # # # # #
# # # # # # def apply_sepia(img):
# # # # # #     """
# # # # # #     עיבוד תמונה ידני: מעבר על פיקסלים ושינוי ערכי RGB למראה נוסטלגי (ספיה).
# # # # # #     זו רמה גבוהה של תכנות כי היא משתמשת בלוגיקה מתמטית על נתונים גולמיים.
# # # # # #     """
# # # # # #     width, height = img.size
# # # # # #     img = img.convert("RGB")
# # # # # #     pixels = img.load()
# # # # # #
# # # # # #     for x in range(width):
# # # # # #         for y in range(height):
# # # # # #             r, g, b = pixels[x, y]
# # # # # #             # נוסחה למראה ספיה
# # # # # #             tr = int(0.393 * r + 0.769 * g + 0.189 * b)
# # # # # #             tg = int(0.349 * r + 0.686 * g + 0.168 * b)
# # # # # #             tb = int(0.272 * r + 0.534 * g + 0.131 * b)
# # # # # #             pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
# # # # # #     return img
# # # # # #
# # # # # #
# # # # # # # --- נתיב הוספת מתכון ---
# # # # # # @recipes_bp.route('/add', methods=['POST'])
# # # # # # @role_required('Uploader')  # דקורטור שמוודא שרק משתמש עם הרשאה מתאימה יכול להיכנס
# # # # # # def add_recipe():
# # # # # #     try:
# # # # # #         # בדיקה שהבקשה מכילה קובץ תמונה
# # # # # #         if 'image' not in request.files:
# # # # # #             return jsonify({"message": "לא נשלחה תמונה בבקשה"}), 400
# # # # # #
# # # # # #         file = request.files['image']
# # # # # #         if file.filename == '' or not allowed_file(file.filename):
# # # # # #             return jsonify({"message": "קובץ לא תקין או סיומת אסורה"}), 400
# # # # # #
# # # # # #         # הכנת נתיב השמירה בשרת
# # # # # #         upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# # # # # #         if not os.path.exists(upload_folder):
# # # # # #             os.makedirs(upload_folder)
# # # # # #
# # # # # #         # יצירת מזהה ייחודי (UUID) כדי למנוע דריסת קבצים עם שמות זהים
# # # # # #         unique_id = str(uuid.uuid4())
# # # # # #         safe_filename = secure_filename(file.filename)
# # # # # #         extension = safe_filename.rsplit('.', 1)[1].lower()
# # # # # #         original_filename = f"{unique_id}_original.{extension}"
# # # # # #         original_path = os.path.join(upload_folder, original_filename)
# # # # # #
# # # # # #         # שמירת התמונה המקורית בדיסק
# # # # # #         file.save(original_path)
# # # # # #
# # # # # #         # פתיחת התמונה עם Pillow לצורך עיבוד וריאציות
# # # # # #         img = Image.open(original_path)
# # # # # #         variation_paths = []
# # # # # #
# # # # # #         # וריאציה 1: שחור-לבן (L = Luminance)
# # # # # #         bw_filename = f"{unique_id}_bw.{extension}"
# # # # # #         img.convert('L').save(os.path.join(upload_folder, bw_filename))
# # # # # #         variation_paths.append(bw_filename)
# # # # # #
# # # # # #         # וריאציה 2: צבעים עזים (Vivid) - עוזר לאוכל להיראות מגרה יותר
# # # # # #         vivid_filename = f"{unique_id}_vivid.{extension}"
# # # # # #         enhancer = ImageEnhance.Color(img.copy())
# # # # # #         vivid_img = enhancer.enhance(1.5)  # הגברת רוויית הצבע ב-50%
# # # # # #         vivid_img.save(os.path.join(upload_folder, vivid_filename))
# # # # # #         variation_paths.append(vivid_filename)
# # # # # #
# # # # # #         # וריאציה 3: ספיה (שימוש בפונקציה שכתבנו למעלה)
# # # # # #         sepia_filename = f"{unique_id}_sepia.{extension}"
# # # # # #         sepia_img = apply_sepia(img.copy())
# # # # # #         sepia_img.save(os.path.join(upload_folder, sepia_filename))
# # # # # #         variation_paths.append(sepia_filename)
# # # # # #
# # # # # #         # שליפת נתוני הטופס (Multipart Form Data)
# # # # # #         title = request.form.get('title')
# # # # # #         instructions = request.form.get('instructions')
# # # # # #         recipe_type = request.form.get('type')
# # # # # #         prep_time = int(request.form.get('prep_time', 0))
# # # # # #         current_user = get_current_user()
# # # # # #
# # # # # #         # יצירת אובייקט המתכון בבסיס הנתונים
# # # # # #         new_recipe = Recipe(
# # # # # #             title=title,
# # # # # #             instructions=instructions,
# # # # # #             recipe_type=recipe_type,
# # # # # #             image_path=original_filename,
# # # # # #             # המרת רשימת הנתיבים לטקסט JSON כדי שיוכל להישמר ב-DB
# # # # # #             variation_paths=json.dumps(variation_paths),
# # # # # #             user_id=current_user.id,
# # # # # #             prep_time=prep_time,
# # # # # #             avg_rating=0.0
# # # # # #         )
# # # # # #         new_recipe.save()
# # # # # #
# # # # # #         # שמירת הרכיבים (Ingredients) המקושרים למתכון
# # # # # #         ingredients_data = request.form.get('ingredients')
# # # # # #         if ingredients_data:
# # # # # #             ingredients_list = json.loads(ingredients_data)  # המרה ממחרוזת JSON לרשימת פייתון
# # # # # #             for ing in ingredients_list:
# # # # # #                 new_ingredient = IngredientEntry(
# # # # # #                     product=ing.get('product'),
# # # # # #                     amount=float(ing.get('amount')),
# # # # # #                     unit=ing.get('unit'),
# # # # # #                     recipe_id=new_recipe.id  # קישור למתכון החדש
# # # # # #                 )
# # # # # #                 new_ingredient.save()
# # # # # #
# # # # # #         return jsonify({"message": "המתכון נוסף בהצלחה!", "recipe_id": new_recipe.id}), 201
# # # # # #     except Exception as e:
# # # # # #         return jsonify({"message": "שגיאה בתהליך השמירה", "error": str(e)}), 500
# # # # # #
# # # # # #
# # # # # # # --- שליפת כל המתכונים ---
# # # # # # @recipes_bp.route('/all', methods=['GET'])
# # # # # # def get_all_recipes():
# # # # # #     # סינון מתכונים שלא נמחקו (מחיקה לוגית)
# # # # # #     recipes = Recipe.query.filter_by(is_deleted=False).all()
# # # # # #     output = []
# # # # # #     for r in recipes:
# # # # # #         output.append({
# # # # # #             "id": r.id,
# # # # # #             "title": r.title,
# # # # # #             "image": r.image_path,
# # # # # #             "recipe_type": r.recipe_type,
# # # # # #             "prep_time": r.prep_time,
# # # # # #             "avg_rating": r.avg_rating,
# # # # # #             "variations": json.loads(r.variation_paths) if r.variation_paths else []
# # # # # #         })
# # # # # #     return jsonify(output), 200
# # # # # #
# # # # # #
# # # # # # # --- חיפוש חכם לפי רכיבים ---
# # # # # # @recipes_bp.route('/search', methods=['POST'])
# # # # # # def search_recipes():
# # # # # #     """
# # # # # #     אלגוריתם חיפוש המבוסס על תורת הקבוצות (Sets).
# # # # # #     מחשב אחוזי התאמה בין המצרכים שיש למשתמש למצרכים במתכון.
# # # # # #     """
# # # # # #     data = request.json
# # # # # #     user_ingredients_list = data.get('ingredients', [])
# # # # # #     # ניקוי רווחים והמרת רשימת המשתמש ל-Set לחיפוש מהיר
# # # # # #     user_set = {i.strip().lower() for i in user_ingredients_list if i}
# # # # # #
# # # # # #     all_recipes = Recipe.query.filter_by(is_deleted=False).all()
# # # # # #     results = []
# # # # # #
# # # # # #     for recipe in all_recipes:
# # # # # #         # יצירת Set של רכיבי המתכון הנוכחי
# # # # # #         recipe_set = {ing.product.strip().lower() for ing in recipe.ingredients if ing.product}
# # # # # #         if not recipe_set: continue
# # # # # #
# # # # # #         # מציאת הרכיבים המשותפים (Intersection)
# # # # # #         common_ingredients = user_set & recipe_set
# # # # # #         # חישוב ציון התאמה (כמה אחוזים מהמתכון יש לי במקרר)
# # # # # #         score = len(common_ingredients) / len(recipe_set)
# # # # # #
# # # # # #         if score >= 0.1:  # החזרת תוצאות רק עם התאמה של מעל 10%
# # # # # #             results.append({
# # # # # #                 "id": recipe.id,
# # # # # #                 "title": recipe.title,
# # # # # #                 "score": round(score * 100, 2),
# # # # # #                 "image": recipe.image_path,
# # # # # #                 "missing_ingredients": list(recipe_set - user_set)  # מה עוד צריך לקנות
# # # # # #             })
# # # # # #
# # # # # #     # מיון התוצאות מהמתכון הכי מתאים להכי פחות מתאים
# # # # # #     results.sort(key=lambda x: x['score'], reverse=True)
# # # # # #     return jsonify(results), 200
# # # # # #
# # # # # #
# # # # # # # --- דירוג מתכון ---
# # # # # # @recipes_bp.route('/rate/<int:recipe_id>', methods=['POST'])
# # # # # # @jwt_required()
# # # # # # def rate_recipe(recipe_id):
# # # # # #     """נתיב המאפשר למשתמש רשום לדרג מתכון ולעדכן את הממוצע שלו"""
# # # # # #     current_user_id = get_jwt_identity()
# # # # # #     data = request.json
# # # # # #     score = data.get('score')
# # # # # #
# # # # # #     if not score or not (1 <= score <= 5):
# # # # # #         return jsonify({"message": "דירוג חייב להיות בין 1 ל-5"}), 400
# # # # # #
# # # # # #     recipe = Recipe.query.get_or_404(recipe_id)
# # # # # #     # בדיקה אם המשתמש כבר דירג בעבר - עדכון או יצירה חדשה
# # # # # #     rating = Rating.query.filter_by(user_id=current_user_id, recipe_id=recipe_id).first()
# # # # # #     if rating:
# # # # # #         rating.score = score
# # # # # #     else:
# # # # # #         rating = Rating(user_id=current_user_id, recipe_id=recipe_id, score=score)
# # # # # #
# # # # # #     rating.save()
# # # # # #     recipe.update_avg_rating()  # פונקציה במודל שמחשבת ממוצע חדש
# # # # # #     return jsonify({"message": "הדירוג נשמר", "new_average": recipe.avg_rating}), 200
# # # # # #
# # # # # #
# # # # # # # --- הגשת קבצי תמונות (Static Files) ---
# # # # # # @recipes_bp.route('/file/<filename>')
# # # # # # def serve_recipe_image(filename):
# # # # # #     """מאפשר גישה ישירה לתמונות מהדפדפן (ללא צורך בטוקן)"""
# # # # # #     upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# # # # # #     return send_from_directory(upload_folder, filename)
# # # # # # # ----------מתכון יחיד------------
# # # # # # # --- נתיב לקבלת מתכון יחיד לפי ID ---
# # # # # # @recipes_bp.route('/<int:recipe_id>', methods=['GET'])
# # # # # # def get_single_recipe(recipe_id):
# # # # # #     # שליפת המתכון או החזרת שגיאה 404 אם לא נמצא
# # # # # #     recipe = Recipe.query.get_or_404(recipe_id)
# # # # # #
# # # # # #     # בניית רשימת הרכיבים בצורה מסודרת
# # # # # #     # ההנחה היא שיש לך טבלת קשר (IngredientEntry) שמחברת בין מתכון לרכיב
# # # # # #     ingredients_list = []
# # # # # #     for entry in recipe.ingredients:
# # # # # #         ingredients_list.append({
# # # # # #             "name": entry.ingredient.name,  # השם מתוך טבלת Ingredients
# # # # # #             "amount": entry.amount,
# # # # # #             "unit": entry.unit
# # # # # #         })
# # # # # #
# # # # # #     # --- לוגיקת התמונות ---
# # # # # #     # נבנה את כתובת ה-URL הבסיסית של השרת כדי שהאנגולר יוכל להציג את התמונה
# # # # # #     # request.host_url יחזיר למשל: http://127.0.0.1:5000/
# # # # # #     base_image_url = request.host_url + 'uploads/'
# # # # # #
# # # # # #     # שם הקובץ המקורי שנשמר במסד הנתונים (למשל: pizza.jpg)
# # # # # #     filename = recipe.image_filename
# # # # # #
# # # # # #     # פיצול שם הקובץ כדי להוסיף את הסיומות לווריאציות
# # # # # #     # אם הקובץ הוא 'cake.jpg', אז name='cake' ו-ext='.jpg'
# # # # # #     name, ext = os.path.splitext(filename)
# # # # # #
# # # # # #     # יצירת מילון שמכיל את כל הנתונים שהאנגולר צריך
# # # # # #     response = {
# # # # # #         "id": recipe.id,
# # # # # #         "title": recipe.title,
# # # # # #         "description": recipe.description,  # אם יש לך שדה תיאור
# # # # # #         "instructions": recipe.instructions,
# # # # # #         "prep_time": recipe.prep_time,  # זמן הכנה (אם קיים במודל)
# # # # # #         "servings": recipe.servings,  # מספר מנות (אם קיים במודל)
# # # # # #         "ingredients": ingredients_list,
# # # # # #         "author": recipe.author.username,  # שם המשתמש שהעלה את המתכון
# # # # # #
# # # # # #         # --- אובייקט הגלריה ---
# # # # # #         "images": {
# # # # # #             "original": base_image_url + filename,
# # # # # #             "black_white": base_image_url + f"{name}_bw{ext}",
# # # # # #             "rotated": base_image_url + f"{name}_rotated{ext}",
# # # # # #             "special_effect": base_image_url + f"{name}_effect{ext}"
# # # # # #         }
# # # # # #     }
# # # # # #
# # # # # #     return jsonify(response), 200
# # # # # #
# # # # # #
# # # # # # # # --- נתיב העלאת מתכון חדש (כולל עיבוד תמונות) ---
# # # # # # # @recipes_bp.route('/add', methods=['POST'])
# # # # # # # @jwt_required()  # חובה: רק משתמש רשום יכול להעלות
# # # # # # # def add_recipe():
# # # # # # #     # 1. זיהוי המשתמש המעלה
# # # # # # #     current_user_id = get_jwt_identity()
# # # # # # #     user = User.query.get(current_user_id)
# # # # # # #
# # # # # # #     # בדיקת הרשאות (אופציונלי: אם את רוצה שרק 'Uploader' יעלה)
# # # # # # #     # if not user.is_approved_uploader:
# # # # # # #     #     return jsonify({"message": "אין לך הרשאה להעלות מתכונים"}), 403
# # # # # # #
# # # # # # #     # 2. בדיקה שנשלח קובץ תמונה
# # # # # # #     if 'image' not in request.files:
# # # # # # #         return jsonify({"message": "חובה להעלות תמונה"}), 400
# # # # # # #
# # # # # # #     file = request.files['image']
# # # # # # #     if file.filename == '':
# # # # # # #         return jsonify({"message": "לא נבחר קובץ"}), 400
# # # # # # #
# # # # # # #     # 3. שמירת התמונה המקורית ועיבוד וריאציות עם Pillow
# # # # # # #     if file:
# # # # # # #         # ניקוי שם הקובץ למניעת פרצות אבטחה
# # # # # # #         filename = secure_filename(file.filename)
# # # # # # #         # שימוש בתיקיית ה-uploads שהוגדרה ב-app.py
# # # # # # #         upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# # # # # # #
# # # # # # #         # ודאי שהתיקייה קיימת
# # # # # # #         os.makedirs(upload_folder, exist_ok=True)
# # # # # # #
# # # # # # #         # שמירת המקור
# # # # # # #         original_path = os.path.join(upload_folder, filename)
# # # # # # #         file.save(original_path)
# # # # # # #
# # # # # # #         # --- יצירת וריאציות (Pillow) ---
# # # # # # #         try:
# # # # # # #             # פתיחת התמונה לזיכרון לעיבוד
# # # # # # #             img = Image.open(original_path)
# # # # # # #
# # # # # # #             # פיצול השם והסיומת (למשל pizza ו-.jpg)
# # # # # # #             name, ext = os.path.splitext(filename)
# # # # # # #
# # # # # # #             # וריאציה 1: שחור לבן (Black & White)
# # # # # # #             # 'L' מציין מצב Grayscale
# # # # # # #             img_bw = img.convert('L')
# # # # # # #             img_bw.save(os.path.join(upload_folder, f"{name}_bw{ext}"))
# # # # # # #
# # # # # # #             # וריאציה 2: מסובב (Rotated)
# # # # # # #             # סיבוב ב-90 מעלות נגד כיוון השעון
# # # # # # #             img_rotated = img.rotate(90, expand=True)
# # # # # # #             img_rotated.save(os.path.join(upload_folder, f"{name}_rotated{ext}"))
# # # # # # #
# # # # # # #             # וריאציה 3: אפקט מיוחד (Blur/Filter)
# # # # # # #             # הוספת פילטר טשטוש או הדגשת פרטים. כאן בחרנו ב-DETAIL
# # # # # # #             img_effect = img.filter(ImageFilter.DETAIL)
# # # # # # #             img_effect.save(os.path.join(upload_folder, f"{name}_effect{ext}"))
# # # # # # #
# # # # # # #         except Exception as e:
# # # # # # #             print(f"Error processing images: {e}")
# # # # # # #             return jsonify({"message": "שגיאה בעיבוד התמונות"}), 500
# # # # # # #
# # # # # # #         # 4. קריאת נתוני הטקסט (מגיעים ב-form-data)
# # # # # # #         try:
# # # # # # #             # יצירת אובייקט המתכון
# # # # # # #             new_recipe = Recipe(
# # # # # # #                 title=request.form['title'],
# # # # # # #                 description=request.form.get('description', ''),
# # # # # # #                 instructions=request.form['instructions'],
# # # # # # #                 prep_time=int(request.form.get('prep_time', 0)),
# # # # # # #                 servings=int(request.form.get('servings', 0)),
# # # # # # #                 image_filename=filename,  # שומרים רק את שם הקובץ המקורי
# # # # # # #                 user_id=user.id
# # # # # # #             )
# # # # # # #
# # # # # # #             db.session.add(new_recipe)
# # # # # # #             db.session.commit()  # שומרים כדי לקבל new_recipe.id
# # # # # # #
# # # # # # #             # 5. טיפול ברכיבים (Ingredients)
# # # # # # #             # ב-FormData רשימות מגיעות בדרך כלל כמחרוזת JSON
# # # # # # #             ingredients_json = request.form.get('ingredients')
# # # # # # #             if ingredients_json:
# # # # # # #                 ingredients_list = json.loads(ingredients_json)
# # # # # # #
# # # # # # #                 for item in ingredients_list:
# # # # # # #                     # item נראה ככה: {'name': 'קמח', 'amount': 500, 'unit': 'גרם'}
# # # # # # #
# # # # # # #                     # בדיקה אם הרכיב קיים במאגר הגלובלי, אם לא - יוצרים אותו
# # # # # # #                     # זה קריטי לחיפוש החכם שלך (Sets)!
# # # # # # #                     ing_obj = Ingredient.query.filter_by(name=item['name']).first()
# # # # # # #                     if not ing_obj:
# # # # # # #                         ing_obj = Ingredient(name=item['name'])
# # # # # # #                         db.session.add(ing_obj)
# # # # # # #                         db.session.commit()  # שומרים כדי לקבל id
# # # # # # #
# # # # # # #                     # יצירת הקישור בטבלת הקשר
# # # # # # #                     entry = IngredientEntry(
# # # # # # #                         recipe_id=new_recipe.id,
# # # # # # #                         ingredient_id=ing_obj.id,
# # # # # # #                         amount=item.get('amount', ''),
# # # # # # #                         unit=item.get('unit', '')
# # # # # # #                     )
# # # # # # #                     db.session.add(entry)
# # # # # # #
# # # # # # #             db.session.commit()  # שמירה סופית של הכל
# # # # # # #             return jsonify({"message": "המתכון הועלה בהצלחה!", "recipe_id": new_recipe.id}), 201
# # # # # # #
# # # # # # #         except Exception as e:
# # # # # # #             db.session.rollback()  # ביטול שינויים במקרה שגיאה
# # # # # # #             return jsonify({"message": f"שגיאה בשמירת הנתונים: {str(e)}"}), 500
# # # # # import os
# # # # # import json
# # # # # from flask import Blueprint, request, jsonify, current_app
# # # # # from flask_jwt_extended import jwt_required, get_jwt_identity
# # # # # from werkzeug.utils import secure_filename
# # # # # from PIL import Image, ImageFilter
# # # # # from models import db, User, Recipe, IngredientEntry, Rating
# # # # #
# # # # # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# # # # #
# # # # #
# # # # # # --- 1. הצגת מתכון בודד (החלק שהיה חסר) ---
# # # # # @recipes_bp.route('/<int:recipe_id>', methods=['GET'])
# # # # # def get_recipe(recipe_id):
# # # # #     recipe = Recipe.query.get_or_404(recipe_id)
# # # # #
# # # # #     # המרת נתוני הרכיבים לרשימה עבור האנגולר
# # # # #     ingredients_list = [{
# # # # #         "product": i.product,
# # # # #         "amount": i.amount,
# # # # #         "unit": i.unit
# # # # #     } for i in recipe.ingredients]
# # # # #
# # # # #     # טיפול בוריאציות (הפיכת מחרוזת ה-JSON חזרה למערך)
# # # # #     variations = json.loads(recipe.variation_paths) if recipe.variation_paths else []
# # # # #
# # # # #     # בניית התגובה לפי ה-Interface של האנגולר
# # # # #     return jsonify({
# # # # #         "id": recipe.id,
# # # # #         "title": recipe.title,
# # # # #         "instructions": recipe.instructions,
# # # # #         "recipe_type": recipe.recipe_type,
# # # # #         "image_path": recipe.image_path,
# # # # #         "variation_paths": variations,
# # # # #         "ingredients": ingredients_list,
# # # # #         "user_id": recipe.user_id,
# # # # #         "prep_time": recipe.prep_time,
# # # # #         "avg_rating": recipe.avg_rating
# # # # #     }), 200
# # # # #
# # # # #
# # # # # # --- 2. סימון מועדף (Toggle Favorite) ---
# # # # # @recipes_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
# # # # # @jwt_required()
# # # # # def toggle_favorite(recipe_id):
# # # # #     user_id = get_jwt_identity()
# # # # #     user = User.query.get(user_id)
# # # # #     recipe = Recipe.query.get_or_404(recipe_id)
# # # # #
# # # # #     if recipe in user.favorite_recipes:
# # # # #         user.favorite_recipes.remove(recipe)
# # # # #         message = "הוסר מהמועדפים"
# # # # #     else:
# # # # #         user.favorite_recipes.append(recipe)
# # # # #         message = "נוסף למועדפים"
# # # # #
# # # # #     db.session.commit()
# # # # #     return jsonify({"message": message, "is_favorite": recipe in user.favorite_recipes}), 200
# # # # #
# # # # #
# # # # # # --- 3. העלאת מתכון (מתוקן עם Pillow ושמות שדות תואמים) ---
# # # # # @recipes_bp.route('/add', methods=['POST'])
# # # # # @jwt_required()
# # # # # def add_recipe():
# # # # #     user_id = get_jwt_identity()
# # # # #
# # # # #     if 'image' not in request.files:
# # # # #         return jsonify({"message": "חסרה תמונה"}), 400
# # # # #
# # # # #     file = request.files['image']
# # # # #     filename = secure_filename(file.filename)
# # # # #     upload_folder = current_app.config['UPLOAD_FOLDER']
# # # # #     file_path = os.path.join(upload_folder, filename)
# # # # #     file.save(file_path)
# # # # #
# # # # #     # יצירת וריאציות עם Pillow
# # # # #     name, ext = os.path.splitext(filename)
# # # # #     variations = []
# # # # #
# # # # #     # דוגמה לוריאציה אחת (שחור לבן)
# # # # #     bw_path = f"{name}_bw{ext}"
# # # # #     with Image.open(file_path) as img:
# # # # #         img.convert('L').save(os.path.join(upload_folder, bw_path))
# # # # #         variations.append(bw_path)
# # # # #
# # # # #     # יצירת המתכון ב-DB
# # # # #     new_recipe = Recipe(
# # # # #         title=request.form['title'],
# # # # #         instructions=request.form['instructions'],
# # # # #         recipe_type=request.form['recipe_type'],
# # # # #         image_path=filename,
# # # # #         variation_paths=json.dumps(variations),  # שומרים כמחרוזת JSON
# # # # #         user_id=user_id,
# # # # #         prep_time=int(request.form.get('prep_time', 0))
# # # # #     )
# # # # #
# # # # #     db.session.add(new_recipe)
# # # # #     db.session.flush()  # מקבלים ID בלי לעשות commit סופי
# # # # #
# # # # #     # שמירת רכיבים
# # # # #     ing_data = json.loads(request.form['ingredients'])
# # # # #     for ing in ing_data:
# # # # #         new_ing = IngredientEntry(
# # # # #             product=ing['product'],
# # # # #             amount=ing['amount'],
# # # # #             unit=ing['unit'],
# # # # #             recipe_id=new_recipe.id
# # # # #         )
# # # # #         db.session.add(new_ing)
# # # # #
# # # # #     db.session.commit()
# # # # #     return jsonify({"message": "מתכון נוצר בהצלחה"}), 201
# # # # import os
# # # # import json
# # # # import uuid
# # # # from flask import Blueprint, request, jsonify, current_app
# # # # from flask_jwt_extended import jwt_required, get_jwt_identity
# # # # from werkzeug.utils import secure_filename
# # # # from PIL import Image, ImageFilter
# # # # from models import db, Recipe, IngredientEntry, User, Rating
# # # #
# # # # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# # # # # הנתיב שבו שמורות התמונות שלך (ודאי שזה תואם למה שהגדרת ב-config)
# # # # UPLOAD_FOLDER = 'uploads'
# # # #
# # # # # --- 1. הצגת כל המתכונים (גלריה) ---
# # # # @recipes_bp.route('/all', methods=['GET'])
# # # # def get_all_recipes():
# # # #     # שליפת כל המתכונים שלא נמחקו לוגית [cite: 24]
# # # #     recipes = Recipe.query.filter_by(is_deleted=False).all()
# # # #
# # # #     output = []
# # # #     for r in recipes:
# # # #         output.append({
# # # #             "id": r.id,
# # # #             "title": r.title,
# # # #             "image": r.image_path,
# # # #             "recipe_type": r.recipe_type,
# # # #             "prep_time": r.prep_time,
# # # #             "avg_rating": r.avg_rating
# # # #         })
# # # #     return jsonify(output), 200
# # # #
# # # #
# # # # # --- 2. הצגת מתכון יחיד (הדף החסר) ---
# # # # @recipes_bp.route('/<int:recipe_id>', methods=['GET'])
# # # # def get_single_recipe(recipe_id):
# # # #     recipe = Recipe.query.get_or_404(recipe_id)
# # # #
# # # #     # המרת רכיבים מרשימה לאובייקטים עבור האנגולר [cite: 39]
# # # #     ingredients = [{"product": i.product, "amount": i.amount, "unit": i.unit} for i in recipe.ingredients]
# # # #
# # # #     # טעינת נתיבי התמונות מפורמט JSON [cite: 39, 66]
# # # #     variations = json.loads(recipe.variation_paths) if recipe.variation_paths else []
# # # #
# # # #     return jsonify({
# # # #         "id": recipe.id,
# # # #         "title": recipe.title,
# # # #         "instructions": recipe.instructions,
# # # #         "recipe_type": recipe.recipe_type,
# # # #         "image_path": recipe.image_path,
# # # #         "variation_paths": variations,
# # # #         "ingredients": ingredients,
# # # #         "prep_time": recipe.prep_time,
# # # #         "avg_rating": recipe.avg_rating
# # # #     }), 200
# # # #
# # # #
# # # # # --- 3. העלאת מתכון חדש עם עיבוד תמונות (Pillow) ---
# # # # @recipes_bp.route('/add', methods=['POST'])
# # # # @jwt_required()
# # # # def add_recipe():
# # # #     user_id = get_jwt_identity()
# # # #     user = User.query.get(user_id)
# # # #
# # # #     # בדיקה שרק "משתמש תוכן" או מנהל יכול להעלות [cite: 7, 17]
# # # #     if user.role not in ['Admin', 'Uploader'] or not user.is_approved_uploader:
# # # #         return jsonify({"message": "Permission denied"}), 403
# # # #
# # # #     if 'image' not in request.files:
# # # #         return jsonify({"message": "No image uploaded"}), 400
# # # #
# # # #     file = request.files['image']
# # # #     unique_filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)  # שם ייחודי [cite: 69]
# # # #     file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
# # # #     file.save(file_path)
# # # #
# # # #     # --- עיבוד תמונות עם Pillow (דרישה: 3 וריאציות) [cite: 6, 64] ---
# # # #     variations = []
# # # #     with Image.open(file_path) as img:
# # # #         name, ext = os.path.splitext(unique_filename)
# # # #
# # # #         # 1. שחור-לבן
# # # #         bw_name = f"{name}_bw{ext}"
# # # #         img.convert('L').save(os.path.join(current_app.config['UPLOAD_FOLDER'], bw_name))
# # # #         variations.append(bw_name)
# # # #
# # # #         # 2. מסובב
# # # #         rotated_name = f"{name}_rotated{ext}"
# # # #         img.rotate(90).save(os.path.join(current_app.config['UPLOAD_FOLDER'], rotated_name))
# # # #         variations.append(rotated_name)
# # # #
# # # #         # 3. אפקט מיוחד (Blur)
# # # #         blur_name = f"{name}_blur{ext}"
# # # #         img.filter(ImageFilter.BLUR).save(os.path.join(current_app.config['UPLOAD_FOLDER'], blur_name))
# # # #         variations.append(blur_name)
# # # #
# # # #     # יצירת מופע המתכון [cite: 33]
# # # #     new_recipe = Recipe(
# # # #         title=request.form.get('title'),
# # # #         instructions=request.form.get('instructions'),
# # # #         recipe_type=request.form.get('recipe_type'),
# # # #         image_path=unique_filename,
# # # #         variation_paths=json.dumps(variations),  # שמירה כ-JSON
# # # #         user_id=user_id,
# # # #         prep_time=int(request.form.get('prep_time', 0))
# # # #     )
# # # #     new_recipe.save()  # שמירה ראשונית לקבלת ID
# # # #
# # # #     # שמירת רכיבים [cite: 37]
# # # #     ingredients_data = json.loads(request.form.get('ingredients', '[]'))
# # # #     for ing in ingredients_data:
# # # #         entry = IngredientEntry(
# # # #             product=ing['product'],
# # # #             amount=float(ing['amount']),
# # # #             unit=ing['unit'],
# # # #             recipe_id=new_recipe.id
# # # #         )
# # # #         db.session.add(entry)
# # # #
# # # #     db.session.commit()
# # # #     return jsonify({"message": "Recipe created successfully"}), 201
# # # #
# # # #
# # # # # --- 4. אלגוריתם חיפוש לפי רכיבים (שימוש ב-Set) ---
# # # # @recipes_bp.route('/search', methods=['POST'])
# # # # def search_by_ingredients():
# # # #     user_ingredients = set(request.json.get('ingredients', []))  # שלב 1: יצירת סטים [cite: 46]
# # # #     recipes = Recipe.query.filter_by(is_deleted=False).all()
# # # #
# # # #     results = []
# # # #     for r in recipes:
# # # #         recipe_ing_list = [i.product for i in r.ingredients]
# # # #         recipe_ing_set = set(recipe_ing_list)
# # # #
# # # #         # שלב 2: חיתוך (Intersection) [cite: 49]
# # # #         common = user_ingredients & recipe_ing_set
# # # #
# # # #         # שלב 3: חישוב ציון [cite: 53]
# # # #         if recipe_ing_set:
# # # #             score = (len(common) / len(recipe_ing_set)) * 100
# # # #
# # # #             if score >= 20:  # סינון מתחת ל-20% [cite: 57]
# # # #                 results.append({
# # # #                     "id": r.id,
# # # #                     "title": r.title,
# # # #                     "score": round(score, 1),
# # # #                     "image": r.image_path
# # # #                 })
# # # #
# # # #     # שלב 4: מיון לפי ציון יורד [cite: 58]
# # # #     results.sort(key=lambda x: x['score'], reverse=True)
# # # #     return jsonify(results), 200
# # # import os
# # # import json
# # # import uuid
# # # from flask import Blueprint, request, jsonify, current_app, send_from_directory
# # # from flask_jwt_extended import jwt_required, get_jwt_identity
# # # from werkzeug.utils import secure_filename
# # # from PIL import Image, ImageFilter
# # # from models import db, Recipe, IngredientEntry, User, Rating
# # #
# # # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# # #
# # #
# # # # --- פונקציית עזר להוספת הכתובת המלאה לתמונה ---
# # # # def get_full_url(filename):
# # #     # if not filename:
# # #         # return None
# # #     # מחזיר כתובת כמו http://127.0.0.1:5000/recipes/file/name.jpg
# # #     # return http://127.0.0.1:5000/ + 'uploads/'
# # #     # request.host_url יחזיר למשל: http://127.0.0.1:5000/
# # #
# # #
# # # base_image_url = request.host_url + 'uploads/'
# # #
# # # # --- 1. הגשת קבצי תמונות (זה מה שחוסר לך!) ---
# # # @recipes_bp.route('/file/<filename>')
# # # def serve_recipe_image(filename):
# # #     """מאפשר לדפדפן לגשת פיזית לקובץ התמונה בתיקיית uploads"""
# # #     upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# # #     return send_from_directory(upload_folder, filename)
# # #
# # #
# # # # --- 2. הצגת כל המתכונים (גלריה) ---
# # # @recipes_bp.route('/all', methods=['GET'])
# # # def get_all_recipes():
# # #     recipes = Recipe.query.filter_by(is_deleted=False).all()
# # #     output = []
# # #     for r in recipes:
# # #         output.append({
# # #             "id": r.id,
# # #             "title": r.title,
# # #             "image": get_full_url(r.image_path),  # שימוש בכתובת מלאה
# # #             "recipe_type": r.recipe_type,
# # #             "prep_time": r.prep_time,
# # #             "avg_rating": r.avg_rating
# # #         })
# # #     return jsonify(output), 200
# # #
# # #
# # # # --- 3. הצגת מתכון יחיד ---
# # # @recipes_bp.route('/<int:recipe_id>', methods=['GET'])
# # # def get_single_recipe(recipe_id):
# # #     recipe = Recipe.query.get_or_404(recipe_id)
# # #
# # #     ingredients = [{"product": i.product, "amount": i.amount, "unit": i.unit} for i in recipe.ingredients]
# # #
# # #     # טעינת וריאציות והפיכתן לכתובות URL מלאות
# # #     raw_variations = json.loads(recipe.variation_paths) if recipe.variation_paths else []
# # #     full_variations = [get_full_url(v) for v in raw_variations]
# # #
# # #     return jsonify({
# # #         "id": recipe.id,
# # #         "title": recipe.title,
# # #         "instructions": recipe.instructions,
# # #         "recipe_type": recipe.recipe_type,
# # #         "image_path": get_full_url(recipe.image_path),  # כתובת מלאה
# # #         "variation_paths": full_variations,  # רשימת כתובות מלאות
# # #         "ingredients": ingredients,
# # #         "prep_time": recipe.prep_time,
# # #         "avg_rating": recipe.avg_rating
# # #     }), 200
# # #
# # #
# # # # @app.route('/recipes/add', methods=['POST'])
# # # # def add_recipe():
# # # #     file = request.files['image']
# # # #     # יצירת שם ייחודי כפי שמוסבר בקובץ ה-Word
# # # #     unique_filename = f"{uuid.uuid4()}_{file.filename}"
# # # #
# # # #     # שמירה פיזית בתיקייה
# # # #     file.save(os.path.join('uploads', unique_filename))
# # # #
# # # #     # שמירה במסד הנתונים - כאן הדיוק חשוב!
# # # #     new_recipe = Recipe(
# # # #         title=request.form.get('title'),
# # # #         image=unique_filename,  # שומרים רק את שם הקובץ
# # # # --- 4. העלאת מתכון חדש (Pillow) ---
# # # @recipes_bp.route('/add', methods=['POST'])
# # # @jwt_required()
# # # def add_recipe():
# # #     user_id = get_jwt_identity()
# # #     user = User.query.get(user_id)
# # #
# # #     if user.role not in ['Admin', 'Uploader'] or not user.is_approved_uploader:
# # #         return jsonify({"message": "Permission denied"}), 403
# # #
# # #     if 'image' not in request.files:
# # #         return jsonify({"message": "No image uploaded"}), 400
# # #
# # #     file = request.files['image']
# # #     # יצירת שם קובץ ייחודי
# # #     unique_filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
# # #     upload_folder = current_app.config['UPLOAD_FOLDER']
# # #     file_path = os.path.join(upload_folder, unique_filename)
# # #     file.save(file_path)
# # #
# # #     variations = []
# # #     with Image.open(file_path) as img:
# # #         name, ext = os.path.splitext(unique_filename)
# # #         # שחור לבן
# # #         bw_name = f"{name}_bw{ext}"
# # #         img.convert('L').save(os.path.join(upload_folder, bw_name))
# # #         variations.append(bw_name)
# # #         # מסובב
# # #         rot_name = f"{name}_rot{ext}"
# # #         img.rotate(90).save(os.path.join(upload_folder, rot_name))
# # #         variations.append(rot_name)
# # #         # טשטוש (Blur)
# # #         blur_name = f"{name}_blur{ext}"
# # #         img.filter(ImageFilter.BLUR).save(os.path.join(upload_folder, blur_name))
# # #         variations.append(blur_name)
# # #     new_recipe = Recipe(
# # #         title=request.form.get('title'),
# # #         instructions=request.form.get('instructions'),
# # #         recipe_type=request.form.get('recipe_type'),
# # #
# # #         # שימי לב: באנגולר את משתמשת ב-recipe.image, אז ודאי ששם השדה במודל הוא image
# # #         # אם במודל שלך השדה נקרא image_path, תשאירי ככה אבל באנגולר תכתבי recipe.image_path
# # #         image=unique_filename,
# # #
# # #         # שמירת הווריאציות כ-JSON (כדי שתוכלי להציג גלריה באנגולר)
# # #         variation_paths=json.dumps(variations),
# # #         user_id=user_id,
# # #         prep_time=int(request.form.get('prep_time', 0))
# # #     )
# # #     # new_recipe = Recipe(
# # #     #     title=request.form.get('title'),
# # #     #     instructions=request.form.get('instructions'),
# # #     #     recipe_type=request.form.get('recipe_type'),
# # #     #     image_path=unique_filename,
# # #     #     variation_paths=json.dumps(variations),
# # #     #     user_id=user_id,
# # #     #     prep_time=int(request.form.get('prep_time', 0))
# # #     # )
# # #     db.session.add(new_recipe)
# # #     db.session.flush()
# # #
# # #     ingredients_data = json.loads(request.form.get('ingredients', '[]'))
# # #     for ing in ingredients_data:
# # #         db.session.add(IngredientEntry(
# # #             product=ing['product'],
# # #             amount=float(ing['amount']),
# # #             unit=ing['unit'],
# # #             recipe_id=new_recipe.id
# # #         ))
# # #
# # #     db.session.commit()
# # #     return jsonify({"message": "Recipe created successfully"}), 201
# # #
# # #
# # # # --- 5. חיפוש לפי רכיבים ---
# # # @recipes_bp.route('/search', methods=['POST'])
# # # def search_by_ingredients():
# # #     user_ingredients = {i.strip().lower() for i in request.json.get('ingredients', [])}
# # #     recipes = Recipe.query.filter_by(is_deleted=False).all()
# # #     results = []
# # #
# # #     for r in recipes:
# # #         recipe_set = {i.product.strip().lower() for i in r.ingredients}
# # #         if not recipe_set: continue
# # #
# # #         common = user_ingredients & recipe_set
# # #         score = (len(common) / len(recipe_set)) * 100
# # #
# # #         if score >= 10:
# # #             results.append({
# # #                 "id": r.id,
# # #                 "title": r.title,
# # #                 "score": round(score, 1),
# # #                 "image": get_full_url(r.image_path)
# # #             })
# # #  # מיון התוצאות מהציון הגבוה לנמוך
# # #
# # #     results.sort(key=lambda x: x['score'], reverse=True)
# # #     return jsonify(results), 200
# # # -----------------
# # # ----------------
# # # # import os
# # # # import uuid
# # # # import json # נדרש לשמירת רשימת הנתיבים ב-DB כשדה טקסט/JSON
# # # # from flask import request, jsonify
# # # # from PIL import Image # נדרש לעיבוד תמונה
# # # #
# # # #
# # # # # הניחי ש-UPLOAD_FOLDER ו-role_required כבר מוגדרים
# # # #
# # # # @app.route('/add_recipe', methods=['POST'])
# # # # @role_required('Uploader') # רק Uploader ומעלה יכולים לגשת
# # # # def add_recipe():
# # # # # 1. איסוף נתונים על המתכון
# # # # title = request.form.get('title')
# # # # instructions = request.form.get('instructions')
# # # #
# # # # # 2. איסוף קובץ התמונה
# # # # if 'image' not in request.files:
# # # # return jsonify({"message": "חסר קובץ תמונה"}), 400
# # # # file = request.files['image']
# # # #
# # # # # --- קוד עיבוד התמונה (כמו שראינו קודם) ---
# # # # unique_id = str(uuid.uuid4())
# # # # original_filename = f"{unique_id}_original.jpg"
# # # # original_path = os.path.join(UPLOAD_FOLDER, original_filename)
# # # #
# # # # # שמירת המקור
# # # # file.save(original_path)
# # # #
# # # # # יצירת הווריאציות (3 וריאציות)
# # # # img = Image.open(original_path)
# # # # variations_paths = []
# # # #
# # # # # (... כאן מגיע הקוד של 3 הווריאציות: שחור-לבן, סיבוב, ושינוי גודל ...)
# # # # # לצורך קיצור הדוגמה, נניח שהפונקציה create_variations החזירה את הנתיבים:
# # # #
# # # # bw_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_bw.jpg")
# # # # img.convert('L').save(bw_path)
# # # # variations_paths.append(bw_path)
# # # #
# # # # rotated_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_rotated.jpg")
# # # # img.rotate(90).save(rotated_path)
# # # # variations_paths.append(rotated_path)
# # # #
# # # # # --- יצירת מופע המתכון ושמירה ב-DB ---
# # # # try:
# # # # # 3. יצירת המופע (Instance)
# # # # new_recipe = Recipe(
# # # # title=title,
# # # # instructions=instructions,
# # # # image_path=original_path, # שמירת הנתיב של המקור
# # # # # המרת הרשימה לפורמט טקסטואלי (JSON) לפני שמירה בשדה variation_paths
# # # # variation_paths=json.dumps(variations_paths),
# # # # user_id=get_current_user().id # קישור למשתמש המעלה
# # # # # ... שדות נוספים כמו type, prep_time
# # # # )
# # # #
# # # # # 4. שמירה ב-DB
# # # # new_recipe.save()
# # # #
# # # # # (אפשרות: הוספת IngredientEntry למתכון, אם המידע נשלח)
# # # #
# # # # return jsonify({"message": "המתכון נוסף בהצלחה!", "recipe_id": new_recipe.id}), 201
# # # #
# # # # except Exception as e:
# # # # # טיפול בשגיאות
# # # # # מומלץ למחוק את הקבצים אם השמירה ל-DB נכשלה (Clean up)
# # # # # os.remove(original_path)
# # # # return jsonify({"message": "שגיאה בשמירת המתכון או הקבצים", "error": str(e)}), 500
# # # import os
# # # import uuid
# # # import json
# # # from flask import Blueprint, request, jsonify
# # # from PIL import Image # נדרש לעיבוד תמונה
# # # from decorators import role_required, get_current_user
# # # from models import Recipe
# # # from flask import current_app # משתמשים בזה במקום ב-app.py ישירות
# # #
# # # # ``````````````````````````````
# # # # from flask import Blueprint
# # # # 1. יוצרים מופע Blueprint במקום מופע App
# # # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# # #
# # # # 2. משתמשים בו להגדרת הנתיבים
# # # # @recipes_bp.route('/add', methods=['POST']) # הכתובת המלאה תהיה: /recipes/add
# # # # def add_recipe():
# # # # # ...
# # # # pass
# # # # ``````````````````````````````
# # #
# # #
# # #
# # # # הגדרת Blueprint: כל הנתיבים יתחילו ב-/recipes
# # # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# # #
# # # UPLOAD_FOLDER = 'uploads'
# # #
# # #
# # # # נתיב להוספת מתכון
# # # @recipes_bp.route('/add_recipe', methods=['POST'])
# # # # @recipes_bp.route('/add', methods=['POST']) # הכתובת המלאה תהיה: /recipes/add
# # # @role_required('Uploader') # רק משתמש תוכן ומעלה [cite: 88]
# # #
# # # def add_recipe():
# # # # 1. בדיקת קובץ ושליפת נתונים
# # # if 'image' not in request.files:
# # # return jsonify({"message": "חסר קובץ תמונה נדרש"}), 400
# # #
# # # # file = request.files['image']#גישה ישירה למילון
# # # file = request.files.get('image') # שימוש בסוגריים עגולים
# # # unique_id = str(uuid.uuid4())
# # # original_filename = f"{unique_id}_original.jpg"
# # # original_path = os.path.join(UPLOAD_FOLDER, original_filename)
# # #
# # # # 2. שמירה ועיבוד (Pillow) [cite: 136-138]
# # # try:
# # # # יצירת התיקייה אם אינה קיימת
# # # if not os.path.exists(UPLOAD_FOLDER):
# # # os.makedirs(UPLOAD_FOLDER)
# # #
# # # file.save(original_path) # שמירת המקור
# # # img = Image.open(original_path)
# # # variations_paths = []
# # #
# # # # וריאציה 1: שחור לבן
# # # bw_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_bw.jpg")
# # # img.convert('L').save(bw_path)
# # # variations_paths.append(bw_path)
# # #
# # # # וריאציה 2: סיבוב
# # # rotated_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_rotated.jpg")
# # # img.rotate(90, expand=True).save(rotated_path)
# # # variations_paths.append(rotated_path)
# # #
# # # # וריאציה 3: שינוי גודל
# # # thumbnail_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_thumb.jpg")
# # # img.resize((200, 200)).save(thumbnail_path)
# # # variations_paths.append(thumbnail_path)
# # #
# # # # 3. יצירת מופע Recipe ושמירה [cite: 106-108]
# # # current_user = get_current_user() # משיגים את המשתמש
# # #
# # # new_recipe = Recipe(
# # # title=request.form.get('title'),
# # # instructions=request.form.get('instructions'),
# # # image_path=original_path, # נתיב התמונה המקורית
# # # variation_paths=json.dumps(variations_paths), # נתיבי הווריאציות [cite: 139]
# # # user_id=current_user.id
# # # # ... יש להוסיף שדות כמו type, prep_time
# # # )
# # #
# # # new_recipe.save() # שמירה ב-DB
# # #
# # # return jsonify({"message": "המתכון נוסף בהצלחה!", "recipe_id": new_recipe.id}), 201
# # #
# # # except Exception as e:
# # # return jsonify({"message": "שגיאה בשרת", "error": str(e)}), 500
# # # ---------------------------------------------------------------------
# # # ---------------------------------------------------------------------
# # import os
# # import uuid
# # import json
# # from flask import Blueprint, request, jsonify, current_app
# # from werkzeug.utils import secure_filename # חשוב לאבטחת שמות קבצים
# # from PIL import Image, ImageEnhance, ImageFilter
# # # from PIL import Image
# # from models import Recipe, db, User, Rating # הניחי ש-db מיובא מ-models או מהקובץ הראשי
# # from decorators import role_required, get_current_user
# # from models import Recipe, IngredientEntry
# #
# # # from models import Recipe, User, Rating, db
# # from flask_jwt_extended import jwt_required, get_jwt_identity
# # from flask import send_from_directory
# #
# #
# # # 1. הגדרת ה-Blueprint
# # # כל הנתיבים בקובץ זה יתחילו בקידומת /recipes
# # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# #
# #
# # def allowed_file(filename):
# # # """בדיקה שהקובץ הוא תמונה (סיומת תקינה)"""
# #       ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# #       return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# #
# #
# # def apply_sepia(img):
# #       """פונקציה שמקבלת אובייקט Image ומחזירה אותו בגווני ספיה"""
# #       width, height = img.size
# #       # המרה ל-RGB כדי להבטיח שיש 3 ערוצי צבע
# #       img = img.convert("RGB")
# #       pixels = img.load()
# #
# #       for x in range(width):
# #           for y in range(height):
# #                r, g, b = pixels[x, y]
# #       # נוסחה מתמטית סטנדרטית לעיבוד ספיה
# #                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
# #                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
# #                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
# #
# #                # וידוא שהערכים לא עוברים את 255
# #                pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
# #       return img
# #
# # # @recipes_bp.route('/add', methods=['POST'])
# # # @role_required('Uploader') # רק משתמש שאושר כ-Uploader או Admin יכול להעלות [cite: 15, 80]
# # # def add_recipe():
# # #       """
# # # נתיב להוספת מתכון חדש.
# # # כולל העלאת תמונה, יצירת 3 וריאציות, ושמירת פרטים ב-DB.
# # #       """
# # #       try:
# # #
# # # # --- שלב 1: בדיקת קובץ תמונה ---
# # #
# # #           if 'image' not in request.files:
# # #                return jsonify({"message": "No image part in the request"}), 400
# # #
# # #           file = request.files['image']
# # #
# # #           if file.filename == '' or not allowed_file(file.filename):
# # #                    return jsonify({"message": "No selected file or invalid file type"}), 400
# # #
# # # # --- שלב 2: הכנת התיקייה והשמות ---
# # # # שימוש בתיקייה המוגדרת בקונפיגורציה של האפליקציה (או ברירת מחדל 'uploads')
# # # upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# # # if not os.path.exists(upload_folder):
# # # os.makedirs(upload_folder)
# # #
# # # # יצירת שם ייחודי למניעת דריסת קבצים [cite: 69]
# # # unique_id = str(uuid.uuid4())
# # # # ניקוי שם הקובץ המקורי מתווים מסוכנים
# # # safe_filename = secure_filename(file.filename)
# # # extension = safe_filename.rsplit('.', 1)[1].lower()
# # #
# # # # בניית השם לקובץ המקורי
# # # original_filename = f"{unique_id}_original.{extension}"
# # # original_path = os.path.join(upload_folder, original_filename)
# # #
# # # # --- שלב 3: שמירה ועיבוד תמונה (Pillow) ---
# # # file.save(original_path) # שמירת המקור בדיסק
# # #
# # # img = Image.open(original_path)
# # # variation_paths = [] # רשימה לשמירת נתיבי הווריאציות [cite: 66]
# # #
# # # # וריאציה 1: שחור-לבן (Black & White) [cite: 64]
# # # bw_filename = f"{unique_id}_bw.{extension}"
# # # bw_path = os.path.join(upload_folder, bw_filename)
# # # img.convert('L').save(bw_path)
# # # variation_paths.append(bw_filename) # שומרים רק את שם הקובץ, לא את הנתיב המלא
# # #
# # # # וריאציה 3: שיפור חדות וצבע (Vivid) - גורם לאוכל להיראות מגרה
# # # from PIL import ImageEnhance
# # # vivid_filename = f"{unique_id}_vivid.{extension}"
# # # vivid_path = os.path.join(upload_folder, vivid_filename)
# # # # שיפור צבע (Color) פי 1.5
# # # enhancer = ImageEnhance.Color(img.copy())
# # # vivid_img = enhancer.enhance(1.5)
# # # vivid_img.save(vivid_path)
# # # variation_paths.append(vivid_filename)
# # #
# # # # וריאציה 2: ספיה
# # # sepia_filename = f"{unique_id}_sepia.{extension}"
# # # sepia_path = os.path.join(upload_folder, sepia_filename)
# # # sepia_img = apply_sepia(img.copy())
# # # sepia_img.save(sepia_path) # תיקון: היה כתוב path, עכשיו sepia_path
# # # variation_paths.append(sepia_filename)
# # #
# # # # וריאציה 4: טשטוש (Blur) - מראה רך ויוקרתי
# # # # blur_filename = f"{unique_id}_blur.{extension}"
# # # # blur_path = os.path.join(upload_folder, blur_filename)
# # # # # יצירת טשטוש ברדיוס 2 (עדין)
# # # # blur_img = img.copy().filter(ImageFilter.GaussianBlur(radius=2))
# # # # blur_img.save(blur_path)
# # # # variation_paths.append(blur_filename)
# # # # # וריאציה 2: סיבוב (Rotated) [cite: 64]
# # # # rotated_filename = f"{unique_id}_rotated.{extension}"
# # # # rotated_path = os.path.join(upload_folder, rotated_filename)
# # # # img.rotate(90, expand=True).save(rotated_path)
# # # # variation_paths.append(rotated_filename)
# # #
# # # # וריאציה 3: שינוי גודל (Thumbnail) [cite: 64]
# # # # thumb_filename = f"{unique_id}_thumb.{extension}"
# # # # thumb_path = os.path.join(upload_folder, thumb_filename)
# # # # img_copy = img.copy() # עדיף לעבוד על עותק כשמשנים גודל
# # # # img_copy.thumbnail((5000, 5000)) # שומר על יחס גובה-רוחב
# # # # img_copy.save(thumb_path)
# # # # variation_paths.append(thumb_filename)
# # #
# # #
# # #
# # # enhancer = ImageEnhance.Color(img)
# # # img_vivid = enhancer.enhance(2.0)
# # # img_vivid.save(vivid_path)
# # # # --- שלב 4: קליטת נתוני הטופס ושמירה ב-DB ---
# # # title = request.form.get('title')
# # # instructions = request.form.get('instructions')# קבלת המידע מהלקוח
# # # recipe_type = request.form.get('type') # Dairy, Meat, Parve
# # # # תיקון: השם ב-Angular הוא 'type'
# # # # recipe_type = request.form.get('type')
# # # #
# # #
# # #
# # #
# # #
# # # current_user = get_current_user() # שליפת המשתמש המחובר
# # # # --------------
# # # # title = request.form.get('title'),
# # # # instructions=request.form.get('instructions'),
# # # # image_path=original_path, # נתיב התמונה המקורית
# # # # variation_paths=json.dumps(variations_paths), # נתיבי הווריאציות [cite: 139]
# # # # user_id=current_user.id
# # # # -----------------
# # #
# # # # prep_time = request.form.get('prep_time') # קבלת הזמן מהטופס
# # # # # תיקון: המרה למספר שלם עבור זמן הכנה
# # # prep_time_raw = request.form.get('prep_time')
# # # prep_time = int(prep_time_raw) if prep_time_raw else 0
# # # new_recipe = Recipe(
# # # title=title,
# # # # (אם יש שדה הוראות במודל, אם לא - הסירי את השורה הבאה)
# # # instructions=instructions,
# # # recipe_type=recipe_type,
# # # image_path=original_filename, # שמירת שם הקובץ המקורי
# # # variation_paths=json.dumps(variation_paths), # המרה ל-JSON String
# # # user_id=current_user.id,
# # # prep_time=prep_time, # שדה חדש למיון
# # # avg_rating=0.0, # איתחול דירוג לבונוס
# # # is_deleted=False # ברירת מחדל, אם קיים
# # # )
# # #
# # # new_recipe.save() # מתודת השמירה שירשנו מ-BaseModel [cite: 35]
# # # # --- שלב 5: שמירת רכיבים (Ingredients) ---
# # # # אנחנו מצפים לקבל מהלקוח מחרוזת JSON שמייצגת רשימת אובייקטים
# # # ingredients_data = request.form.get('ingredients')
# # #
# # # if ingredients_data:
# # # # המרת הטקסט חזרה לרשימת פייתון
# # # ingredients_list = json.loads(ingredients_data)
# # #
# # # for ing in ingredients_list:
# # # new_ingredient = IngredientEntry(
# # # product=ing.get('product'),
# # # amount=float(ing.get('amount')),
# # # unit=ing.get('unit'),
# # # recipe_id=new_recipe.id # הקישור למתכון שיצרנו הרגע!
# # # )
# # # new_ingredient.save()
# # # return jsonify({
# # # "message": "Recipe added successfully",
# # # "recipe_id": new_recipe.id,
# # # "variations": variation_paths
# # # }), 201
# # #
# # # except Exception as e:
# # # # במקרה של שגיאה, רצוי להוסיף לוגיקה שמוחקת את התמונות שנוצרו כדי לא ללכלך את השרת
# # # print(f"Error adding recipe: {e}")
# # # return jsonify({"message": "Failed to add recipe", "error": str(e)}), 500
# #
# # # --- נתיב העלאת מתכון חדש (כולל עיבוד תמונות) ---
# # @recipes_bp.route('/add', methods=['POST'])
# # @jwt_required()  # חובה: רק משתמש רשום יכול להעלות
# # def add_recipe():
# #     # 1. זיהוי המשתמש המעלה
# #     current_user_id = get_jwt_identity()
# #     user = User.query.get(current_user_id)
# #
# #     # בדיקת הרשאות (אופציונלי: אם את רוצה שרק 'Uploader' יעלה)
# #     # if not user.is_approved_uploader:
# #     #     return jsonify({"message": "אין לך הרשאה להעלות מתכונים"}), 403
# #
# #     # 2. בדיקה שנשלח קובץ תמונה
# #     if 'image' not in request.files:
# #         return jsonify({"message": "חובה להעלות תמונה"}), 400
# #
# #     file = request.files['image']
# #     if file.filename == '':
# #         return jsonify({"message": "לא נבחר קובץ"}), 400
# #
# #     # 3. שמירת התמונה המקורית ועיבוד וריאציות עם Pillow
# #     if file:
# #         # ניקוי שם הקובץ למניעת פרצות אבטחה
# #         filename = secure_filename(file.filename)
# #         # שימוש בתיקיית ה-uploads שהוגדרה ב-app.py
# #         upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# #
# #         # ודאי שהתיקייה קיימת
# #         os.makedirs(upload_folder, exist_ok=True)
# #
# #         # שמירת המקור
# #         original_path = os.path.join(upload_folder, filename)
# #         file.save(original_path)
# #
# #         # --- יצירת וריאציות (Pillow) ---
# #         try:
# #             # פתיחת התמונה לזיכרון לעיבוד
# #             img = Image.open(original_path)
# #
# #             # פיצול השם והסיומת (למשל pizza ו-.jpg)
# #             name, ext = os.path.splitext(filename)
# #
# #             # וריאציה 1: שחור לבן (Black & White)
# #             # 'L' מציין מצב Grayscale
# #             img_bw = img.convert('L')
# #             img_bw.save(os.path.join(upload_folder, f"{name}_bw{ext}"))
# #
# #             # וריאציה 2: מסובב (Rotated)
# #             # סיבוב ב-90 מעלות נגד כיוון השעון
# #             img_rotated = img.rotate(90, expand=True)
# #             img_rotated.save(os.path.join(upload_folder, f"{name}_rotated{ext}"))
# #
# #             # וריאציה 3: אפקט מיוחד (Blur/Filter)
# #             # הוספת פילטר טשטוש או הדגשת פרטים. כאן בחרנו ב-DETAIL
# #             img_effect = img.filter(ImageFilter.DETAIL)
# #             img_effect.save(os.path.join(upload_folder, f"{name}_effect{ext}"))
# #
# #         except Exception as e:
# #             print(f"Error processing images: {e}")
# #             return jsonify({"message": "שגיאה בעיבוד התמונות"}), 500
# #
# #         # 4. קריאת נתוני הטקסט (מגיעים ב-form-data)
# #         try:
# #             # יצירת אובייקט המתכון
# #             new_recipe = Recipe(
# #                 title=request.form['title'],
# #                 description=request.form.get('description', ''),
# #                 instructions=request.form['instructions'],
# #                 prep_time=int(request.form.get('prep_time', 0)),
# #                 servings=int(request.form.get('servings', 0)),
# #                 image_filename=filename,  # שומרים רק את שם הקובץ המקורי
# #                 user_id=user.id
# #             )
# #
# #             db.session.add(new_recipe)
# #             db.session.commit()  # שומרים כדי לקבל new_recipe.id
# #
# #             # 5. טיפול ברכיבים (Ingredients)
# #             # ב-FormData רשימות מגיעות בדרך כלל כמחרוזת JSON
# #             ingredients_json = request.form.get('ingredients')
# #             if ingredients_json:
# #                 ingredients_list = json.loads(ingredients_json)
# #
# #                 for item in ingredients_list:
# #                     # item נראה ככה: {'name': 'קמח', 'amount': 500, 'unit': 'גרם'}
# #
# #                     # בדיקה אם הרכיב קיים במאגר הגלובלי, אם לא - יוצרים אותו
# #                     # זה קריטי לחיפוש החכם שלך (Sets)!
# #                     ing_obj = Ingredient.query.filter_by(name=item['name']).first()
# #                     if not ing_obj:
# #                         ing_obj = Ingredient(name=item['name'])
# #                         db.session.add(ing_obj)
# #                         db.session.commit()  # שומרים כדי לקבל id
# #
# #                     # יצירת הקישור בטבלת הקשר
# #                     entry = IngredientEntry(
# #                         recipe_id=new_recipe.id,
# #                         ingredient_id=ing_obj.id,
# #                         amount=item.get('amount', ''),
# #                         unit=item.get('unit', '')
# #                     )
# #                     db.session.add(entry)
# #
# #             db.session.commit()  # שמירה סופית של הכל
# #             return jsonify({"message": "המתכון הועלה בהצלחה!", "recipe_id": new_recipe.id}), 201
# #
# #         except Exception as e:
# #             db.session.rollback()  # ביטול שינויים במקרה שגיאה
# #             return jsonify({"message": f"שגיאה בשמירת הנתונים: {str(e)}"}), 500
# #
# # # @recipes_bp.route('/all', methods=['GET'])
# # # def get_all_recipes():
# # # # שליפת כל המתכונים שלא נמחקו
# # # recipes = Recipe.query.filter_by(is_deleted=False).all()
# # #
# # # output = []
# # # for r in recipes:
# # # output.append({
# # # "id": r.id,
# # # "title": r.title,
# # # "image": r.image_path,
# # # "type": r.recipe_type,
# # # "variations": json.loads(r.variation_paths) if r.variation_paths else []
# # # })
# # #
# # # return jsonify(output), 200
# # # זה מאפשר לכל העולם לגשת לקבצים בתיקיית uploads בלי טוקן
# # # return send_from_directory('uploads', filename)
# # @recipes_bp.route('/all', methods=['GET'])
# # def get_all_recipes():
# #      recipes = Recipe.query.filter_by(is_deleted=False).all()
# #      output = []
# #      for r in recipes:
# #          output.append({
# #          "id": r.id,
# #          "title": r.title,
# #          "image": r.image_path,
# #          "recipe_type": r.recipe_type, # התאמה לאנגולר
# #          "prep_time": r.prep_time, # הוספה בשביל המיון
# #          "avg_rating": r.avg_rating, # הוספה בשביל הכוכבים
# #          "variations": json.loads(r.variation_paths) if r.variation_paths else []
# #          })
# #      return jsonify(output), 200
# #
# # # נתיב ציבורי לתמונות - לא דורש טוקן!
# # @recipes_bp.route('/file/<filename>')
# # def serve_recipe_image(filename):
# #     upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# #     return send_from_directory(upload_folder, filename)
# # # @recipes_bp.route('/all', methods=['GET'])
# # # # @jwt_required(optional=True) # <--- הוסיפי את השורה הזו!
# # # def get_all_recipes():
# # # # שליפת כל המתכונים שלא נמחקו
# # # recipes = Recipe.query.filter_by(is_deleted=False).all()
# # #
# # # # ניסיון לזהות את המשתמש המחובר (כדי לדעת מה הוא סימן כמועדף)
# # # # הערה: אם את משתמשת ב-JWT, אפשר להוציא את ה-identity
# # # # אם לא נשלח טוקן, user_id יהיה None
# # # try:
# # # current_user_id = get_jwt_identity()
# # # user = User.query.get(current_user_id) if current_user_id else None
# # # # recipes = Recipe.query.filter_by(is_deleted=False).all()
# # # except:
# # # user = None
# # #
# # # output = []
# # # for r in recipes:
# # # output.append({
# # # "id": r.id,
# # # "title": r.title,
# # # "image": r.image_path,
# # # "recipe_type": r.recipe_type, # שימוש בשם העמודה מה-Model שלך
# # # "prep_time": r.prep_time, # חובה בשביל המיון ב-Angular!
# # # "avg_rating": r.avg_rating, # חובה בשביל המיון והצגת הכוכבים
# # # "variations": json.loads(r.variation_paths) if r.variation_paths else [],
# # #
# # # # בדיקה האם המתכון הזה נמצא ברשימת המועדפים של המשתמש שצופה כרגע
# # # "is_favorite": user in r.favorited_by if user else False
# # # })
# # #
# # # return jsonify(output), 200
# # # @recipes_bp.route('/delete/<int:recipe_id>', methods=['DELETE'])
# # # @role_required('Uploader') # או Admin
# # # def delete_recipe(recipe_id):
# # # recipe = Recipe.query.get(recipe_id)
# # # if not recipe:
# # # return jsonify({"message": "מתכון לא נמצא"}), 404
# # #
# # # # מחיקה לוגית
# # # recipe.is_deleted = True
# # # recipe.save()
# #
# # # return jsonify({"message": "המתכון נמחק בהצלחה (לוגית)"}), 200
# #
# # #--------------------------------------------------------
# # #------------------------------------------------
# #
# # #------------------------------------------------
# # #-----------------------ניתוב למתכון בודד----------------------
# # @recipes_bp.route('/<int:recipe_id>', methods=['GET'])
# # def get_recipe_details(recipe_id):
# # # """שליפת פרטי מתכון בודד כולל רכיבים ותמונות"""
# #      recipe = Recipe.query.get_or_404(recipe_id)
# #
# #      # הכנת רשימת הרכיבים בפורמט JSON
# #      ingredients = []
# #      for ing in recipe.ingredients:
# #           ingredients.append({
# #           "product": ing.product,
# #           "amount": ing.amount,
# #           "unit": ing.unit
# #           })
# #
# #           return jsonify({
# #           "id": recipe.id,
# #           "title": recipe.title,
# #           "instructions": recipe.instructions,
# #           "type": recipe.recipe_type,
# #           "image": recipe.image_path,
# #           "prep_time": recipe.prep_time, # <--- הוספת השורה הזו חיונית!
# #           "avg_rating": recipe.avg_rating, # מומלץ להוסיף גם את זה לדירוג
# #
# #           "variations": json.loads(recipe.variation_paths) if recipe.variation_paths else [],
# #           "ingredients": ingredients,
# #           "author_id": recipe.user_id
# #           }), 200
# # #-------------חיפוש מתכון לפי רכיבים-------------------
# #
# # @recipes_bp.route('/search', methods=['POST'])
# # def search_recipes():
# #       # שלב 1: הכנת נתונים - קבלת הרשימה מהלקוח והפיכתה ל-Set
# #       data = request.json
# #       # רשימת המצרכים שהמשתמש הזין (למשל: ["קמח", "ביצים", "סוכר"])
# #       user_ingredients_list = data.get('ingredients', [])
# #       # user_set = set(user_ingredients_list)
# #       # ניקוי רווחים מהרכיבים של המשתמש
# #       user_set = {i.strip().lower() for i in user_ingredients_list if i}
# #
# #       # שליפת כל המתכונים מהמסד (רק אלו שלא נמחקו)
# #       all_recipes = Recipe.query.filter_by(is_deleted=False).all()
# #       results = []
# #
# #       for recipe in all_recipes:
# #       # שלב 1 המשך: הכנת ה-Set של המתכון הנוכחי
# #       # שליפת שמות הרכיבים מתוך הקשר (Relationship) שיצרנו במודל
# #       # recipe_ingredients_list = [ing.product.strip() for ing in recipe.ingredients]
# #       # recipe_set = set(recipe_ingredients_list)
# #       # שימוש ב-Set Comprehension בשורה אחת - יעיל וקריא יותר
# #            recipe_set = {ing.product.strip().lower() for ing in recipe.ingredients if ing.product}
# #            if not recipe_set: # הגנה למקרה של מתכון בלי רכיבים
# #                continue
# #
# # # שלב 2: חישוב רכיבים משותפים (Intersection) באמצעות האופרטור &
# #            common_ingredients = user_set & recipe_set
# #
# # # שלב 3: חישוב ציון ההתאמה (Matching Score)
# # # נוסחה: (כמות משותפים / סך הכל נדרשים במתכון)
# #            score = len(common_ingredients) / len(recipe_set)
# #
# # # שלב 4: סינון (רק מתכונים עם התאמה של מעל 20%)
# #       if score >= 0.1:
# #            results.append({
# #            "id": recipe.id,
# #            "title": recipe.title,
# #            "score": round(score * 100, 2), # הפיכה לאחוזים (למשל 75.5)
# #            "image": recipe.image_path,
# #            "matching_count": len(common_ingredients),
# #            "missing_ingredients": list(recipe_set - user_set) # מה חסר למשתמש לקנות
# #            })
# #
# # # שלב 4 המשך: מיון התוצאות בסדר יורד לפי הציון (Score)
# #            results.sort(key=lambda x: x['score'], reverse=True)
# #
# # # שלב 4 סיום: שליחת הנתונים ל-Angular
# #       return jsonify(results), 200
# #
# #
# #
# # # --- מחיקת מתכון (מותאם למנהל) ---
# # @recipes_bp.route('/delete/<int:recipe_id>', methods=['DELETE'])
# # @jwt_required()
# # def delete_recipe(recipe_id):
# #       current_user_id = get_jwt_identity()
# #       user = User.query.get(current_user_id)
# #       recipe = Recipe.query.get_or_404(recipe_id)
# #
# #       # בדיקה: רק אם המשתמש הוא מנהל, או שזה המתכון שלו והוא Uploader
# #       if user.role == 'Admin' or (user.role == 'Uploader' and recipe.user_id == user.id):
# #            recipe.is_deleted = True
# #            recipe.save()
# #            return jsonify({"message": "המתכון נמחק בהצלחה"}), 200
# #
# #       return jsonify({"message": "אין לך הרשאה למחוק מתכון זה"}), 403
# #
# #
# # # --- ניהול מועדפים ---
# # @recipes_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
# # @jwt_required()
# # def toggle_favorite(recipe_id):
# #      user_id = get_jwt_identity()
# #      user = User.query.get(user_id)
# #      recipe = Recipe.query.get_or_404(recipe_id)
# #
# #      if recipe in user.favorite_recipes:
# #           user.favorite_recipes.remove(recipe)
# #           message = "הוסר מהמועדפים"
# #           is_favorite = False
# #      else:
# #           user.favorite_recipes.append(recipe)
# #           message = "נוסף למועדפים"
# #           is_favorite = True
# #
# #      db.session.commit()
# #      return jsonify({"message": message, "is_favorite": is_favorite}), 200
# # # פונקציה להוספה/הסרה מהמועדפים (Toggle)
# # @recipes_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
# # @jwt_required()
# # def toggle_favorite(recipe_id):
# #      current_user_id = get_jwt_identity()
# #      user = User.query.get(current_user_id)
# #      recipe = Recipe.query.get_or_404(recipe_id)
# # ---------------
# # -----------------
#
#
# # # import os
# # # import uuid
# # # import json # נדרש לשמירת רשימת הנתיבים ב-DB כשדה טקסט/JSON
# # # from flask import request, jsonify
# # # from PIL import Image # נדרש לעיבוד תמונה
# # #
# # #
# # # # הניחי ש-UPLOAD_FOLDER ו-role_required כבר מוגדרים
# # #
# # # @app.route('/add_recipe', methods=['POST'])
# # # @role_required('Uploader') # רק Uploader ומעלה יכולים לגשת
# # # def add_recipe():
# # # # 1. איסוף נתונים על המתכון
# # # title = request.form.get('title')
# # # instructions = request.form.get('instructions')
# # #
# # # # 2. איסוף קובץ התמונה
# # # if 'image' not in request.files:
# # # return jsonify({"message": "חסר קובץ תמונה"}), 400
# # # file = request.files['image']
# # #
# # # # --- קוד עיבוד התמונה (כמו שראינו קודם) ---
# # # unique_id = str(uuid.uuid4())
# # # original_filename = f"{unique_id}_original.jpg"
# # # original_path = os.path.join(UPLOAD_FOLDER, original_filename)
# # #
# # # # שמירת המקור
# # # file.save(original_path)
# # #
# # # # יצירת הווריאציות (3 וריאציות)
# # # img = Image.open(original_path)
# # # variations_paths = []
# # #
# # # # (... כאן מגיע הקוד של 3 הווריאציות: שחור-לבן, סיבוב, ושינוי גודל ...)
# # # # לצורך קיצור הדוגמה, נניח שהפונקציה create_variations החזירה את הנתיבים:
# # #
# # # bw_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_bw.jpg")
# # # img.convert('L').save(bw_path)
# # # variations_paths.append(bw_path)
# # #
# # # rotated_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_rotated.jpg")
# # # img.rotate(90).save(rotated_path)
# # # variations_paths.append(rotated_path)
# # #
# # # # --- יצירת מופע המתכון ושמירה ב-DB ---
# # # try:
# # # # 3. יצירת המופע (Instance)
# # # new_recipe = Recipe(
# # # title=title,
# # # instructions=instructions,
# # # image_path=original_path, # שמירת הנתיב של המקור
# # # # המרת הרשימה לפורמט טקסטואלי (JSON) לפני שמירה בשדה variation_paths
# # # variation_paths=json.dumps(variations_paths),
# # # user_id=get_current_user().id # קישור למשתמש המעלה
# # # # ... שדות נוספים כמו type, prep_time
# # # )
# # #
# # # # 4. שמירה ב-DB
# # # new_recipe.save()
# # #
# # # # (אפשרות: הוספת IngredientEntry למתכון, אם המידע נשלח)
# # #
# # # return jsonify({"message": "המתכון נוסף בהצלחה!", "recipe_id": new_recipe.id}), 201
# # #
# # # except Exception as e:
# # # # טיפול בשגיאות
# # # # מומלץ למחוק את הקבצים אם השמירה ל-DB נכשלה (Clean up)
# # # # os.remove(original_path)
# # # return jsonify({"message": "שגיאה בשמירת המתכון או הקבצים", "error": str(e)}), 500
# # import os
# # import uuid
# # import json
# # from flask import Blueprint, request, jsonify
# # from PIL import Image # נדרש לעיבוד תמונה
# # from decorators import role_required, get_current_user
# # from models import Recipe
# # from flask import current_app # משתמשים בזה במקום ב-app.py ישירות
# #
# # # ``````````````````````````````
# # # from flask import Blueprint
# # # 1. יוצרים מופע Blueprint במקום מופע App
# # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# #
# # # 2. משתמשים בו להגדרת הנתיבים
# # # @recipes_bp.route('/add', methods=['POST']) # הכתובת המלאה תהיה: /recipes/add
# # # def add_recipe():
# # # # ...
# # # pass
# # # ``````````````````````````````
# #
# #
# #
# # # הגדרת Blueprint: כל הנתיבים יתחילו ב-/recipes
# # recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
# #
# # UPLOAD_FOLDER = 'uploads'
# #
# #
# # # נתיב להוספת מתכון
# # @recipes_bp.route('/add_recipe', methods=['POST'])
# # # @recipes_bp.route('/add', methods=['POST']) # הכתובת המלאה תהיה: /recipes/add
# # @role_required('Uploader') # רק משתמש תוכן ומעלה [cite: 88]
# #
# # def add_recipe():
# # # 1. בדיקת קובץ ושליפת נתונים
# # if 'image' not in request.files:
# # return jsonify({"message": "חסר קובץ תמונה נדרש"}), 400
# #
# # # file = request.files['image']#גישה ישירה למילון
# # file = request.files.get('image') # שימוש בסוגריים עגולים
# # unique_id = str(uuid.uuid4())
# # original_filename = f"{unique_id}_original.jpg"
# # original_path = os.path.join(UPLOAD_FOLDER, original_filename)
# #
# # # 2. שמירה ועיבוד (Pillow) [cite: 136-138]
# # try:
# # # יצירת התיקייה אם אינה קיימת
# # if not os.path.exists(UPLOAD_FOLDER):
# # os.makedirs(UPLOAD_FOLDER)
# #
# # file.save(original_path) # שמירת המקור
# # img = Image.open(original_path)
# # variations_paths = []
# #
# # # וריאציה 1: שחור לבן
# # bw_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_bw.jpg")
# # img.convert('L').save(bw_path)
# # variations_paths.append(bw_path)
# #
# # # וריאציה 2: סיבוב
# # rotated_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_rotated.jpg")
# # img.rotate(90, expand=True).save(rotated_path)
# # variations_paths.append(rotated_path)
# #
# # # וריאציה 3: שינוי גודל
# # thumbnail_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_thumb.jpg")
# # img.resize((200, 200)).save(thumbnail_path)
# # variations_paths.append(thumbnail_path)
# #
# # # 3. יצירת מופע Recipe ושמירה [cite: 106-108]
# # current_user = get_current_user() # משיגים את המשתמש
# #
# # new_recipe = Recipe(
# # title=request.form.get('title'),
# # instructions=request.form.get('instructions'),
# # image_path=original_path, # נתיב התמונה המקורית
# # variation_paths=json.dumps(variations_paths), # נתיבי הווריאציות [cite: 139]
# # user_id=current_user.id
# # # ... יש להוסיף שדות כמו type, prep_time
# # )
# #
# # new_recipe.save() # שמירה ב-DB
# #
# # return jsonify({"message": "המתכון נוסף בהצלחה!", "recipe_id": new_recipe.id}), 201
# #
# # except Exception as e:
# # return jsonify({"message": "שגיאה בשרת", "error": str(e)}), 500
# # ---------------------------------------------------------------------
# # ---------------------------------------------------------------------
# import os
# import uuid
# import json
# from flask import Blueprint, request, jsonify, current_app
# from werkzeug.utils import secure_filename  # חשוב לאבטחת שמות קבצים
# from PIL import Image, ImageEnhance, ImageFilter
# # from PIL import Image
# from models import Recipe, db, User, Rating  # הניחי ש-db מיובא מ-models או מהקובץ הראשי
# from decorators import role_required, get_current_user
# from models import Recipe, IngredientEntry
#
# # from models import Recipe, User, Rating, db
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from flask import send_from_directory
#
# # 1. הגדרת ה-Blueprint
# # כל הנתיבים בקובץ זה יתחילו בקידומת /recipes
# recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')
#
#
# def allowed_file(filename):
#     """בדיקה שהקובץ הוא תמונה (סיומת תקינה)"""
#
#
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# def apply_sepia(img):
#     """פונקציה שמקבלת אובייקט Image ומחזירה אותו בגווני ספיה"""
#
#
# width, height = img.size
# # המרה ל-RGB כדי להבטיח שיש 3 ערוצי צבע
# img = img.convert("RGB")
# pixels = img.load()
#
# for x in range(width):
#     for y in range(height):
#         r, g, b = pixels[x, y]
# # נוסחה מתמטית סטנדרטית לעיבוד ספיה
# tr = int(0.393 * r + 0.769 * g + 0.189 * b)
# tg = int(0.349 * r + 0.686 * g + 0.168 * b)
# tb = int(0.272 * r + 0.534 * g + 0.131 * b)
#
# # וידוא שהערכים לא עוברים את 255
# pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
# return img
#
#
# @recipes_bp.route('/add', methods=['POST'])
# @role_required('Uploader')  # רק משתמש שאושר כ-Uploader או Admin יכול להעלות [cite: 15, 80]
# def add_recipe():
#     """
#     נתיב להוספת מתכון חדש.
#     כולל העלאת תמונה, יצירת 3 וריאציות, ושמירת פרטים ב-DB.
#     """
#
#
# try:
# # --- שלב 1: בדיקת קובץ תמונה ---
# if 'image' not in request.files:
#     return jsonify({"message": "No image part in the request"}), 400
#
# file = request.files['image']
#
# if file.filename == '' or not allowed_file(file.filename):
#     return jsonify({"message": "No selected file or invalid file type"}), 400
#
# # --- שלב 2: הכנת התיקייה והשמות ---
# # שימוש בתיקייה המוגדרת בקונפיגורציה של האפליקציה (או ברירת מחדל 'uploads')
# upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# if not os.path.exists(upload_folder):
#     os.makedirs(upload_folder)
#
# # יצירת שם ייחודי למניעת דריסת קבצים [cite: 69]
# unique_id = str(uuid.uuid4())
# # ניקוי שם הקובץ המקורי מתווים מסוכנים
# safe_filename = secure_filename(file.filename)
# extension = safe_filename.rsplit('.', 1)[1].lower()
#
# # בניית השם לקובץ המקורי
# original_filename = f"{unique_id}_original.{extension}"
# original_path = os.path.join(upload_folder, original_filename)
#
# # --- שלב 3: שמירה ועיבוד תמונה (Pillow) ---
# file.save(original_path)  # שמירת המקור בדיסק
#
# img = Image.open(original_path)
# variation_paths = []  # רשימה לשמירת נתיבי הווריאציות [cite: 66]
#
# # וריאציה 1: שחור-לבן (Black & White) [cite: 64]
# bw_filename = f"{unique_id}_bw.{extension}"
# bw_path = os.path.join(upload_folder, bw_filename)
# img.convert('L').save(bw_path)
# variation_paths.append(bw_filename)  # שומרים רק את שם הקובץ, לא את הנתיב המלא
#
# # וריאציה 3: שיפור חדות וצבע (Vivid) - גורם לאוכל להיראות מגרה
# from PIL import ImageEnhance
#
# vivid_filename = f"{unique_id}_vivid.{extension}"
# vivid_path = os.path.join(upload_folder, vivid_filename)
# # שיפור צבע (Color) פי 1.5
# enhancer = ImageEnhance.Color(img.copy())
# vivid_img = enhancer.enhance(1.5)
# vivid_img.save(vivid_path)
# variation_paths.append(vivid_filename)
#
# # וריאציה 2: ספיה
# sepia_filename = f"{unique_id}_sepia.{extension}"
# sepia_path = os.path.join(upload_folder, sepia_filename)
# sepia_img = apply_sepia(img.copy())
# sepia_img.save(sepia_path)  # תיקון: היה כתוב path, עכשיו sepia_path
# variation_paths.append(sepia_filename)
#
# # וריאציה 4: טשטוש (Blur) - מראה רך ויוקרתי
# # blur_filename = f"{unique_id}_blur.{extension}"
# # blur_path = os.path.join(upload_folder, blur_filename)
# # # יצירת טשטוש ברדיוס 2 (עדין)
# # blur_img = img.copy().filter(ImageFilter.GaussianBlur(radius=2))
# # blur_img.save(blur_path)
# # variation_paths.append(blur_filename)
# # # וריאציה 2: סיבוב (Rotated) [cite: 64]
# # rotated_filename = f"{unique_id}_rotated.{extension}"
# # rotated_path = os.path.join(upload_folder, rotated_filename)
# # img.rotate(90, expand=True).save(rotated_path)
# # variation_paths.append(rotated_filename)
#
# # וריאציה 3: שינוי גודל (Thumbnail) [cite: 64]
# # thumb_filename = f"{unique_id}_thumb.{extension}"
# # thumb_path = os.path.join(upload_folder, thumb_filename)
# # img_copy = img.copy() # עדיף לעבוד על עותק כשמשנים גודל
# # img_copy.thumbnail((5000, 5000)) # שומר על יחס גובה-רוחב
# # img_copy.save(thumb_path)
# # variation_paths.append(thumb_filename)
#
#
# enhancer = ImageEnhance.Color(img)
# img_vivid = enhancer.enhance(2.0)
# img_vivid.save(vivid_path)
# # --- שלב 4: קליטת נתוני הטופס ושמירה ב-DB ---
# title = request.form.get('title')
# instructions = request.form.get('instructions')  # קבלת המידע מהלקוח
# recipe_type = request.form.get('type')  # Dairy, Meat, Parve
# # תיקון: השם ב-Angular הוא 'type'
# # recipe_type = request.form.get('type')
# #
#
#
# current_user = get_current_user()  # שליפת המשתמש המחובר
# # --------------
# # title = request.form.get('title'),
# # instructions=request.form.get('instructions'),
# # image_path=original_path, # נתיב התמונה המקורית
# # variation_paths=json.dumps(variations_paths), # נתיבי הווריאציות [cite: 139]
# # user_id=current_user.id
# # -----------------
#
# # prep_time = request.form.get('prep_time') # קבלת הזמן מהטופס
# # # תיקון: המרה למספר שלם עבור זמן הכנה
# prep_time_raw = request.form.get('prep_time')
# prep_time = int(prep_time_raw) if prep_time_raw else 0
# new_recipe = Recipe(
#     title=title,
#     # (אם יש שדה הוראות במודל, אם לא - הסירי את השורה הבאה)
#     instructions=instructions,
#     recipe_type=recipe_type,
#     image_path=original_filename,  # שמירת שם הקובץ המקורי
#     variation_paths=json.dumps(variation_paths),  # המרה ל-JSON String
#     user_id=current_user.id,
#     prep_time=prep_time,  # שדה חדש למיון
#     avg_rating=0.0,  # איתחול דירוג לבונוס
#     is_deleted=False  # ברירת מחדל, אם קיים
# )
#
# new_recipe.save()  # מתודת השמירה שירשנו מ-BaseModel [cite: 35]
# # --- שלב 5: שמירת רכיבים (Ingredients) ---
# # אנחנו מצפים לקבל מהלקוח מחרוזת JSON שמייצגת רשימת אובייקטים
# ingredients_data = request.form.get('ingredients')
#
# if ingredients_data:
# # המרת הטקסט חזרה לרשימת פייתון
# ingredients_list = json.loads(ingredients_data)
#
# for ing in ingredients_list:
#     new_ingredient = IngredientEntry(
#         product=ing.get('product'),
#         amount=float(ing.get('amount')),
#         unit=ing.get('unit'),
#         recipe_id=new_recipe.id  # הקישור למתכון שיצרנו הרגע!
#     )
# new_ingredient.save()
# return jsonify({
#     "message": "Recipe added successfully",
#     "recipe_id": new_recipe.id,
#     "variations": variation_paths
# }), 201
#
# except Exception as e:
# # במקרה של שגיאה, רצוי להוסיף לוגיקה שמוחקת את התמונות שנוצרו כדי לא ללכלך את השרת
# print(f"Error adding recipe: {e}")
# return jsonify({"message": "Failed to add recipe", "error": str(e)}), 500
#
# # @recipes_bp.route('/all', methods=['GET'])
# # def get_all_recipes():
# # # שליפת כל המתכונים שלא נמחקו
# # recipes = Recipe.query.filter_by(is_deleted=False).all()
# #
# # output = []
# # for r in recipes:
# # output.append({
# # "id": r.id,
# # "title": r.title,
# # "image": r.image_path,
# # "type": r.recipe_type,
# # "variations": json.loads(r.variation_paths) if r.variation_paths else []
# # })
# #
# # return jsonify(output), 200
# # זה מאפשר לכל העולם לגשת לקבצים בתיקיית uploads בלי טוקן
# return send_from_directory('uploads', filename)
#
#
# @recipes_bp.route('/all', methods=['GET'])
# def get_all_recipes():
#     recipes = Recipe.query.filter_by(is_deleted=False).all()
#
#
# output = []
# for r in recipes:
#     output.append({
#         "id": r.id,
#         "title": r.title,
#         "image": r.image_path,
#         "recipe_type": r.recipe_type,  # התאמה לאנגולר
#         "prep_time": r.prep_time,  # הוספה בשביל המיון
#         "avg_rating": r.avg_rating,  # הוספה בשביל הכוכבים
#         "variations": json.loads(r.variation_paths) if r.variation_paths else []
#     })
# return jsonify(output), 200
#
#
# # נתיב ציבורי לתמונות - לא דורש טוקן!
# @recipes_bp.route('/file/<filename>')
# def serve_recipe_image(filename):
#     upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
#
#
# return send_from_directory(upload_folder, filename)
#
#
# # @recipes_bp.route('/all', methods=['GET'])
# # # @jwt_required(optional=True) # <--- הוסיפי את השורה הזו!
# # def get_all_recipes():
# # # שליפת כל המתכונים שלא נמחקו
# # recipes = Recipe.query.filter_by(is_deleted=False).all()
# #
# # # ניסיון לזהות את המשתמש המחובר (כדי לדעת מה הוא סימן כמועדף)
# # # הערה: אם את משתמשת ב-JWT, אפשר להוציא את ה-identity
# # # אם לא נשלח טוקן, user_id יהיה None
# # try:
# # current_user_id = get_jwt_identity()
# # user = User.query.get(current_user_id) if current_user_id else None
# # # recipes = Recipe.query.filter_by(is_deleted=False).all()
# # except:
# # user = None
# #
# # output = []
# # for r in recipes:
# # output.append({
# # "id": r.id,
# # "title": r.title,
# # "image": r.image_path,
# # "recipe_type": r.recipe_type, # שימוש בשם העמודה מה-Model שלך
# # "prep_time": r.prep_time, # חובה בשביל המיון ב-Angular!
# # "avg_rating": r.avg_rating, # חובה בשביל המיון והצגת הכוכבים
# # "variations": json.loads(r.variation_paths) if r.variation_paths else [],
# #
# # # בדיקה האם המתכון הזה נמצא ברשימת המועדפים של המשתמש שצופה כרגע
# # "is_favorite": user in r.favorited_by if user else False
# # })
# #
# # return jsonify(output), 200
# # @recipes_bp.route('/delete/<int:recipe_id>', methods=['DELETE'])
# # @role_required('Uploader') # או Admin
# # def delete_recipe(recipe_id):
# # recipe = Recipe.query.get(recipe_id)
# # if not recipe:
# # return jsonify({"message": "מתכון לא נמצא"}), 404
# #
# # # מחיקה לוגית
# # recipe.is_deleted = True
# # recipe.save()
#
# # return jsonify({"message": "המתכון נמחק בהצלחה (לוגית)"}), 200
#
# # --------------------------------------------------------
# # ------------------------------------------------
#
# # ------------------------------------------------
# # -----------------------ניתוב למתכון בודד----------------------
# @recipes_bp.route('/<int:recipe_id>', methods=['GET'])
# def get_recipe_details(recipe_id):
#     """שליפת פרטי מתכון בודד כולל רכיבים ותמונות"""
#
#
# recipe = Recipe.query.get_or_404(recipe_id)
#
# # הכנת רשימת הרכיבים בפורמט JSON
# ingredients = []
# for ing in recipe.ingredients:
#     ingredients.append({
#         "product": ing.product,
#         "amount": ing.amount,
#         "unit": ing.unit
#     })
#
# return jsonify({
#     "id": recipe.id,
#     "title": recipe.title,
#     "instructions": recipe.instructions,
#     "type": recipe.recipe_type,
#     "image": recipe.image_path,
#     "prep_time": recipe.prep_time,  # <--- הוספת השורה הזו חיונית!
#     "avg_rating": recipe.avg_rating,  # מומלץ להוסיף גם את זה לדירוג
#
#     "variations": json.loads(recipe.variation_paths) if recipe.variation_paths else [],
#     "ingredients": ingredients,
#     "author_id": recipe.user_id
# }), 200
#
#
# # -------------חיפוש מתכון לפי רכיבים-------------------
#
# @recipes_bp.route('/search', methods=['POST'])
# def search_recipes():
#
#
# # שלב 1: הכנת נתונים - קבלת הרשימה מהלקוח והפיכתה ל-Set
# data = request.json
# # רשימת המצרכים שהמשתמש הזין (למשל: ["קמח", "ביצים", "סוכר"])
# user_ingredients_list = data.get('ingredients', [])
# # user_set = set(user_ingredients_list)
# # ניקוי רווחים מהרכיבים של המשתמש
# user_set = {i.strip().lower() for i in user_ingredients_list if i}
#
# # שליפת כל המתכונים מהמסד (רק אלו שלא נמחקו)
# all_recipes = Recipe.query.filter_by(is_deleted=False).all()
# results = []
#
# for recipe in all_recipes:
# # שלב 1 המשך: הכנת ה-Set של המתכון הנוכחי
# # שליפת שמות הרכיבים מתוך הקשר (Relationship) שיצרנו במודל
# # recipe_ingredients_list = [ing.product.strip() for ing in recipe.ingredients]
# # recipe_set = set(recipe_ingredients_list)
# # שימוש ב-Set Comprehension בשורה אחת - יעיל וקריא יותר
# recipe_set = {ing.product.strip().lower() for ing in recipe.ingredients if ing.product}
# if not recipe_set:  # הגנה למקרה של מתכון בלי רכיבים
#     continue
#
# # שלב 2: חישוב רכיבים משותפים (Intersection) באמצעות האופרטור &
# common_ingredients = user_set & recipe_set
#
# # שלב 3: חישוב ציון ההתאמה (Matching Score)
# # נוסחה: (כמות משותפים / סך הכל נדרשים במתכון)
# score = len(common_ingredients) / len(recipe_set)
#
# # שלב 4: סינון (רק מתכונים עם התאמה של מעל 20%)
# if score >= 0.1:
#     results.append({
#         "id": recipe.id,
#         "title": recipe.title,
#         "score": round(score * 100, 2),  # הפיכה לאחוזים (למשל 75.5)
#         "image": recipe.image_path,
#         "matching_count": len(common_ingredients),
#         "missing_ingredients": list(recipe_set - user_set)  # מה חסר למשתמש לקנות
#     })
#
# # שלב 4 המשך: מיון התוצאות בסדר יורד לפי הציון (Score)
# results.sort(key=lambda x: x['score'], reverse=True)
#
# # שלב 4 סיום: שליחת הנתונים ל-Angular
# return jsonify(results), 200
#
#
# # --- מחיקת מתכון (מותאם למנהל) ---
# @recipes_bp.route('/delete/<int:recipe_id>', methods=['DELETE'])
# @jwt_required()
# def delete_recipe(recipe_id):
#     current_user_id = get_jwt_identity()
#
#
# user = User.query.get(current_user_id)
# recipe = Recipe.query.get_or_404(recipe_id)
#
# # בדיקה: רק אם המשתמש הוא מנהל, או שזה המתכון שלו והוא Uploader
# if user.role == 'Admin' or (user.role == 'Uploader' and recipe.user_id == user.id):
#     recipe.is_deleted = True
# recipe.save()
# return jsonify({"message": "המתכון נמחק בהצלחה"}), 200
#
# return jsonify({"message": "אין לך הרשאה למחוק מתכון זה"}), 403
#
# # --- ניהול מועדפים ---
# # @recipes_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
# # @jwt_required()
# # def toggle_favorite(recipe_id):
# # user_id = get_jwt_identity()
# # user = User.query.get(user_id)
# # recipe = Recipe.query.get_or_404(recipe_id)
# #
# # if recipe in user.favorite_recipes:
# # user.favorite_recipes.remove(recipe)
# # message = "הוסר מהמועדפים"
# # is_favorite = False
# # else:
# # user.favorite_recipes.append(recipe)
# # message = "נוסף למועדפים"
# # is_favorite = True
# #
# # db.session.commit()
# # return jsonify({"message": message, "is_favorite": is_favorite}), 200
# # פונקציה להוספה/הסרה מהמועדפים (Toggle)
# # @recipes_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
# # @jwt_required()
import os
import uuid
import json
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter
from flask_jwt_extended import jwt_required, get_jwt_identity

# ייבוא המודלים והדקורטורים שלך
from models import Recipe, db, User, Rating, IngredientEntry
from decorators import role_required, get_current_user

# 1. הגדרת ה-Blueprint
recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')


# --- פונקציות עזר ---

def allowed_file(filename):
    """בדיקה שהקובץ הוא תמונה (סיומת תקינה)"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def apply_sepia(img):
    """פונקציה שמקבלת אובייקט Image ומחזירה אותו בגווני ספיה"""
    img = img.convert("RGB")
    width, height = img.size
    pixels = img.load()

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
    return img


# --- נתיבים (Routes) ---

@recipes_bp.route('/add', methods=['POST'])
@role_required('Uploader')
def add_recipe():
    """הוספת מתכון חדש הכוללת עיבוד תמונה ושמירת רכיבים"""
    try:

        # בדיקה ששדות החובה קיימים בבקשה
        title = request.form.get('title')
        instructions = request.form.get('instructions')

        if not title or not instructions:
            return jsonify({"message": "חובה להזין כותרת והוראות הכנה"}), 400
        # בדיקת קובץ תמונה
        if 'image' not in request.files:
            return jsonify({"message": "No image part in the request"}), 400

        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({"message": "No selected file or invalid file type"}), 400

        # הכנת תיקייה ושמות קבצים
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        unique_id = str(uuid.uuid4())
        extension = secure_filename(file.filename).rsplit('.', 1)[1].lower()
        original_filename = f"{unique_id}_original.{extension}"
        original_path = os.path.join(upload_folder, original_filename)

        # שמירת המקור ועיבוד וריאציות
        file.save(original_path)
        img = Image.open(original_path)
        variation_paths = []

        # וריאציה 1: שחור-לבן
        bw_filename = f"{unique_id}_bw.{extension}"
        img.convert('L').save(os.path.join(upload_folder, bw_filename))
        variation_paths.append(bw_filename)

        # וריאציה 2: Vivid (צבעים עזים)
        vivid_filename = f"{unique_id}_vivid.{extension}"
        enhancer = ImageEnhance.Color(img.copy())
        vivid_img = enhancer.enhance(1.5)
        vivid_img.save(os.path.join(upload_folder, vivid_filename))
        variation_paths.append(vivid_filename)

        # וריאציה 3: ספיה
        sepia_filename = f"{unique_id}_sepia.{extension}"
        sepia_img = apply_sepia(img.copy())
        sepia_img.save(os.path.join(upload_folder, sepia_filename))
        variation_paths.append(sepia_filename)

        # שמירה ב-DB
        current_user = get_current_user()
        prep_time_raw = request.form.get('prep_time')

        new_recipe = Recipe(
            title=request.form.get('title'),
            instructions=request.form.get('instructions'),
            recipe_type=request.form.get('type'),
            image_path=original_filename,
            variation_paths=json.dumps(variation_paths),
            user_id=current_user.id,
            prep_time=int(prep_time_raw) if prep_time_raw else 0,
            avg_rating=0.0,
            is_deleted=False
        )
        new_recipe.save()

        # שמירת רכיבים (Ingredients)
        ingredients_data = request.form.get('ingredients')
        if ingredients_data:
            ingredients_list = json.loads(ingredients_data)
            for ing in ingredients_list:
                new_ingredient = IngredientEntry(
                    product=ing.get('product'),
                    amount=float(ing.get('amount')) if ing.get('amount') else 0,
                    unit=ing.get('unit'),
                    recipe_id=new_recipe.id
                )
                new_ingredient.save()

        return jsonify({"message": "Recipe added successfully", "recipe_id": new_recipe.id}), 201

    except Exception as e:
        print(f"Error adding recipe: {e}")
        return jsonify({"message": "Failed to add recipe", "error": str(e)}), 500


@recipes_bp.route('/all', methods=['GET'])
# @jwt_required(optional=True)  # מאפשר גם לאורחים להיכנס
def get_all_recipes():
    """שליפת כל המתכונים הפעילים"""
    recipes = Recipe.query.filter_by(is_deleted=False).all()
    output = []
    for r in recipes:
        output.append({
            "id": r.id,
            "title": r.title,
            "image": r.image_path,
            "recipe_type": r.recipe_type,
            "prep_time": r.prep_time,
            "avg_rating": r.avg_rating,
            "variations": json.loads(r.variation_paths) if r.variation_paths else []
        })
    return jsonify(output), 200
# @recipes_bp.route('/all', methods=['GET'])
# # @jwt_required(optional=True)  # מאפשר גם לאורחים להיכנס
# def get_all_recipes():
#     current_user_id = get_jwt_identity()
#     recipes = Recipe.query.filter_by(is_deleted=False).all()
#
#     output = []
#     user = User.query.get(current_user_id) if current_user_id else None
#
#     for r in recipes:
#         output.append({
#             "id": r.id,
#             "title": r.title,
#             "image": r.image_path,
#             "recipe_type": r.recipe_type,
#             "prep_time": r.prep_time,
#             "avg_rating": r.avg_rating,
#             "is_favorite": user in r.favorited_by if user else False,  # מסמן אם המשתמש הנוכחי אהב
#             "variations": json.loads(r.variation_paths) if r.variation_paths else []
#         })
#     return jsonify(output), 200

@recipes_bp.route('/<int:recipe_id>', methods=['GET'])
def get_recipe_details(recipe_id):
    """שליפת פרטי מתכון בודד"""
    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = [{"product": i.product, "amount": i.amount, "unit": i.unit} for i in recipe.ingredients]

    return jsonify({
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "type": recipe.recipe_type,
        "image": recipe.image_path,
        "prep_time": recipe.prep_time,
        "avg_rating": recipe.avg_rating,
        "variations": json.loads(recipe.variation_paths) if recipe.variation_paths else [],
        "ingredients": ingredients,
        "author_id": recipe.user_id
    }), 200


@recipes_bp.route('/search', methods=['POST'])
def search_recipes():
    """חיפוש מתכונים לפי רכיבים (Matching Score)"""
    data = request.json
    user_ingredients_list = data.get('ingredients', [])
    user_set = {i.strip().lower() for i in user_ingredients_list if i}

    all_recipes = Recipe.query.filter_by(is_deleted=False).all()
    results = []

    for recipe in all_recipes:
        recipe_set = {ing.product.strip().lower() for ing in recipe.ingredients if ing.product}
        if not recipe_set:
            continue

        common_ingredients = user_set & recipe_set
        score = len(common_ingredients) / len(recipe_set)

        if score >= 0.1:
            results.append({
                "id": recipe.id,
                "title": recipe.title,
                "score": round(score * 100, 2),
                "image": recipe.image_path,
                "matching_count": len(common_ingredients),
                "missing_ingredients": list(recipe_set - user_set)
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(results), 200


@recipes_bp.route('/delete/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    """מחיקה לוגית של מתכון (למנהל או ליוצר המתכון)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    recipe = Recipe.query.get_or_404(recipe_id)

    if user.role == 'Admin' or (user.role == 'Uploader' and recipe.user_id == user.id):
        recipe.is_deleted = True
        recipe.save()
        return jsonify({"message": "המתכון נמחק בהצלחה"}), 200

    return jsonify({"message": "אין לך הרשאה למחוק מתכון זה"}), 403


@recipes_bp.route('/file/<filename>')
def serve_recipe_image(filename):
    """הגשת קבצי התמונות מהשרת"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, filename)


@recipes_bp.route('/my-favorites', methods=['GET'])
@jwt_required()
def get_my_favorites():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    output = []
    for r in user.favorite_recipes:
        output.append({
            "id": r.id,
            "title": r.title,
            "image": r.image_path,
            "avg_rating": r.avg_rating
        })
    return jsonify(output), 200


@recipes_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
@jwt_required()  # חובה להיות מחובר כדי לסמן מועדף
def toggle_favorite(recipe_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe in user.favorite_recipes:
        user.favorite_recipes.remove(recipe)
        status = False
    else:
        user.favorite_recipes.append(recipe)
        status = True

    db.session.commit()
    return jsonify({"is_favorite": status}), 200

#
# @recipes_bp.route('/rate/<int:recipe_id>', methods=['POST'])
# @jwt_required()  # חובה להיות מחובר כדי לדרג
# def rate_recipe(recipe_id):
#     current_user_id = get_jwt_identity()
#     data = request.json
#     new_score = data.get('score')
#
#     if not new_score or not (1 <= new_score <= 5):
#         return jsonify({"message": "Invalid score"}), 400
#
#     # בדיקה אם המשתמש כבר דירג בעבר - אם כן, נעדכן את הדירוג הקיים
#     rating = Rating.query.filter_by(user_id=current_user_id, recipe_id=recipe_id).first()
#
#     if rating:
#         rating.score = new_score
#     else:
#         rating = Rating(score=new_score, user_id=current_user_id, recipe_id=recipe_id)
#         db.session.add(rating)
#
#     db.session.commit()
#
#     # עדכון הממוצע בשדה avg_rating של המתכון (משתמש במתודה שבנית במודל)
#     recipe = Recipe.query.get(recipe_id)
#     recipe.update_avg_rating()
#
#     return jsonify({"message": "Rating updated", "new_avg": recipe.avg_rating}), 200


@recipes_bp.route('/rate/<int:recipe_id>', methods=['POST'])
@jwt_required()
def rate_recipe(recipe_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_score = data.get('score')

    # וולידציה - לוודא שהציון תקין
    if not new_score or not (1 <= new_score <= 5):
        return jsonify({"message": "ציון לא תקין"}), 400

    # בדיקה אם המשתמש כבר דירג - אם כן, נעדכן. אם לא, ניצור חדש.
    rating = Rating.query.filter_by(user_id=current_user_id, recipe_id=recipe_id).first()

    if rating:
        rating.score = new_score
    else:
        rating = Rating(score=new_score, user_id=current_user_id, recipe_id=recipe_id)
        db.session.add(rating)

    db.session.commit()

    # עדכון הממוצע האוטומטי (משתמש במתודה שיש לך במודל)
    recipe = Recipe.query.get(recipe_id)
    recipe.update_avg_rating()

    # החזרת הממוצע החדש כדי שה-Angular יתעדכן מיד במסך
    return jsonify({
        "message": "Rating saved",
        "new_average": recipe.avg_rating
    }), 200


@recipes_bp.route('/update/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id):
    """עדכון פרטי מתכון קיים (כותרת, הוראות, סוג, זמן הכנה ורכיבים)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        recipe = Recipe.query.get_or_404(recipe_id)

        # בדיקת הרשאות: רק המנהל או המשתמש שהעלה את המתכון יכולים לערוך
        if user.role != 'Admin' and recipe.user_id != int(current_user_id):
            return jsonify({"message": "אין לך הרשאה לערוך מתכון זה"}), 403

        # קבלת הנתונים מהבקשה (JSON)
        data = request.json
        if not data:
            return jsonify({"message": "לא התקבלו נתונים לעדכון"}), 400

        # 1. עדכון שדות בסיסיים של המתכון
        recipe.title = data.get('title', recipe.title)
        recipe.instructions = data.get('instructions', recipe.instructions)
        recipe.recipe_type = data.get('type', recipe.recipe_type)

        # טיפול בזמן הכנה (וודוא שזה מספר)
        if 'prep_time' in data:
            recipe.prep_time = int(data['prep_time'])

        # 2. עדכון רכיבים (Ingredients)
        # הגישה המקצועית: מוחקים את הישנים ויוצרים חדשים כדי למנוע כפילויות או בלאגן
        if 'ingredients' in data:
            # מחיקת הרכיבים המשויכים למתכון הזה
            IngredientEntry.query.filter_by(recipe_id=recipe.id).delete()

            # הוספת הרכיבים החדשים מתוך הרשימה שהגיעה
            for ing in data['ingredients']:
                new_ingredient = IngredientEntry(
                    product=ing.get('product'),
                    amount=float(ing.get('amount')) if ing.get('amount') else 0,
                    unit=ing.get('unit'),
                    recipe_id=recipe.id
                )
                db.session.add(new_ingredient)

        # 3. שמירה סופית למסד הנתונים
        recipe.save()
        # הערה: המתודה save() שלך מבצעת commit, אז הכל יישמר יחד.

        return jsonify({
            "message": "המתכון עודכן בהצלחה!",
            "recipe_id": recipe.id
        }), 200

    except Exception as e:
        print(f"Error updating recipe: {e}")
        db.session.rollback()  # ביטול שינויים במקרה של תקלה
        return jsonify({"message": "עדכון המתכון נכשל", "error": str(e)}), 500