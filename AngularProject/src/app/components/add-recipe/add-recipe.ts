import { Component } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { RecipeService } from '../services/recipe';
import { RouterModule } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-add-recipe',
  imports: [RouterModule,
    MatFormFieldModule,
    CommonModule,
    MatFormFieldModule,
    ReactiveFormsModule, 
    MatInputModule,
    MatIconModule,
  ],
  templateUrl: './add-recipe.html',
  styleUrl: './add-recipe.css'
})
export class AddRecipe {
  recipeForm: FormGroup;
  selectedFile: File | null = null;
// הוספת משתנה למחלקה
imagePreview: string | ArrayBuffer | null = null;
  constructor(private fb: FormBuilder, private recipeService: RecipeService) {
 
this.recipeForm = this.fb.group({
  title: ['', Validators.required],
  instructions: ['', Validators.required],
  type: ['Parve', Validators.required],
  prep_time: [null, [Validators.required, Validators.min(1)]], // <-- הוסיפי את זה
  ingredients: this.fb.array([])
});
this.addIngredient();
  }

  // עזר לגישה לרכיבים
  get ingredients() {
    return this.recipeForm.get('ingredients') as FormArray;
  }

  addIngredient() {
    const ingredientGroup = this.fb.group({
      product: ['', Validators.required],
      amount: [0, [Validators.required, Validators.min(0.1)]],
      unit: ['', Validators.required]
    });
    this.ingredients.push(ingredientGroup);
  }

  removeIngredient(index: number) {
    this.ingredients.removeAt(index);
  }

  
onSubmit() {
  // בתחילת פונקציית ה-onSubmit
Swal.fire({
  title: 'מעלה את המתכון...',
  didOpen: () => {
    Swal.showLoading();
  },
  allowOutsideClick: false, // מונע סגירה בזמן הטעינה
  background: '#FFFDF5'
});
  console.log("Form Status:", this.recipeForm.status); // תבדקי מה מודפס כאן!
  if (this.recipeForm.invalid || !this.selectedFile) {
    Swal.fire({
      title: 'אופס... משהו חסר',
      text: 'נא לוודא שכל שדות החובה מלאים (אל תשכחי תמונה!)',
      icon: 'warning',
      confirmButtonText: 'הבנתי, אבדוק שוב',
      confirmButtonColor: '#D2691E',
      background: '#FFFDF5',
      color: '#3E2723'
    });
    return;
  }
  if (this.recipeForm.invalid || !this.selectedFile) return;

  const formData = new FormData();
  formData.append('title', this.recipeForm.value.title);
  formData.append('instructions', this.recipeForm.value.instructions);
  formData.append('type', this.recipeForm.value.type);
  formData.append('prep_time', this.recipeForm.value.prep_time);
  formData.append('image', this.selectedFile);
  formData.append('ingredients', JSON.stringify(this.recipeForm.value.ingredients));

  // הוסיפי את ה-ID של המשתמש כאן (תלוי מאיפה את מושכת אותו, למשל מ-localStorage)
  const userId = localStorage.getItem('user_id'); 
  if (userId) {
    formData.append('user_id', userId);
  }

  this.recipeService.uploadRecipe(formData).subscribe({
    next: (res) => {
      Swal.fire({
      title: 'המתכון פורסם בהצלחה!',
      text: 'היצירה הקולינרית שלך מחכה לכולם באתר',
      icon: 'success',
      confirmButtonText: 'מעולה!',
      confirmButtonColor: '#D2691E', // צבע הטרקוטה שלך
      background: '#FFFDF5',      // צבע השמנת של האתר
      color: '#3E2723',           // צבע הטקסט החום
      iconColor: '#556B2F'        // ירוק זית לאייקון ה-V
    });
      this.recipeForm.reset();
    },
    error: (err) => {
      console.error('Error details:', err);
// הודעת שגיאה במקרה של בעיה בשרת או בתקשורת
      Swal.fire({
        title: 'שגיאה בשמירת המתכון',
        text: 'משהו השתבש בדרך... כדאי לנסות שוב מאוחר יותר',
        icon: 'error',
        confirmButtonText: 'סגור',
        confirmButtonColor: '#AE2012', // אדום יין עמוק שמתאים לסגנון
        background: '#FFFDF5',
        color: '#3E2723'
      });
    }
  });
}

onFileSelected(event: any) {
  // 1. השמירה המקורית שלך
  this.selectedFile = event.target.files[0];

  // 2. הוספת תצוגה מקדימה (אופליין לחלוטין)
  if (this.selectedFile) {
    const reader = new FileReader();
    reader.onload = () => {
      this.imagePreview = reader.result; // המשתנה הזה יוצג ב-HTML
    };
    reader.readAsDataURL(this.selectedFile);
  }
}

}