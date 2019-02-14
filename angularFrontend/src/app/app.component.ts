/* tslint:disable:max-line-length */
import {Component, OnInit} from '@angular/core';
import {geoJSON, latLng, tileLayer} from 'leaflet';
import {HttpClient} from '@angular/common/http';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
    constructor(private http: HttpClient) { }

    options = {};
    layers = {};
    panOptions = {};
    map: any;
    aalLatLong = latLng(57.046707, 9.935932);
    attribution = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors,' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>';
    origin: bigint;
    dest: bigint;
    routeJson: any;
    routeUrl = 'http://localhost:5000/route';

    route() {
        let url = this.routeUrl + '?origin=' + this.origin + '&dest=' + this.dest;
        this.http.get(url).subscribe(res => {
            this.routeJson = res;
            this.layers[0] = geoJSON(this.routeJson);
            this.map.fitBounds(this.layers[0].getBounds());
        });
    }

    mapReady(map) {
        this.map = map;
        console.log('map is ready');
        console.log(map);
    }

    ngOnInit(): void {
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
