import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-image-search',
  templateUrl: './image-search.component.html',
  styleUrls: ['./image-search.component.scss']
})
export class ImageSearchComponent {
  tags: string = '';
  imageTags: string = '';
  imagesFromTags: any[] | undefined;
  imagesFromImageTags: any[] | undefined;

  constructor(
    private http: HttpClient,
    private apiService: ApiService
  ) { }

  searchImageByTag(): void {
    this.apiService.getImagesByTags(this.tags).subscribe(
      (response) => {
        this.imagesFromTags = response.links;
        console.log(response.links);
      },
      (error) => {
        console.log('API error:', error);
      }
    );
  }
}
