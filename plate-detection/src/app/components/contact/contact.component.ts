import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ContactService } from '../../services/contact.service';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="container py-5">
      <!-- Header -->
      <h1 class="fw-bold text-primary mb-4 text-center">Nous Contacter</h1>

      <!-- Formulaire de Contact -->
      <section class="mb-5">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="card shadow-lg p-4 bg-light">
              <h3 class="text-center mb-4">Envoyez-nous un message</h3>
              <form (ngSubmit)="onSubmit()">
                <div class="mb-3">
                  <label for="name" class="form-label">Nom</label>
                  <input
                    type="text"
                    class="form-control"
                    id="name"
                    [(ngModel)]="name"
                    name="name"
                    required
                  />
                </div>
                <div class="mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    [(ngModel)]="email"
                    name="email"
                    required
                  />
                </div>
                <div class="mb-3">
                  <label for="message" class="form-label">Message</label>
                  <textarea
                    class="form-control"
                    id="message"
                    [(ngModel)]="message"
                    name="message"
                    rows="5"
                    required
                  ></textarea>
                </div>
                <div class="text-center">
                  <button type="submit" class="btn btn-primary btn-lg">Envoyer</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>

      <!-- Informations de Contact -->
      <section class="text-center">
        <h3 class="fw-bold text-primary mb-4">Nos Coordonnées</h3>
        <p class="text-muted lead">
          Email:
          <a href="mailto:ramzi2020haj@gmail.com" class="text-primary text-decoration-none"
            >ramzi2020haj&#64;gmail.com</a
          ><br />
          Téléphone: <span class="text-primary">+216 22 528 882</span>
        </p>
        <div class="social-icons mt-4">
          <a href="#" class="text-primary me-3" target="_blank"
            ><i class="bi bi-facebook fs-3"></i
          ></a>
          <a href="#" class="text-primary me-3" target="_blank"
            ><i class="bi bi-twitter fs-3"></i
          ></a>
          <a href="#" class="text-primary" target="_blank"
            ><i class="bi bi-linkedin fs-3"></i></a>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .container {
      /* Ajout d'une image de fond */
      background: url('/assets/contact-background.jpg') no-repeat center center fixed;
      background-size: cover;
      min-height: 100vh;
      padding: 30px 15px;
      position: relative;
    }

    /* Couche semi-transparente pour la lisibilité */
    .container::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(255, 255, 255, 0.85); /* Ajuster l'opacité si nécessaire */
      z-index: 1;
    }

    /* Contenu au-dessus de l'overlay */
    .container > * {
      position: relative;
      z-index: 2;
    }

    .card {
      border-radius: 12px;
      border: none;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
      background: rgba(255, 255, 255, 0.95);
      transition: transform 0.2s ease-in-out;
    }

    .card:hover {
      transform: translateY(-5px);
    }

    .form-control:focus {
      border-color: #007bff;
      box-shadow: 0 0 8px rgba(0, 123, 255, 0.6);
    }

    .btn-primary {
      background-color: #007bff;
      border: none;
      padding: 10px 30px;
      transition: background-color 0.3s ease;
    }

    .btn-primary:hover {
      background-color: #0056b3;
    }

    .btn-lg {
      font-size: 1.1rem;
      font-weight: 500;
    }

    .lead {
      font-size: 1.15rem;
      line-height: 1.6;
    }

    .social-icons a {
      text-decoration: none;
      transition: color 0.3s ease;
    }

    .social-icons a:hover {
      color: #0056b3 !important;
    }

    h1, h3 {
      text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
    }
  `]
})
export class ContactComponent {
  name: string = '';
  email: string = '';
  message: string = '';

  constructor(private contactService: ContactService) { }

  onSubmit() {
    const contactData = {
      name: this.name,
      email: this.email,
      message: this.message
    };

    this.contactService.sendContactMessage(contactData).subscribe({
      next: (response) => {
        alert('Message envoyé avec succès ! Merci de nous avoir contactés.');
        this.name = '';
        this.email = '';
        this.message = '';
      },
      error: (err) => {
        alert('Erreur lors de l\'envoi du message : ' + err.message);
      }
    });
  }
}
