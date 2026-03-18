import { Component, OnInit } from '@angular/core';
import { RecipeService } from '../services/recipe';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home implements OnInit {
  allRecipes: any[] = [];
  filteredRecipes: any[] = [];
  featuredRecipes: any[] = [];

  currentSlide: number = 0;
  filterType: string = 'All';
  searchQuery: string = '';
  isLoading: boolean = true;
  minRating: number = 0;

  aboutText: string = "ברוכים הבאים לפלטפורמת המתכונים שלנו. כאן תמצאו השראה לכל ארוחה...";
  displayAbout: string = "";

  constructor(private recipeService: RecipeService) { }

  ngOnInit() {
    this.runTypewriter(); // אפקט הכתיבה
    this.loadAllRecipes(); // טעינת המתכונים מהשרת
  }

  runTypewriter() {
    let i = 0;
    const interval = setInterval(() => {
      this.displayAbout += this.aboutText.charAt(i);
      i++;
      if (i === this.aboutText.length) clearInterval(interval);
    }, 200);
  }

  loadAllRecipes() {
    this.isLoading = true;
    this.recipeService.getRecipes().subscribe({
      next: (recipes) => {
        this.allRecipes = recipes;
        this.filteredRecipes = [...recipes];
        // לקיחת 4 המתכונים האחרונים לקרוסלה
        this.featuredRecipes = recipes.slice(-4);
        this.isLoading = false;
        this.startCarousel();
      },
      error: (err) => {
        console.error('שגיאה בטעינת נתונים:', err);
        this.isLoading = false;
      }
    });
  }

  startCarousel() {
    if (this.featuredRecipes.length > 0) {
      setInterval(() => {
        this.currentSlide = (this.currentSlide + 1) % this.featuredRecipes.length;
      }, 5000);
    }
  }

  rate(recipe: any, stars: number) { // שימוש ב-any מאפשר להוסיף שדות דינמית
    this.recipeService.rateRecipe(recipe.id, stars).subscribe({
      next: (res: any) => {
        // res.new_average הוא השם שחוזר מה-jsonify ב-Python
        recipe.avg_rating = res.new_average;

        // כדי ש-Angular יצבע את הכוכבים, אנחנו שומרים את הדירוג שהמשתמש נתן כרגע
        recipe['userRating'] = stars;

        Swal.fire({
          title: 'תודה על הדירוג!',
          text: `דירגת את ${recipe.title} ב-${stars} כוכבים`,
          icon: 'success',
          timer: 2000, // נסגר לבד אחרי 2 שניות
          showConfirmButton: false,
          background: '#FFFDF5',
          color: '#3E2723',
          iconColor: '#556B2F'
        });
      },
      error: (err) => {
        console.error(err);
        Swal.fire({
          title: 'אופס...',
          text: 'וודאי שאת מחוברת כדי לדרג מתכונים',
          icon: 'info',
          confirmButtonColor: '#D2691E'
        });
      }
    });
  }

  // סינון מקומי משולב - שימי לב לשמות השדות התואמים ל-DB
  applyFilter() {
    this.filteredRecipes = this.allRecipes.filter(r => {
      const matchType = this.filterType === 'All' || r.recipe_type === this.filterType;
      const matchSearch = r.title.toLowerCase().includes(this.searchQuery.toLowerCase());
      const matchRating = (r.avg_rating || 0) >= this.minRating;
      return matchType && matchSearch && matchRating;
    });
  }

  // מיון מקצועי (לפי דירוג או זמן הכנה כפי שנדרש בפרויקט)
  sortRecipes(criterion: string) {
    if (criterion === 'rating') {
      this.filteredRecipes.sort((a, b) => (b.avg_rating || 0) - (a.avg_rating || 0));
    } else if (criterion === 'prep_time') {
      this.filteredRecipes.sort((a, b) => (a.prep_time || 0) - (b.prep_time || 0));
    }
  }
}