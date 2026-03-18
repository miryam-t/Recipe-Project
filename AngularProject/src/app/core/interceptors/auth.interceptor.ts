import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('token'); // שליפת הטוקן ששמרת ב-Login

  // אם יש טוקן, נשכפל את הבקשה ונוסיף לה את ה-Header
  if (token) {
    const cloned = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    return next(cloned);
  }

  // אם אין טוקן, נשלח את הבקשה המקורית
  return next(req);
};