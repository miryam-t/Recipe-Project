import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Navbar } from './components/navbar/navbar';
import { Home } from './components/home/home';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

// הגדרת המבנה המדויק שחוזר מהשרת (Flask)
export interface LoginResponse {
  user_id: number;
  role: string;
  message: string;
}

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,      // כדי שה-router-outlet יעבוד
    Navbar,    // כדי שה-app-navbar יהיה מוכר!
    Home    // מאפשר להשתמש ב <app-home>
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  // protected readonly title = signal('AngularProject');
  title = 'recipe-project';
  private baseUrl = 'http://127.0.0.1:5000';

  public isLoggedIn: boolean = false;
  // הגדרת טיפוס מדויק למשתמש המחובר כדי למנוע שגיאות Property does not exist
  public currentUser: { id: number, role: string, username: string } | null = null;

  constructor(private http: HttpClient) {
    this.loadUserFromStorage(); // טעינת משתמש בטעינת הדף
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/register`, userData);
  }

  login(credentials: any): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/users/login`, credentials).pipe(
      tap(response => {
        this.isLoggedIn = true;
        this.currentUser = {
          id: response.user_id,
          role: response.role,
          username: credentials.username // השם שהוזן בטופס
        };
      })
    );
  }

  private loadUserFromStorage() {
    const id = localStorage.getItem('user_id');
    const role = localStorage.getItem('user_role');
    const name = localStorage.getItem('user_name');

    if (id && role && name) {
      this.isLoggedIn = true;
      this.currentUser = { id: +id, role: role, username: name };
    }
  }

  getRecipes(): Observable<any> {
    return this.http.get(`${this.baseUrl}/recipes/all`);
  }

  logout() {
    this.isLoggedIn = false;
    this.currentUser = null;
    localStorage.clear();
  }
}