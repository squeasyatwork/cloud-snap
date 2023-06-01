import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'https://x73gr910pb.execute-api.us-east-1.amazonaws.com/production/api';
  constructor(private http: HttpClient) { }

  deleteImage(param: any):Observable<any> {
    const url = `${this.baseUrl}/images?image_url=` + param;
    return this.http.delete<any>(url);
  }

  getImagesByImage(request: any): Observable<any> {
    const url = `${this.baseUrl}/images/search/image`;
    return this.http.post<any>(url, request);
  }

  getImagesByTags(request: any): Observable<any> {
    const url = `${this.baseUrl}/images/search/tags`;
    return this.http.post<any>(url, request);
  }

  updateTag(request: any): Observable<any> {
    const url = `${this.baseUrl}/images/change/tags`;
    return this.http.post<any>(url, request);
  }
}
