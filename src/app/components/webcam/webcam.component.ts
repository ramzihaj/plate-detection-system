import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { io, Socket } from 'socket.io-client';

@Component({
  selector: 'app-webcam',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './webcam.component.html',
  styleUrls: ['./webcam.component.css']
})
export class WebcamComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('video', { static: false }) videoElementRef!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvas', { static: false }) canvasElementRef!: ElementRef<HTMLCanvasElement>;

  webcamActive = false;
  realtimeActive = false;
  showHistorical = false;
  videoElement: HTMLVideoElement | null = null;
  canvasElement: HTMLCanvasElement | null = null;
  stream: MediaStream | null = null;
  plateTextResults: any[] = [];
  realtimeImage: string | null = null;
  socket: Socket | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.socket = io('http://localhost:3000', { transports: ['websocket'] });
    this.socket.on('connect', () => {
      console.log('Connecté au serveur WebSocket');
    });
    this.socket.on('result', (data) => {
      if (data.error) {
        alert('Erreur : ' + data.error);
        return;
      }
      this.realtimeImage = `data:image/jpeg;base64,${data.annotated_frame}`;
      if (data.plates && data.plates.length > 0) {
        const newPlates = data.plates.filter((plate: any) => plate.text !== 'Aucune plaque détectée');
        this.plateTextResults = [...newPlates, ...this.plateTextResults];
      }
    });
    this.socket.on('error', (data) => {
      alert('Erreur : ' + data.message);
    });

    this.plateTextResults = [];
  }

  ngAfterViewInit() {
    this.videoElement = this.videoElementRef?.nativeElement || null;
    this.canvasElement = this.canvasElementRef?.nativeElement || null;
    console.log('ngAfterViewInit: videoElement exists:', !!this.videoElement, 'canvasElement exists:', !!this.canvasElement);
  }

  ngOnDestroy() {
    this.stopWebcam();
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  async startWebcam() {
    if (!this.videoElement || !this.canvasElement) {
      alert('Erreur : Les éléments vidéo ou canvas ne sont pas disponibles. Veuillez réessayer.');
      console.error('startWebcam: videoElement:', this.videoElement, 'canvasElement:', this.canvasElement);
      return;
    }

    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.videoElement.srcObject = this.stream;
      this.webcamActive = true;
      console.log('Webcam activée avec succès');
    } catch (err: any) {
      alert('Erreur lors de l\'accès à la webcam : ' + (err.message || 'Erreur inconnue'));
      console.error('Erreur dans startWebcam:', err);
    }
  }

  startRealtimeDetection() {
    if (!this.videoElement || !this.canvasElement) {
      alert('Erreur : Les éléments vidéo ou canvas ne sont pas disponibles. Veuillez réessayer.');
      console.error('startRealtimeDetection: videoElement:', this.videoElement, 'canvasElement:', this.canvasElement);
      return;
    }

    this.realtimeActive = true;
    const sendFrame = () => {
      if (!this.realtimeActive || !this.videoElement || !this.canvasElement) return;

      this.canvasElement.width = this.videoElement.videoWidth;
      this.canvasElement.height = this.videoElement.videoHeight;
      const context = this.canvasElement.getContext('2d')!;
      context.drawImage(this.videoElement, 0, 0);
      this.canvasElement.toBlob(
        (blob) => {
          if (blob) {
            blob.arrayBuffer().then((buffer) => {
              const binary = new Uint8Array(buffer);
              const base64 = btoa(binary.reduce((data, byte) => data + String.fromCharCode(byte), ''));
              if (this.socket) {
                this.socket.emit('frame', base64);
              }
            });
          }
        },
        'image/jpeg'
      );
      setTimeout(sendFrame, 200);
    };
    sendFrame();
  }

  stopRealtimeDetection() {
    this.realtimeActive = false;
    this.realtimeImage = null;
  }

  stopWebcam() {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
      this.webcamActive = false;
      this.realtimeActive = false;
      this.realtimeImage = null;
    }
  }

  loadHistoricalPlates() {
    this.http.get<{ plates: any[] }>('http://localhost:3000/api/plates').subscribe({
      next: (response) => {
        this.plateTextResults = response.plates.filter((plate) => plate.text !== 'Aucune plaque détectée');
        this.showHistorical = true;
        console.log('Historique des plaques chargé:', this.plateTextResults);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des plaques:', err);
        alert('Erreur lors du chargement de l\'historique : ' + err.message);
      }
    });
  }

  clearHistoricalPlates() {
    this.plateTextResults = [];
    this.showHistorical = false;
  }
}
