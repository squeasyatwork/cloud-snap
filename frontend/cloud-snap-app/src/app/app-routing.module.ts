import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { TagUpdateComponent } from './components/tag-update/tag-update.component';
import { ImageDeleteComponent } from './components/image-delete/image-delete.component';
import { LoginComponent } from './components/login/login.component';
import { ImageUploadComponent } from './components/image-upload/image-upload.component';
import { ImageSearchComponent } from './components/image-search/image-search.component';
import { HomeComponent } from './components/home/home.component';
import { AuthGuard } from './guards/auth.guard';

const routes: Routes = [
  { path: 'login', component: LoginComponent},
  { path: 'home', component: HomeComponent, canActivate: [AuthGuard]},
  { path: 'upload', component: ImageUploadComponent, canActivate: [AuthGuard] },
  { path: 'search', component: ImageSearchComponent, canActivate: [AuthGuard] },
  { path: 'update-tag', component: TagUpdateComponent, canActivate: [AuthGuard] },
  { path: 'delete', component: ImageDeleteComponent, canActivate: [AuthGuard] },
  { path: '', redirectTo: '/home', pathMatch: 'full' },
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes)
  ],
  exports: [RouterModule],
})
export class AppRoutingModule {}
