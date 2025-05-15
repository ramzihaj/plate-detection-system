import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContactService } from '../../services/contact.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container py-5">
      <h1 class="fw-bold text-primary mb-4 text-center">Uploader une Image ou Vidéo</h1>

      <!-- Section Upload -->
      <section class="mb-5">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="card shadow-sm p-4">
              <h3 class="text-center mb-4">Sélectionner un fichier</h3>
              <input
                type="file"
                class="form-control mb-3"
                accept="image/*,video/*"
                (change)="onFileSelected($event)"
              />
              <button
                class="btn btn-success w-100"
                [disabled]="!selectedFile"
                (click)="detectPlateText()"
              >
                Détecter Texte Matricule
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Résultats Texte Matricule -->
      <section *ngIf="plateTextResults && plateTextResults.length > 0" class="mb-5">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="card shadow-sm p-4">
              <h3 class="text-center mb-4">Résultats Texte Matricule</h3>
              <div class="table-responsive">
                <table class="table table-striped table-bordered table-hover">
                  <thead class="table-dark">
                    <tr>
                      <th scope="col">Matricule</th>
                      <th scope="col">Date de Détection</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr *ngFor="let result of plateTextResults">
                      <td>{{ result.text }}</td>
                      <td>{{ result.detectionDate | date:'medium' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Message si aucun résultat -->
      <section *ngIf="plateTextResults && plateTextResults.length === 0" class="mb-5">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="card shadow-sm p-4 text-center">
              <p class="text-danger">Aucune plaque détectée.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .container {
      background: url('/assets/background.jpg') no-repeat center center fixed;
      background-size: cover;
      min-height: 100vh;
      padding: 20px;
      position: relative;
    }

    .container::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(255, 255, 255, 0.7);
      z-index: 1;
    }

    .container > * {
      position: relative;
      z-index: 2;
    }

    .form-control:focus {
      border-color: #007bff;
      box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
    }

    .table {
      border-collapse: separate;
      border-spacing: 0;
      border-radius: 8px;
      overflow: hidden;
    }

    .table th, .table td {
      padding: 12px 15px;
      text-align: center;
      vertical-align: middle;
    }

    .table thead th {
      background-color: #343a40;
      color: white;
      font-weight: 600;
      border: none;
    }

    .table tbody tr {
      transition: background-color 0.2s ease-in-out;
    }

    .table tbody tr:hover {
      background-color: #f1f3f5;
    }

    .table-bordered {
      border: 1px solid #dee2e6;
    }

    .table-bordered th, .table-bordered td {
      border: 1px solid #dee2e6;
    }

    .card {
      border-radius: 10px;
      border: none;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      background: rgba(255, 255, 255, 0.9);
    }
  `]
})
export class UploadComponent {
  selectedFile: File | null = null;
  plateTextResults: any[] = [];

  constructor(private contactService: ContactService) { }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
      console.log('Fichier sélectionné:', this.selectedFile.name);
    }
  }

  detectPlateText() {
    if (!this.selectedFile) {
      alert('Veuillez sélectionner un fichier');
      return;
    }
    console.log('Envoi du fichier pour détection de texte:', this.selectedFile.name);
    this.contactService.detectPlateText(this.selectedFile).subscribe({
      next: (response) => {
        console.log('Réponse reçue pour /detect-plate-text:', response);
        // Ajouter tous les plates à la liste des résultats
        if (response.plates && Array.isArray(response.plates)) {
          this.plateTextResults = [...this.plateTextResults, ...response.plates];
        } else {
          console.warn('Réponse inattendue, aucun tableau de plaques trouvé:', response);
          this.plateTextResults.push({
            text: 'Aucune plaque détectée',
            detectionDate: new Date().toISOString()
          });
        }
      },
      error: (err) => {
        console.error('Erreur lors de /detect-plate-text:', err);
        alert('Erreur lors de la détection du texte : ' + err.message);
      },
      complete: () => {
        console.log('Requête /detect-plate-text terminée');
      }
    });
  }
}
