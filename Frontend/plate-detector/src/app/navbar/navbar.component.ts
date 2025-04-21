import { CommonModule, NgFor, NgIf } from '@angular/common';
import { Component } from '@angular/core';


@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule,NgIf],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent {

  showDashboardMenu = true;

}
