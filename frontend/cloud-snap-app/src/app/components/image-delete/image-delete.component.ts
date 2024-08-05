import { Component } from '@angular/core';
import { ApiService } from 'src/app/services/api.service';


@Component({
  selector: 'app-image-delete',
  templateUrl: './image-delete.component.html',
  styleUrls: ['./image-delete.component.scss']
})
export class ImageDeleteComponent {
  imageUrl: string = '';

  constructor(
    private apiService: ApiService
  ) { }
  
  deleteImage() {
    // Perform the deletion logic
  
    // Show alert
    console.log(this.imageUrl);

    this.apiService.deleteImage(this.imageUrl).subscribe(
      (response) => {
        // this.images = response.links;
        console.log(response);
        alert('Image deleted successfully!');
      },
      (error) => {
        console.log('API error:', error);
      }
    );
  }
}
