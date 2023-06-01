import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-tag-update',
  templateUrl: './tag-update.component.html',
  styleUrls: ['./tag-update.component.scss']
})
export class TagUpdateComponent {
  tags: string = '';
  jsonBefore: string = '';
  jsonAfter: string = '';

  constructor(
    private http: HttpClient,
    private apiService: ApiService
  ) { }

  updateTag(): void {
    this.apiService.updateTag(this.tags).subscribe(
      (response) => {
        this.jsonBefore = JSON.stringify(response.from[0], undefined, 4);
        this.jsonAfter = JSON.stringify(response.to[0], undefined, 4);
        console.log(this.jsonBefore);
        console.log(response.to[0]);
      },
      (error) => {
        console.log('API error:', error);
      }
    );
  }
}
