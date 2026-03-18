import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Register } from './components/register/register';
import { RecipeList } from './components/recipe-list/recipe-list';
import { Login } from './components/login/login';
import { Profile } from './components/profile/profile';
import { RecipeDetail } from './components/recipe-detail/recipe-detail';
import { AdminPanel } from './components/admin-panel/admin-panel';
import { AddRecipe } from './components/add-recipe/add-recipe';
import { AdminDashboard } from './components/admin-dashboard/admin-dashboard';

export const routes: Routes = [
  { path: 'home', component: Home },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'recipes', component: RecipeList },
  { path: 'recipes/:id', component: RecipeDetail },
  { path: 'profile', component: Profile },
  { path: 'add-recipe', component: AddRecipe },
  
  // נתיבים למנהל - שימי לב לשמות כאן
  { path: 'admin-panel', component: AdminPanel }, // פאנל כללי אם יש לך
  { path: 'admin-dashboard', component: AdminDashboard }, // הדף שבו מאשרים משתמשים
  
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: '**', redirectTo: '/home' } // הגנה מפני נתיבים לא קיימים // שינוי דף ברירת המחדל לבית]
];