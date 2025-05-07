import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:3000/api'; // Remplacez par l'URL de votre backend
  private tokenKey = 'auth_token';

  constructor(private http: HttpClient) {}

  // Action de connexion
  login(data: { email: string; password: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, data).pipe(
      tap((response: any) => {
        if (response.token) {
          this.setToken(response.token); // Stocke le token
        }
      })
    );
  }

  // Action d'inscription
  signup(data: { username: string; email: string; password: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/signup`, data);
  }

  // Stocke le token dans localStorage
  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  // Récupère le token
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  // Vérifie si l'utilisateur est connecté
  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  // Déconnexion
  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }
}
