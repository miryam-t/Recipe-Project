import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { Recipe } from '../../models/recipe';
import { AuthService } from './auth';

@Injectable({ providedIn: 'root' })
export class RecipeService {
  
  private baseUrl = 'http://127.0.0.1:5000/recipes'; // כתובת השרת עבור מתכונים

  constructor(private http: HttpClient, private auth: AuthService) {}
  token = localStorage.getItem('token'); // ודאי שהשם זהה למה ששמרת ב-Login

getRecipes(type?: string, maxTime?: number): Observable<any[]> {
  const token = localStorage.getItem('token');
  let params = '';
  
  // בניית ה-Query Params לסינון
  if (type || maxTime) {
    params = `?type=${type || ''}&max_time=${maxTime || ''}`;
  }

  const headers = new HttpHeaders({
    'Authorization': `Bearer ${token}`
  });

  return this.http.get<any[]>(`${this.baseUrl}/all${params}`, { headers });
}
 

  // אלגוריתם החיפוש: שליחת רשימת רכיבים וקבלת מתכונים ממוינים לפי ציון [cite: 77, 131, 132]
  searchByIngredients(ingredients: string[]): Observable<any[]> {
    // השוואת הסטים (Sets) מתבצעת בשרת פייתון [cite: 116, 122]
    return this.http.post<any[]>(`${this.baseUrl}/search`, { ingredients });
  }

uploadRecipe(formData: FormData): Observable<any> {
  // 1. שליפת הטוקן שקיבלת ב-Login ונשמר ב-LocalStorage
  const token = localStorage.getItem('token'); 
  
  // 2. יצירת ה-Headers עם המילה Bearer (חובה!)
  const headers = new HttpHeaders({
    'Authorization': `Bearer ${token}` 
  });

  // 3. שליחת הבקשה עם ה-Headers
  return this.http.post(`${this.baseUrl}/add`, formData, { headers });
}

  // פונקציה לשליפת פרטי מתכון בודד לפי ה-ID שלו
getRecipeById(id: number): Observable<any> {
  return this.http.get<any>(`${this.baseUrl}/${id}`);
}
// פונקציה לדירוג מתכון - שולחת את הציון לשרת הפייתון
  rateRecipe(recipeId: number, score: number): Observable<any> {
    const token = localStorage.getItem('token'); // שליפת הטוקן לזיהוי המשתמש המדרג
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    // שליחת ה-score בתוך ה-body של בקשת ה-POST
    return this.http.post(`${this.baseUrl}/rate/${recipeId}`, { score }, { headers });
  }
  // recipe.service.ts

// פונקציה למחיקת מתכון (עבור אדמין/יוצר)
deleteRecipe(id: number): Observable<any> {
  const token = localStorage.getItem('token');
  const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
  return this.http.delete(`${this.baseUrl}/delete/${id}`, { headers });
}

// פונקציה לניהול מועדפים (Toggle)
// ודאי שזה מופיע ככה ב-RecipeService
toggleFavorite(recipeId: number): Observable<any> {
  const token = localStorage.getItem('token');
  const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
  return this.http.post(`${this.baseUrl}/favorite/${recipeId}`, {}, { headers });
}
getMyFavorites(): Observable<any[]> {
  const token = localStorage.getItem('token');
  const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
  
  // פנייה לנתיב החדש שיצרנו בפייתון
  return this.http.get<any[]>(`${this.baseUrl}/my-favorites`, { headers });
}
// פונקציה למיון לפי דירוג (מבוסס על השדה avg_rating שהוספת ב-Model)
sortRecipesByRating(recipes: any[]): any[] {
  return recipes.sort((a, b) => (b.avg_rating || 0) - (a.avg_rating || 0));
}
}