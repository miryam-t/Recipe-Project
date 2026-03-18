import { HttpClient } from '@angular/common/http'; // ייבוא הכלי לביצוע בקשות HTTP לשרת [cite: 9]
import { Injectable } from '@angular/core'; // מאפשר להזריק את השירות לקומפוננטות אחרות
import { BehaviorSubject, Observable, tap } from 'rxjs'; // טיפול בנתונים שחוזרים מהשרת בצורה אסינכרונית
import { User } from '../../models/recipe'; // ייבוא ה"חוזה" שמגדיר איך נראה משתמש [cite: 110]

@Injectable({ providedIn: 'root' }) // הגדרה שהשירות זמין לכל האפליקציה

export class AuthService {

  private baseUrl = 'http://127.0.0.1:5000/users'; // כתובת השרת (Flask) עבור משתמשים [cite: 82]
  currentUser: User | null = null; // משתנה ששומר את פרטי המשתמש שמחובר כרגע [cite: 94]
// שימוש ב-BehaviorSubject מאפשר לכל האפליקציה "להאזין" למצב המשתמש בזמן אמת
  private userSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.userSubject.asObservable();
  
  constructor(private http: HttpClient) {
    // בבדיקה בטעינת האתר: האם המשתמש כבר שמור בזיכרון הדפדפן?
    const savedUser = localStorage.getItem('user'); 
    if (savedUser) this.currentUser = JSON.parse(savedUser); // אם כן, נטען אותו לתוך האפליקציה
  }

  // פונקציית עזר לבדיקה מהירה: האם יש משתמש מחובר? 
  get isLoggedIn(): boolean { return !!this.currentUser; }

currentUserImageUrl: string = '1.JPG'; // ברירת מחדל

  // פונקציה לעדכון התמונה (תיקרא מדף הלוגין)
  setProfileImage(base64Image: string) {
    this.currentUserImageUrl = base64Image;
  }

  // שליחת נתוני הרשמה לשרת 
  register(userData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/register`, userData);
  }

  // ביצוע כניסה ושמירת הנתונים 
  login(credentials: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/login`, credentials).pipe(
      tap(res => {
         // שמירת הטוקן בנפרד לשימוש בבקשות עתידיות
      localStorage.setItem('token', res.token); 
      
        // לאחר הצלחה, נשמור את הפרטים (ID ותפקיד) בזיכרון [cite: 112]
        this.currentUser = {
          id: res.user_id, // המזהה הייחודי מה-DB [cite: 112]
          username: credentials.username,
          role: res.role, // האם הוא Admin, Uploader או Reader [cite: 112]
          email: '', 
          is_approved_uploader: res.role !== 'Reader', // האם הוא מורשה להעלות מתכונים [cite: 112]
          has_requested_upgrade: res.has_requested_upgrade || false
        };
        // שמירה פיזית בדפדפן כדי שלא יימחק בריענון [cite: 43, 48]
        localStorage.setItem('user', JSON.stringify(this.currentUser));
      })
    );
  }

sendUpgradeRequest(): Observable<any> {
  // הוספת ה-Headers עם הטוקן כדי שהשרת יזהה מי המשתמש
  return this.http.post(`${this.baseUrl}/request_uploader`, {}, this.getAuthHeaders());
}

// פונקציה לרענון נתוני המשתמש המחובר מהשרת
refreshUserStatus(): void {
  if (this.currentUser) {
    // אנו פונים לנתיב בשרת שמחזיר את נתוני המשתמש לפי ה-ID שלו
    this.http.get<any>(`${this.baseUrl}/profile/${this.currentUser.id}`).subscribe(res => {
      // עדכון המשתנה המקומי ב-Service
      this.currentUser = {
        ...this.currentUser!,
        role: res.role,
        is_approved_uploader: res.is_approved_uploader
      };
      // עדכון ה-LocalStorage כדי שהשינוי יישמר בריענון
      localStorage.setItem('user', JSON.stringify(this.currentUser));
    });
  }
}


private getAuthHeaders() {
  
  const token = localStorage.getItem('token');
  return {
    // 'Authorization': `Bearer ${token}`
    headers: { 'Authorization': `Bearer ${token}` } // שימי לב לרווח אחרי ה-Bearer
  };
}

getPendingUsers(): Observable<any[]> {
  return this.http.get<any[]>(`${this.baseUrl}/pending_uploaders`, this.getAuthHeaders());
}
// פונקציית עזר לבדיקת תפקיד המשתמש מהרכיב (Component)
getUserRole(): string {
  return this.currentUser ? this.currentUser.role : 'Reader';
}
// אישור משתמש ספציפי - מעודכן עם Headers
approveUser(userId: number): Observable<any> {
  // שימי לב: שיניתי ל-approve_user כדי שיתאים לשם הפונקציה שקראת לה ב-admin-dashboard.ts
  return this.http.post(`${this.baseUrl}/approve/${userId}`, {}, this.getAuthHeaders());
}

  // התנתקות - מחיקת הנתונים מהזיכרון
  logout() {
   
  // מחיקת כל הנתונים מה-LocalStorage
  localStorage.removeItem('token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('role');
  localStorage.removeItem('username');
  
  // רענון הדף כדי שהאפליקציה תתאפס
  window.location.href = '/login';

    this.currentUser = null;
    localStorage.removeItem('user');
  }

}
