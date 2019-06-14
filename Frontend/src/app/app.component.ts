/* tslint:disable:max-line-length */
import {Component, Inject, OnInit} from '@angular/core';
import {geoJSON, latLng, tileLayer} from 'leaflet';
import {HttpClient} from '@angular/common/http';
import {DOCUMENT} from '@angular/platform-browser';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
    constructor(private http: HttpClient, @Inject(DOCUMENT) private document: any) {
    }

    // available routes
    availableTrips = [
        '202094',
        '1234',
        '5678'
    ];
    selectedTrip = "202094";

    // leaflet stuff
    options = {};
    layers = {};
    map: any;
    aalLatLong = latLng(57.046707, 9.935932);
    attribution = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors,' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>';

    // Estimation
    routeJson: any;
    tripDistance: number;
    tripModelCost: number;
    tripModelAbsError: number;
    tripModelPercentageError: number;
    tripBaselineCost: number;
    tripBaselineAbsError: number;
    tripBaselinePercentageError: number;
    tripActualCost: number;

    // visual bools
    estimateShown = true;
    tripLoaded = false;
    tripLoading = false;
    usingSegmentModel = true;

    showTrip() {
        const model = this.usingSegmentModel ? 'segment' : 'supersegment';
        const url = './assets/trip' + this.selectedTrip + '-' + model + '.json';
        console.log('GET: ' + url);

        this.tripLoading = true;
        this.http.get(url).subscribe(
            (res: any) => {
                this.routeJson = res;
                console.log(res);

                this.tripDistance = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_length / 1000;
                this.tripActualCost = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_actual;
                this.tripModelCost = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_cost;
                this.tripBaselineCost = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_baseline;

                this.tripBaselineAbsError = Math.abs(this.tripActualCost - this.tripBaselineCost);
                this.tripBaselinePercentageError = (this.tripBaselineAbsError / this.tripActualCost) * 100;
                this.tripModelAbsError = Math.abs(this.tripActualCost - this.tripModelCost);
                this.tripModelPercentageError = (this.tripModelAbsError / this.tripActualCost) * 100;

                this.layers[0] = geoJSON(this.routeJson);
                this.map.fitBounds(this.layers[0].getBounds());
                this.tripLoaded = true;
                this.tripLoading = false;
            },
            error1 => {
                this.tripLoaded = false;
                this.tripLoading = false;
                console.log(error1.error);
            }
        );
    }

    mapReady(mp) {
        this.map = mp;
        this.showTrip();
    }

    ngOnInit(): void {
        this.options = {
            layers: [
                tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 18,
                    attribution: this.attribution
                })
            ],
            zoom: 13,
            center: this.aalLatLong
        };
        this.layers = [];
    }

    useSegmentModel(b: boolean) {
        this.usingSegmentModel = b;
        this.showTrip();
    }
}
