import { Component } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-image-upload',
  templateUrl: './image-upload.component.html',
  styleUrls: ['./image-upload.component.scss']
})
export class ImageUploadComponent {
  images: any[] = [];
  fileToUpload!: Blob;
  showAlert = false;

  constructor(
    private snackBar: MatSnackBar,
    private apiService: ApiService
  ) {}

  onFileSelected(event: any) {
    // console.log(event.target.files);
    this.fileToUpload = event.target.files[0];
  }

  uploadImage() {
    // Logic to upload the image
    const reader = new FileReader();
    reader.onload = () => {
      const imageData = reader.result as string;
      if (!imageData) {
        return;
      }

      const base64Data = imageData.substring(imageData.indexOf(',') + 1);
      const request = '{"image": "' + base64Data + '"}';
      this.apiService.getImagesByImage(request).subscribe(
        (response) => {
          this.images = response.links;
          console.log(response.links);
        },
        (error) => {
          console.log('API error:', error);
        }
      );
      
    };
    reader.readAsDataURL(this.fileToUpload);
    // Show alert after successful upload
    alert('Image uploaded successfully!')
  }
}
