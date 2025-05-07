import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-about-us',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
       <div class="container py-5">
         <!-- Header -->
         <h1 class="fw-bold text-primary mb-4 text-center">À Propos de Nous</h1>

         <!-- À Propos du Projet -->
         <section class="mb-5">
           <div class="row justify-content-center">
             <div class="col-lg-10">
               <h3 class="text-center mb-4">Notre Mission</h3>
               <p class="lead text-muted text-center">
                 Plate Detection est une application innovante conçue pour détecter et lire les plaques d’immatriculation tunisiennes grâce à l’intelligence artificielle. Nous utilisons YOLOv8 pour offrir une solution rapide et précise, que ce soit via des uploads d’images/vidéos ou en temps réel avec une webcam.
               </p>
               <p class="text-muted text-center">
                 Notre objectif est de fournir une technologie accessible et efficace pour des applications dans la sécurité, la gestion de parkings, et bien plus encore.
               </p>
             </div>
           </div>
         </section>

         <!-- Équipe -->
         <section class="text-center">
           <h3 class="fw-bold text-primary mb-4">Notre Équipe</h3>
           <div class="row">
             <div class="col-md-4 mb-4">
               <div class="card shadow-sm p-4">
                 <i class="bi bi-person-circle fs-1 text-primary mb-3"></i>
                 <h5>Ramzi Haj Massoud</h5>
                 <p class="text-muted">Fondateur & Développeur Principal</p>
               </div>
             </div>
             <div class="col-md-4 mb-4">
               <div class="card shadow-sm p-4">
                 <i class="bi bi-person-circle fs-1 text-primary mb-3"></i>
                 <h5>Équipe AI</h5>
                 <p class="text-muted">Spécialistes en Intelligence Artificielle</p>
               </div>
             </div>
             <div class="col-md-4 mb-4">
               <div class="card shadow-sm p-4">
                 <i class="bi bi-person-circle fs-1 text-primary mb-3"></i>
                 <h5>Équipe Support</h5>
                 <p class="text-muted">Support Technique & Utilisateur</p>
               </div>
             </div>
           </div>
         </section>

         <!-- Call to Action -->
         <div class="text-center mt-5">
           <a routerLink="/" class="btn btn-primary">Retour à l'Accueil</a>
         </div>
       </div>
     `,
  styles: []
})
export class AboutUsComponent { }
