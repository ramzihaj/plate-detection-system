import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { OwlOptions, CarouselModule } from 'ngx-owl-carousel-o';
import { CountUp } from 'countup.js';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, CarouselModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements AfterViewInit {
  customOptions: OwlOptions = {
    loop: true,
    mouseDrag: true,
    touchDrag: true,
    pullDrag: false,
    dots: true,
    navSpeed: 700,
    autoplay: true,
    autoplayTimeout: 5000,
    autoplayHoverPause: true,
    navText: ['<i class="bi bi-chevron-left"></i>', '<i class="bi bi-chevron-right"></i>'],
    responsive: {
      0: { items: 1 },
      600: { items: 1 },
      1000: { items: 1 }
    },
    nav: true
  };

  galleryOptions: OwlOptions = {
    loop: true,
    mouseDrag: true,
    touchDrag: true,
    pullDrag: false,
    dots: false,
    navSpeed: 700,
    autoplay: true,
    autoplayTimeout: 10000,
    autoplayHoverPause: true,
    rtl: true, // Right-to-left for gallery
    responsive: {
      0: { items: 2 },
      600: { items: 3 },
      1000: { items: 4 }
    },
    nav: false
  };

  slides = [
    { id: '1', image: 'assets/slide1.jpg', caption: 'Détection avancée des plaques tunisiennes avec YOLOv8' },
    { id: '2', image: 'assets/slide2.jpg', caption: 'Analyse en temps réel pour des résultats instantanés' },
    { id: '3', image: 'assets/slide3.jpg', caption: 'Upload facile pour images et vidéos' }
  ];

  detectionImages = [
    { id: '1', src: 'assets/detection1.jpg', alt: 'Détection de plaque 180 TN 3049' },
    { id: '2', src: 'assets/detection2.jpg', alt: 'Détection de plaque 144 TN 6669' },
    { id: '3', src: 'assets/detection3.jpg', alt: 'Détection en temps réel' },
    { id: '4', src: 'assets/detection4.jpg', alt: 'Détection en faible luminosité' },
    { id: '5', src: 'assets/detection5.jpg', alt: 'Détection multi-plaques' }
  ];

  ngAfterViewInit() {
    // Initialize CountUp animations
    const options = { duration: 2, separator: ',', decimalPlaces: 2 };
    new CountUp('successRate', 97.85, { ...options, suffix: '%' }).start();
    new CountUp('precision', 98, { ...options, suffix: '%' }).start();
    new CountUp('platesPerHour', 5000, { ...options }).start();
    new CountUp('processingSpeed', 50, { ...options, suffix: ' ms' }).start();
  }
}
