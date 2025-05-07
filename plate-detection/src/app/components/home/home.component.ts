import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { OwlOptions, CarouselModule } from 'ngx-owl-carousel-o';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, CarouselModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  customOptions: OwlOptions = {
    loop: true,
    mouseDrag: true,
    touchDrag: true,
    pullDrag: false,
    dots: true,
    navSpeed: 700,
    navText: ['<i class="bi bi-chevron-left"></i>', '<i class="bi bi-chevron-right"></i>'],
    responsive: {
      0: { items: 1 },
      600: { items: 1 },
      1000: { items: 1 }
    },
    nav: true
  };

  slides = [
    { id: '1', image: 'assets/slide1.jpg', caption: 'Détection précise des plaques tunisiennes avec YOLOv8' },
    { id: '2', image: 'assets/slide2.jpg', caption: 'Analyse en temps réel via webcam' },
    { id: '3', image: 'assets/slide3.jpg', caption: 'Upload d’images et vidéos pour une détection rapide' }
  ];
}
