import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { io, Socket } from 'socket.io-client';

@Component({
  selector: 'app-webcam',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container py-5">
      <h1 class="fw-bold text-primary mb-4 text-center">Détection en Temps Réel</h1>

      <!-- Section Webcam -->
      <section class="mb-5">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="card shadow-sm p-4">
              <h3 class="text-center mb-4">Webcam</h3>
              <video #video autoplay playsinline class="w-100 mb-3"></video>
              <canvas #canvas style="display: none;"></canvas>
              <div class="text-center">
                <button
                  class="btn btn-primary me-2"
                  (click)="startWebcam()"
                  *ngIf="!webcamActive"
                >
                  Activer Webcam
                </button>
                <button
                  class="btn btn-primary me-2"
                  (click)="startRealtimeDetection()"
                  *ngIf="webcamActive && !realtimeActive"
                >
                  Détection en temps réel
                </button>
                <button
                  class="btn btn-danger"
                  (click)="stopRealtimeDetection()"
                  *ngIf="realtimeActive"
                >
                  Arrêter Détection
                </button>
                <button
                  class="btn btn-danger"
                  (click)="stopWebcam()"
                  *ngIf="webcamActive"
                >
                  Arrêter Webcam
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Résultats -->
      <section *ngIf="realtimeResults" class="mb-5">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="card shadow-sm p-4">
              <h3 class="text-center mb-4">Résultats</h3>
              <img
                [src]="realtimeImage"
                class="img-fluid mb-3"
                alt="Frame annotée"
              />
              <div *ngFor="let plate of realtimeResults.plates">
                <p><strong>Texte :</strong> {{ plate.text }}</p>
                <p><strong>Confiance :</strong> {{ plate.confidence | number:'1.2-2' }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .form-control:focus {
      border-color: #007bff;
      box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
    }
    video, img {
      max-width: 100%;
      height: auto;
    }
  `]
})
export class WebcamComponent implements OnInit, OnDestroy {
  @ViewChild('video') videoElementRef!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvas') canvasElementRef!: ElementRef<HTMLCanvasElement>;

  webcamActive = false;
  realtimeActive = false;
  videoElement!: HTMLVideoElement;
  canvasElement!: HTMLCanvasElement;
  stream: MediaStream | null = null;
  realtimeResults: any = null;
  realtimeImage: string | null = null;
  socket: Socket | null = null;

  ngOnInit() {
    this.socket = io('http://localhost:3000');
    this.socket.on('result', (data) => {
      if (data.error) {
        alert('Erreur : ' + data.error);
        return;
      }
      this.realtimeResults = data;
      this.realtimeImage = `data:image/jpeg;base64,${this.hexToBase64(data.annotated_frame)}`;
    });
    this.socket.on('error', (data) => {
      alert('Erreur : ' + data.message);
    });
  }

  ngOnDestroy() {
    this.stopWebcam();
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  async startWebcam() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.videoElement = this.videoElementRef.nativeElement;
      this.canvasElement = this.canvasElementRef.nativeElement;
      this.videoElement.srcObject = this.stream;
      this.webcamActive = true;
    } catch (err: any) { // Typage explicite de err comme any ou Error
      alert('Erreur lors de l\'accès à la webcam : ' + (err.message || 'Erreur inconnue'));
    }
  }

  startRealtimeDetection() {
    this.realtimeActive = true;
    const sendFrame = () => {
      if (!this.realtimeActive) return;
      this.canvasElement.width = this.videoElement.videoWidth;
      this.canvasElement.height = this.videoElement.videoHeight;
      const context = this.canvasElement.getContext('2d')!;
      context.drawImage(this.videoElement, 0, 0);
      this.canvasElement.toBlob((blob) => {
        if (blob) {
          blob.arrayBuffer().then((buffer) => {
            // Convertir ArrayBuffer en base64 sans Buffer
            const binary = new Uint8Array(buffer);
            const base64 = btoa(
              binary.reduce((data, byte) => data + String.fromCharCode(byte), '')
            );
            if (this.socket) {
              this.socket.emit('frame', base64);
            }
          });
        }
      }, 'image/jpeg');
      setTimeout(sendFrame, 100); // 10 FPS pour réduire la charge
    };
    sendFrame();
  }

  stopRealtimeDetection() {
    this.realtimeActive = false;
    this.realtimeResults = null;
    this.realtimeImage = null;
  }

  stopWebcam() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
      this.webcamActive = false;
      this.realtimeActive = false;
      this.realtimeResults = null;
      this.realtimeImage = null;
    }
  }

  private hexToBase64(hex: string): string {
    const bytes = new Uint8Array(hex.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16)));
    return btoa(String.fromCharCode(...bytes));
  }
}
