import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContactService } from '../../services/contact.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  selectedFile: File | null = null;
  plateTextResults: any[] = [];

  constructor(private contactService: ContactService) {}

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
        if (response.plates && Array.isArray(response.plates)) {
          this.plateTextResults = [...response.plates.filter((plate: any) => plate.text !== 'Aucune plaque détectée'), ...this.plateTextResults];
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
        alert('Erreur lors de la détection du texte : ' + (err.message || 'Erreur inconnue'));
      },
      complete: () => {
        console.log('Requête /detect-plate-text terminée');
      }
    });
  }
}
