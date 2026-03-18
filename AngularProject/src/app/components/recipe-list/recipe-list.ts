import { Component, OnInit } from '@angular/core';
import { RecipeService } from '../services/recipe';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../services/auth';
import { FormsModule } from '@angular/forms'; // <--- חובה להוסיף עבור הסינונים
import Swal from 'sweetalert2';

@Component({
  selector: 'app-recipe-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule], // <--- הוספנו FormsModule
  templateUrl: './recipe-list.html',
  styleUrl: './recipe-list.css'
})
export class RecipeList implements OnInit {
  recipes: any[] = [];          // הרשימה הגולמית מהשרת
  filteredRecipes: any[] = [];  // הרשימה שמוצגת בפועל
  isLoading: boolean = true;
  isEditMode: boolean = false;
  minRating: number = 0;
  // משתני סינון (מחוברים ל-HTML עם ngModel)
  searchTerm: string = '';
  selectedType: string = 'All';
  sortBy: string = 'newest';

  constructor(private recipeService: RecipeService, public auth: AuthService) { }
  ngOnInit(): void {
    this.isLoading = true; // התחלת טעינה
    this.recipeService.getRecipes().subscribe({
      next: (data) => {
        this.recipes = data;
        this.filteredRecipes = data;
        this.isLoading = false; // סיום טעינה
      },
      error: (err) => {
        console.error('שגיאה בטעינת מתכונים', err);
        this.isLoading = false;
      }
    });
  }

  // עדכון חיפוש רכיבים כדי שיחליף את הגלריה באותו דף
  searchByIngredients(input: string) {
    if (!input.trim()) {
      this.filteredRecipes = [...this.recipes]; // אם ריק, מחזירים הכל
      return;
    }

    const ingredientsArray = input.split(',').map(i => i.trim());
    this.isLoading = true;

    this.recipeService.searchByIngredients(ingredientsArray).subscribe({
      next: (results) => {
        // כאן אנחנו מעדכנים את filteredRecipes בתוצאות מהשרת (כולל ה-Score)
        this.filteredRecipes = results;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('שגיאה בחיפוש רכיבים:', err);
        this.isLoading = false;
      }
    });
  }

  onRate(recipe: any, score: number): void {
    console.log("שולח דירוג למתכון:", recipe.id, "ציון:", score);
    this.recipeService.rateRecipe(recipe.id, score).subscribe({
      next: (res) => {
        console.log("תשובה מהשרת לאחר דירוג:", res);
        recipe.avg_rating = res.new_average;
      },
      error: (err) => console.error("שגיאה בדירוג:", err)
    });
  }


  rate(recipe: any, stars: number) { // שימוש ב-any מאפשר להוסיף שדות דינמית
    this.recipeService.rateRecipe(recipe.id, stars).subscribe({
      next: (res: any) => {
        // res.new_average הוא השם שחוזר מה-jsonify ב-Python
        recipe.avg_rating = res.new_average;

        // כדי ש-Angular יצבע את הכוכבים, אנחנו שומרים את הדירוג שהמשתמש נתן כרגע
        recipe['userRating'] = stars;

        alert('הדירוג עודכן בהצלחה!');
      },
      error: (err) => {
        console.error(err);
        alert('חלה שגיאה: וודאי שאת מחוברת למערכת');
      }
    });
  }

  applyFilters(): void {
    let result = [...this.recipes];

    // סינון טקסט
    if (this.searchTerm) {
      result = result.filter(r => r.title.toLowerCase().includes(this.searchTerm.toLowerCase()));
    }

    // סינון כשרות - חשוב שה-Value ב-HTML יהיה זהה ל-String ב-DB
    if (this.selectedType !== 'All') {
      result = result.filter(r => r.recipe_type === this.selectedType);

    }

    // סינון דירוג - שימוש ב-0 כברירת מחדל אם אין דירוג
    if (this.minRating > 0) {
      result = result.filter(r => (r.avg_rating || 0) >= this.minRating);
    }

    // מיון
    result.sort((a, b) => {
      if (this.sortBy === 'prep_time') return (a.prep_time || 0) - (b.prep_time || 0);
      if (this.sortBy === 'rating') return (b.avg_rating || 0) - (a.avg_rating || 0);
      return b.id - a.id; // הכי חדש
    });

    this.filteredRecipes = result;
  }

  toggleFav(recipe: any) {
    this.recipeService.toggleFavorite(recipe.id).subscribe({
      next: (res) => {
        // res.is_favorite מגיע מה-Flask
        // אנחנו מעדכנים את recipe.is_favorite כדי שה-HTML יזהה
        recipe.is_favorite = res.is_favorite;
      },
      error: (err) =>
        Swal.fire({
          icon: 'warning',
          title: 'שימי לב',
          text: 'צריך להיות מחובר כדי לשמור מועדפים!',
          confirmButtonText: 'להתחברות',
          confirmButtonColor: '#f8bb86'
        })

    });
  }
  onDelete(id: number): void {
    if (confirm('האם את בטוחה?')) {
      this.recipeService.deleteRecipe(id).subscribe({
        next: () => {
          this.recipes = this.recipes.filter(r => r.id !== id);
          this.applyFilters(); // עדכון התצוגה לאחר מחיקה
        }
      });
    }
  }

  // מיון רשימת המתכונים
  sortRecipes(criterion: string) {
    if (criterion === 'score') {
      this.filteredRecipes.sort((a, b) => (b.score || 0) - (a.score || 0));
    } else if (criterion === 'rating') {
      this.filteredRecipes.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    }
  }

  setRatingFilter(stars: number) {
    this.minRating = stars;
    this.applyFilters();
  }

  toggleEditMode(): void {
    this.isEditMode = !this.isEditMode;
  }
}