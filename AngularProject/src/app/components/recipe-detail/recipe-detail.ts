import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { RecipeService } from '../services/recipe';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-recipe-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './recipe-detail.html',
  styleUrl: './recipe-detail.css'
})
export class RecipeDetail implements OnInit {
  recipe: any = null;

  activeImage: string = ''; // המשתנה שיחזיק את התמונה שמוצגת בגדול
  constructor(
    private route: ActivatedRoute,
    private recipeService: RecipeService
  ) { }

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.recipeService.getRecipeById(id).subscribe({
      next: (data) => {
        this.recipe = data;
        console.log('נתוני המתכון המלאים מהשרת:', data); // <--- השורה הזו תראה לך בקונסול את שמות השדות
        this.activeImage = data.image;
      },// בהתחלה מציגים את התמונה המקורית
      error: (err) => console.error('Error fetching recipe', err)
    });
  }
  printRecipe() {
    window.print();
  }
  // פונקציה להחלפת התמונה
  changeImage(imgName: string) {
    this.activeImage = imgName;
  }
}