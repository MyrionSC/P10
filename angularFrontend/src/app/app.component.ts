/* tslint:disable:max-line-length */
import {Component, Inject, OnInit} from '@angular/core';
import {geoJSON, latLng, tileLayer} from 'leaflet';
import {HttpClient} from '@angular/common/http';
import {environment} from '../environments/environment';
import { DOCUMENT } from '@angular/platform-browser';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
    constructor(private http: HttpClient, @Inject(DOCUMENT) private document: any) {}

    options = {};
    layers = {};
    map: any;
    aalLatLong = latLng(57.046707, 9.935932);
    attribution = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors,' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>';
    origin: bigint;
    dest: bigint;
    routeJson: any;
    hostUrl: string;

    // visual bools
    routeLoading = false;
    routeLoaded = false;

    route() {
        const url = this.hostUrl + '/route?origin=' + this.origin + '&dest=' + this.dest;
        console.log('GET: ' + url);
        this.routeLoading = true;
        this.http.get(url).subscribe(res => {
            this.routeJson = res;
            this.layers[0] = geoJSON(this.routeJson);
            this.map.fitBounds(this.layers[0].getBounds());
            this.routeLoaded = true;
            this.routeLoading = false;
        });
    }

    mapReady(map) {
        this.map = map;
    }

    ngOnInit(): void {
        this.hostUrl = this.document.location.hostname === '172.25.11.191' ?
            this.hostUrl = 'http://172.25.11.191:5000' :
            this.hostUrl = 'http://localhost:5000';

        this.options = {
            layers: [
                tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18, attribution: this.attribution})
            ],
            zoom: 13,
            center: this.aalLatLong
        };
        this.layers = [];
    }
}
