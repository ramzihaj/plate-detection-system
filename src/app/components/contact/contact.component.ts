import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ContactService } from '../../services/contact.service';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent {
  name: string = '';
  email: string = '';
  message: string = '';

  constructor(private contactService: ContactService) {}

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
        alert('Erreur lors de l\'envoi du message : ' + (err.message || 'Erreur inconnue'));
      }
    });
  }
}
