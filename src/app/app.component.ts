import { Component } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule,RouterOutlet,CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'plate-detector';
  showDashboardMenu = true;
  showUserMenu: boolean | undefined;
  toggleMenu() {
    this.showUserMenu = !this.showUserMenu;
  }
}
