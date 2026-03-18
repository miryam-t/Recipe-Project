import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http'
import { authInterceptor } from './core/interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // provideHttpClient(withInterceptors([authInterceptor])),
    // הוספת withInterceptors עם האינטרספטור שלך היא קריטית!
   provideHttpClient(
      withInterceptors([authInterceptor]) // וודאי שהשם כאן תואם לייצוא מהקובץ
    ),
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    // provideHttpClient()

  ]
};
