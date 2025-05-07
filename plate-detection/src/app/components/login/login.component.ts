import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../auth.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router'; // Pour routerLink

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterModule], // Ajouter RouterModule
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginData = { email: '', password: '' };
  errorMessage = '';

  constructor(private authService: AuthService, private router: Router) {}

  onLogin() {
    // Validation simple côté client
    if (!this.loginData.email || !this.loginData.password) {
      this.errorMessage = 'Tous les champs sont requis.';
      return;
    }

    this.authService.login(this.loginData).subscribe({
      next: () => {
        alert('Connexion réussie !');
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.errorMessage = err.error.message || 'Erreur lors de la connexion';
      }
    });
  }
}
