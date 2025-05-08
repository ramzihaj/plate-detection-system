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
            <div class="card shadow-sm p-4">
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
                  <button type="submit" class="btn btn-primary">Envoyer</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>

      <!-- Informations de Contact -->
      <section class="text-center">
        <h3 class="fw-bold text-primary mb-4">Nos Coordonnées</h3>
        <p class="text-muted">
          Email:
          <a href="mailto:ramzi2020haj@gmail.com" class="text-primary"
            >ramzi2020haj&#64;gmail.com</a
          ><br />
          Téléphone: +216 22 528 882
        </p>
        <div class="social-icons mt-3">
          <a href="#" class="text-primary me-3"
            ><i class="bi bi-facebook fs-4"></i
          ></a>
          <a href="#" class="text-primary me-3"
            ><i class="bi bi-twitter fs-4"></i
          ></a>
          <a href="#" class="text-primary"><i class="bi bi-linkedin fs-4"></i></a>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .form-control:focus {
      border-color: #007bff;
      box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
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
