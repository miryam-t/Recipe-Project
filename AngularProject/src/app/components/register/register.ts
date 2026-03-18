import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth'; // ייבוא השירות שבנינו
import Swal from 'sweetalert2';

@Component({
  selector: 'app-register',
  standalone: true, // הגדרה כקומפוננטה עצמאית
  imports: [FormsModule], // חובה כדי להשתמש ב-ngModel ב-HTML
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  // אובייקט הנתונים שקשור לטופס
  userData = {
    username: '',
    email: '',
    password: ''
  };

  // הזרקת השירותים - כאן קבעת שהשם הוא 'auth' בתוך הקומפוננטה
  constructor(private auth: AuthService, private router: Router) {}

  onRegister() {
    // התיקון: משתמשים ב-this.auth (השם מה-Constructor) ולא בשם ה-Class
    this.auth.register(this.userData).subscribe({

      next: (response: any) => {
        Swal.fire({
  icon: 'success',
  title: 'ברוכה הבאה!',
  text: 'ההרשמה בוצעה בהצלחה! כעת תוכלי להתחבר.',
  confirmButtonText: 'מעולה',
  confirmButtonColor: '#3085d6'
});
       
        this.router.navigate(['/login']); // מעבר אוטומטי לדף התחברות
      },
      error: (err: any) => {
        // טיפול בשגיאה מהשרת (למשל אם המשתמש כבר קיים)
        Swal.fire({
  icon: 'error',
  title: 'שגיאה בהרשמה',
  text: err.error?.message || 'נסה שוב מאוחר יותר',
  confirmButtonText: 'הבנתי',
  confirmButtonColor: '#d33'
});
       
      }
    });
  }
}