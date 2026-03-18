import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth';
import { RouterModule } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-admin-panel',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './admin-panel.html',
  styleUrl: './admin-panel.css'
})
export class AdminPanel implements OnInit {
  pendingUsers: any[] = [];
  message: string = '';

  constructor(private auth: AuthService) { }

  ngOnInit(): void {
    this.loadPendingUsers();
  }

  loadPendingUsers() {
    this.auth.getPendingUsers().subscribe({
      next: (users) => this.pendingUsers = users,
      error: (err) => this.message = 'שגיאה בטעינת משתמשים'
    });
  }

  approve(userId: number) {
    this.auth.approveUser(userId).subscribe({
      next: (res) => {
        Swal.fire({
          icon: 'success',
          title: 'בוצע!',
          text: 'המשתמש אושר בהצלחה!',
          timer: 2500, // החלון ייסגר לבד אחרי 2.5 שניות
          showConfirmButton: false // מעלים את הכפתור כי יש טיימר
        });
        this.loadPendingUsers(); // רענון הרשימה
      },
      error: (err) => Swal.fire({
        icon: 'error',
        title: 'אישור נכשל',
        text: 'שגיאה באישור המשתמש',
        confirmButtonText: 'סגור',
        confirmButtonColor: '#d33' // צבע אדום לשגיאה
      })
    });
  }
}