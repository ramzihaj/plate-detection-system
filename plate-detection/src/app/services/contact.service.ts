import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ContactService {
  private apiUrl = 'http://localhost:3000/api';

  constructor(private http: HttpClient) { }

  sendContactMessage(data: { name: string; email: string; message: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/contact`, data).pipe(
      catchError((err) => {
        throw new Error(err.error.message || 'Erreur lors de l\'envoi du message');
      })
    );
  }

  detectPlate(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    console.log('Envoi de la requête POST à:', `${this.apiUrl}/detect`, 'avec fichier:', file.name);
    return this.http.post(`${this.apiUrl}/detect`, formData).pipe(
      catchError((err) => {
        throw new Error(err.error.message || 'Erreur lors de la détection');
      })
    );
  }
}
