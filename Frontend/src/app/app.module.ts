import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {HttpClientModule} from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {LeafletModule} from '@asymmetrik/angular2-leaflet';
import {AppComponent} from './app.component';

import { registerLocaleData } from '@angular/common';
import localeDK from '@angular/common/locales/en-DK';

// the second parameter 'fr' is optional
registerLocaleData(localeDK, 'en-DK');

@NgModule({
    declarations: [
        AppComponent
    ],
    imports: [
        BrowserModule,
        FormsModule,
        HttpClientModule,
        LeafletModule.forRoot()
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule {
}
