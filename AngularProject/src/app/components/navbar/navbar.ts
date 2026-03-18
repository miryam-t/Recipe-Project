import { CommonModule } from '@angular/common';
import { Component, HostListener } from '@angular/core';
import { NavigationEnd, Router, RouterModule } from '@angular/router'; // ייבוא כלים לניהול ניווט וקישורים
import { filter } from 'rxjs'; // כלי לסינון אירועים
import { AuthService } from '../services/auth'; // ייבוא שירות האימות שלנו

@Component({
  selector: 'app-navbar',
  standalone: true, // מגדיר את הקומפוננטה כעצמאית
  imports: [CommonModule, RouterModule], // ייבוא מודלים הכרחיים להצגת תנאים וקישורים
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar {
  isHomePage: boolean = false; // משתנה שיגיד לנו אם אנחנו בדף הבית
  isScrolled: boolean = false; // משתנה חדש למעקב אחרי גלילה

  // הזרקת השירותים ב-Constructor
  constructor(public auth: AuthService, private router: Router) {
    // האזנה לכל אירוע ניווט באתר
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd) // נתמקד רק ברגע שהניווט הסתיים בהצלחה
    ).subscribe((event: any) => {
      // בדיקה: האם הכתובת הנוכחית היא דף הבית ('/home' או רק '/')
      this.isHomePage = event.url === '/home' || event.url === '/' || event.urlAfterRedirects === '/home';
    });
  }

  // פונקציה שמאזינה לגלילה של המשתמש
  @HostListener('window:scroll', [])
  onWindowScroll() {
    // אם המשתמש גלל יותר מ-50 פיקסלים, נשנה את מצב הנאבבאר
    this.isScrolled = window.scrollY > 50;
  }

  // פונקציית התנתקות שקוראת ל-Service
  onLogout() {
    this.auth.logout();
    this.router.navigate(['/login']); // אחרי התנתקות נעבור לדף כניסה
  }
}
