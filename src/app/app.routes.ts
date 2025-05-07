import { NgModule } from '@angular/core';
import { PreloadAllModules, RouterModule, Routes } from '@angular/router';

export const routes: Routes = [
  { path: 'home', loadChildren: () => import('./home/home.module').then(m => m.HomeModule) },
  { path: 'contact', loadChildren: () => import('./contact/contact.module').then(m => m.ContactModule) },
  { path: 'aboutus', loadChildren: () => import('./aboutus/aboutus.module').then(m => m.AboutusModule) }
];
@NgModule({
  imports: [RouterModule.forRoot(routes,
    {preloadingStrategy: PreloadAllModules}
  )],
  exports: [RouterModule]
})
export class AppRoutingModule {}
