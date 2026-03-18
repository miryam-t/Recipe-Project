import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { RouterModule } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    RouterModule,
    MatButtonModule,
    MatTableModule, // <--- זה חשוב, אבל זה לא מספיק
    MatIconModule
    // אם את משתמשת בגרסה חדשה של Angular Material, לעיתים צריך לייבא את MatTableModule המלא
  ],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.css'
})
export class AdminDashboard implements OnInit {
  pendingUsers: any[] = [];
  // אלו העמודות שיוצגו בטבלה
  displayedColumns: string[] = ['username', 'email', 'actions'];

  constructor(private auth: AuthService) { }

  ngOnInit() {

    this.loadUsers();
  }

  loadUsers() {
    // פנייה לפונקציה getPendingUsers שב-Service שלך
    this.auth.getPendingUsers().subscribe({
      next: (users) => {
        this.pendingUsers = users;
      },
      error: (err) => console.error('שגיאה בטעינת משתמשים', err)
    });
  }
  approve(userId: number) {
    Swal.fire({
      title: 'האם את בטוחה?',
      text: "המשתמש יקבל הרשאת העלאת מתכונים",
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'כן, אשר שדרוג!',
      cancelButtonText: 'ביטול'
    }).then((result) => {
      if (result.isConfirmed) {
        this.auth.approveUser(userId).subscribe({
          next: (res) => {
            Swal.fire('אושר!', 'המשתמש שודרג בהצלחה.', 'success');
            this.loadUsers(); // רענון הרשימה
          },
          error: (err) => Swal.fire('שגיאה', 'לא ניתן היה לאשר את המשתמש', 'error')
        });
      }
    });
  }

}