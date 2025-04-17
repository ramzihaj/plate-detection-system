import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';

interface PlateDetectionData {
  filename: string;
  image: string;
  plates: string[];
  datetime?: string;
  plate_count?: number;
  error?: string;
}
@Component({
  selector: 'app-plate-detection',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './plate-detection.component.html',
  styleUrl: './plate-detection.component.css'
})

export class PlateDetectionComponent implements OnInit{
  detections: PlateDetectionData[] = [];
  ngOnInit(): void {
    const socket = new WebSocket('ws://localhost:8000/ws');

    socket.onmessage = (event) => {
      const data: PlateDetectionData = JSON.parse(event.data);

      if (!data.error) {
        data.datetime = new Date().toLocaleString();
        data.plate_count = data.plates.length;
      }

      this.detections.unshift(data); // newest first
    };
  }

}
