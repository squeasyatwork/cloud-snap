import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'cloud-snap-app';
  isLoggedIn = false;
  
  constructor(private router: Router) {}

  ngOnInit(): void {

  }


  login() {
  }

  logout() {
    // Perform logout logic here (e.g., clearing session, removing tokens, etc.)
    // Redirect to the sign-in page

    this.router.navigate(['/home']);
  }  
}
