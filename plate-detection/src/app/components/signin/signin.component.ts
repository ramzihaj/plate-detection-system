import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router'; // Pour routerLink

@Component({
  selector: 'app-signin',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterModule], // Ajouter RouterModule pour routerLink
  templateUrl: './signin.component.html',
  styleUrls: ['./signin.component.css']
})
export class SigninComponent {
  signupData = { username: '', email: '', password: '' };
  errorMessage = '';

  constructor(private authService: AuthService, private router: Router) { }

  onSignup() {
    // Validation simple côté client
    if (!this.signupData.username || !this.signupData.email || !this.signupData.password) {
      this.errorMessage = 'Tous les champs sont requis.';
      return;
    }

    this.authService.signup(this.signupData).subscribe({
      next: () => {
        alert('Inscription réussie ! Veuillez vous connecter.');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.errorMessage = err.error.message || 'Erreur lors de l’inscription';
      }
    });
  }
}
