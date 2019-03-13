/* tslint:disable:max-line-length */
import {Component, Inject, OnInit} from '@angular/core';
import {geoJSON, latLng, tileLayer} from 'leaflet';
import {HttpClient} from '@angular/common/http';
import {environment} from '../environments/environment';
import { DOCUMENT } from '@angular/platform-browser';
import { map } from "rxjs/operators";

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
    constructor(private http: HttpClient, @Inject(DOCUMENT) private document: any) {}

    modelList = [];

    selectedModel = "";

    options = {};
    layers = {};
    map: any;
    aalLatLong = latLng(57.046707, 9.935932);
    attribution = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors,' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>';

    // Routing
    origin: bigint;
    dest: bigint;
    routeJson: any;
    routeEnergyCost: number;
    routeDistance: number;

    // Estimation
    tripId: any;
    estimationDirections: any;
    estimationSegments: any;

    hostUrl: string;

    // visual bools
    routeLoading = false;
    routeLoaded = false;

    getRoute(endpoint: string) {
        const url = this.hostUrl + '/' + endpoint + '?origin=' + this.origin + '&dest=' + this.dest;
        console.log('GET: ' + url);
        this.routeLoading = true;
        this.http.get(url).subscribe((res: any) => {
            this.routeJson = res;
            this.routeEnergyCost = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_cost - this.routeJson.features.length;
            this.routeDistance = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_length / 1000;
            this.layers[0] = geoJSON(this.routeJson);
            this.map.fitBounds(this.layers[0].getBounds());
            this.routeLoaded = true;
            this.routeLoading = false;

            const segmentKeys = res.features.map(seg => seg.properties.segmentkey );
            const segmentKeysString = segmentKeys.join(", ");
            console.log("Segmentkeys of trip:");
            console.log(segmentKeysString);
        });
    }

    getModels(): any {
        const url = this.hostUrl + '/current_models';
        this.http.get(url).subscribe((res: any) => {
           this.modelList = res;
           this.selectedModel = res[0];
        });
    }

    loadModel() {
        const strs = this.selectedModel.split("/");
        const url = this.hostUrl + '/load_model?batch=' + strs[0] + '&model_name=' + strs[1];
        this.http.get<any>(url).subscribe((res: any) => {
            console.log(res);
        });
    }

    mapReady(mp) {
        this.map = mp;
    }

    ngOnInit(): void {
        this.hostUrl = 'http://172.25.11.191:5000';
        // this.hostUrl = this.document.location.hostname === '172.25.11.191' ?
        //     this.hostUrl = 'http://172.25.11.191:5000' :
        //     this.hostUrl = 'http://localhost:5000';

        this.options = {
            layers: [
                tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18, attribution: this.attribution})
            ],
            zoom: 13,
            center: this.aalLatLong
        };
        this.layers = [];
        this.getModels();
    }

}
