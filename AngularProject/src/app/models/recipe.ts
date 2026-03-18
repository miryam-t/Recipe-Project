// מודל משתמש - תואם למחלקת User ב-Python
export interface User {
    id: number;
    username: string;
    email: string;
    role: 'Admin' | 'Uploader' | 'Reader';
    is_approved_uploader: boolean;
    // is_approved_uploader: boolean;
    has_pending_request?: boolean; // השדה שדיברנו עליו קודם
    has_requested_upgrade: boolean;

    // הסימן שאלה (?) אומר לאנגולר: "השדה הזה לא תמיד חובה", זה מונע שגיאות אם הוא טרם נטען
}

// מודל רכיב - תואם למחלקת IngredientEntry ב-Python
export interface Ingredient {
    product: string;
    amount: number;
    unit: string;
}

// מודל מתכון - תואם למחלקת Recipe ב-Python
export interface Recipe {
    id?: number; // סימן השאלה אומר שזה אופציונלי (כי כשיוצרים מתכון חדש עדיין אין לו ID)
    title: string;
    instructions: string;
    recipe_type: string; // Dairy, Meat, Parve
    image_path: string;  // שם הקובץ המקורי
    variation_paths: string[]; // מערך של שמות קבצים (שחור-לבן, סיבוב וכו')
    ingredients: Ingredient[];
    user_id: number;
     is_favorite: boolean;
    is_deleted?: boolean;
}

// מודל לתשובת החיפוש (עם הציון שהוספת בפייתון)
export interface SearchResult {
    id: number;
    title: string;
    score: number;
    image: string;
    matching_count: number;
    missing_ingredients: string[];
}