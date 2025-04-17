import { CommonModule } from '@angular/common';
import { Component, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterOutlet } from '@angular/router';
import { PlateDetectionComponent } from './plate-detection/plate-detection.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule,PlateDetectionComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'plate-detector';
}
