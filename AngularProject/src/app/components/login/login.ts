import { Component, ViewChild, ElementRef, OnInit, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../services/auth';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, RouterModule, CommonModule, MatIconModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login implements OnInit, OnDestroy {
  @ViewChild('video') videoElement!: ElementRef;
  @ViewChild('canvas') canvasElement!: ElementRef;

  loginData = {
    username: '',
    password: ''
  };

  stream: MediaStream | null = null;
  isCameraActive: boolean = false; // משתנה למעקב אחרי מצב המצלמה

  constructor(private auth: AuthService, private router: Router) { }

  ngOnInit() {
    // המצלמה לא נפתחת אוטומטית יותר כדי לא להבהיל
  }

  // פונקציה להפעלת המצלמה בלחיצת כפתור
  async startCamera() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 300, height: 300 }
      });
      if (this.videoElement) {
        this.videoElement.nativeElement.srcObject = this.stream;
        this.isCameraActive = true; // עדכון שהמצלמה פעילה
      }
    } catch (err) {
      console.error("שגיאה בגישה למצלמה:", err);
      Swal.fire({
        icon: 'error',
        title: 'גישה נדחתה',
        text: 'לא ניתן לגשת למצלמה. ודא שנתת הרשאה בדפדפן.',
        confirmButtonText: 'הבנתי'
      });
    }
  }

  takeSnapshot(): string {
    if (!this.isCameraActive) return ''; // הגנה למקרה שלא הופעלה מצלמה

    const video = this.videoElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL('image/png');
  }

  onLogin() {
    // 1. צילום התמונה (רק אם המצלמה הופעלה)
    if (this.isCameraActive) {
      const capturedImage = this.takeSnapshot();
      this.auth.setProfileImage(capturedImage);
    }

    // 2. שליחת נתוני התחברות
    this.auth.login(this.loginData).subscribe({
      next: (response) => {
        Swal.fire({
          icon: 'success',
          title: `שלום ${this.auth.currentUser?.username}!`,
          text: 'התחברת בהצלחה למערכת',
          timer: 3000, // נסגר אוטומטית אחרי 3 שניות
          showConfirmButton: false
        });
        this.stopCamera();
        this.router.navigate(['/home']);
      },
      error: (err) => {
        Swal.fire({
          icon: 'warning',
          title: 'אופס...',
          text: 'שגיאה בהתחברות: בדוק את שם המשתמש והסיסמה',
          confirmButtonColor: '#d33'
        });
      }
    });
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      if (this.videoElement && this.videoElement.nativeElement) {
        this.videoElement.nativeElement.srcObject = null;
      }
      this.stream = null;
      this.isCameraActive = false;
    }
  }

  ngOnDestroy() {
    this.stopCamera();
  }
}