import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth';
import { User } from '../../models/recipe';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { RouterModule } from '@angular/router';
import Swal from 'sweetalert2';
import { RecipeService } from '../services/recipe';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,

  ],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {
  user: User | null = null;
  userImageUrl: string = '/1.JPG';
  isPending: boolean = false;
  myFavoriteRecipes: any[] = [];
  showFavorites: boolean = false;
  favoritesCount: number = 0;

  constructor(public auth: AuthService, private recipeService: RecipeService) { }

  ngOnInit() {
    this.auth.refreshUserStatus();
    this.user = this.auth.currentUser;
    this.userImageUrl = this.auth.currentUserImageUrl || '/1.JPG';

    if (this.user?.is_approved_uploader) {
      this.isPending = true;
    }
  }

  // תיקון השם ל-toggleFavorites (עם s) כדי שיתאים למה שקראת לו קודם
  // ושימוש ב-toggleFavorite (בלי s) עבור ה-Service
  toggleFavorites() {
    if (this.showFavorites) {
      this.showFavorites = false;
      return;
    }

    this.recipeService.getMyFavorites().subscribe({
      next: (data: any[]) => { // הוספת : any[]
        this.myFavoriteRecipes = data;
        this.favoritesCount = data.length;
        this.showFavorites = true;
      },
      error: (err: any) => { // הוספת : any
        console.error("Error loading favorites", err);
        Swal.fire('שגיאה', 'לא הצלחנו לטעון את המועדפים שלך', 'error');
      }
    });
  }

  removeFromFavorites(recipeId: number) {
    // כאן אנחנו משתמשים בשם המדויק שבתוך ה-Service שלך
    this.recipeService.toggleFavorite(recipeId).subscribe({
      next: (res: any) => {
        this.myFavoriteRecipes = this.myFavoriteRecipes.filter(r => r.id !== recipeId);
        this.favoritesCount = this.myFavoriteRecipes.length;
        Swal.fire({
          toast: true,
          position: 'top-end',
          icon: 'success',
          title: 'הוסר מהמועדפים',
          showConfirmButton: false,
          timer: 1500
        });
      },
      error: (err: any) => {
        Swal.fire('שגיאה', 'לא הצלחנו להסיר מהמועדפים', 'error');
      }
    });
  }

  getUserRoleLabel(): string {
    if (!this.user) return 'אורח';
    switch (this.user.role) {
      case 'Admin': return 'מנהל מערכת';
      case 'Uploader': return 'משתמש תוכן (בשלן)';
      default: return 'משתמש רגיל';
    }
  }

  requestUploaderStatus() {
    this.auth.sendUpgradeRequest().subscribe({
      next: (res: any) => {
        if (this.auth.currentUser) {
          this.auth.currentUser.has_requested_upgrade = true;
          localStorage.setItem('user', JSON.stringify(this.auth.currentUser));
        }

        Swal.fire({
          title: 'הבקשה נשלחה!',
          text: 'מנהל המערכת קיבל את בקשתך ויאשר אותה בהקדם.',
          icon: 'success',
          confirmButtonText: 'מעולה'
        });
      },
      error: (err: any) => {
        Swal.fire('שגיאה', 'לא הצלחנו לשלוח את הבקשה', 'error');
      }
    });
  }
}