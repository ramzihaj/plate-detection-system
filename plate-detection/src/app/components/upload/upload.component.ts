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
                class="btn btn-primary w-100"
                [disabled]="!selectedFile"
                (click)="detectPlate()"
              >
                Détecter
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Résultats -->
      <section *ngIf="results" class="mb-5">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="card shadow-sm p-4">
              <h3 class="text-center mb-4">Résultats</h3>
              <p>Résultats bruts: {{ results | json }}</p>
              <img
                *ngIf="!isVideo"
                [src]="results.annotated_file"
                class="img-fluid mb-3"
                alt="Image annotée"
                (error)="onImageError($event)"
              />
              <video
                *ngIf="isVideo"
                [src]="results.annotated_file"
                controls
                class="img-fluid mb-3"
              ></video>
              <div *ngFor="let plate of results.plates">
                <p><strong>Texte :</strong> {{ plate.text }}</p>
                <p><strong>Confiance :</strong> {{ plate.confidence | number:'1.2-2' }}</p>
              </div>
              <p *ngIf="!results.plates || results.plates.length === 0" class="text-danger">
                Aucune plaque détectée
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .form-control:focus {
      border-color: #007bff;
      box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
    }
    video, img {
      max-width: 100%;
      height: auto;
    }
  `]
})
export class UploadComponent {
  selectedFile: File | null = null;
  results: any = null;
  isVideo = false;

  constructor(private contactService: ContactService) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
      this.isVideo = ['video/mp4', 'video/avi', 'video/mov'].includes(this.selectedFile.type);
      console.log('Fichier sélectionné:', this.selectedFile.name);
    }
  }

  detectPlate() {
    if (!this.selectedFile) {
      alert('Veuillez sélectionner un fichier');
      return;
    }
    console.log('Envoi du fichier:', this.selectedFile.name);
    this.contactService.detectPlate(this.selectedFile).subscribe({
      next: (response) => {
        console.log('Réponse du backend:', response);
        this.results = response;
        this.results.annotated_file = `http://localhost:3000/${response.annotated_file}`;
      },
      error: (err) => {
        console.error('Erreur HTTP:', err);
        alert('Erreur lors de la détection : ' + err.message);
      }
    });
  }

  onImageError(event: Event) {
    console.error('Erreur de chargement de l\'image annotée:', event);
  }
}
