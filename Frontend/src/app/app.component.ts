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

    modelList = [];

    selectedModel = '';

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
    routeDistance: number;
    routeEnergyCost: number;

    // Estimation
    tripId: any;

    tripDistance: number;
    tripModelCost: number;
    tripModelAbsError: number;
    tripModelPercentageError: number;
    tripBaselineCost: number;
    tripBaselineAbsError: number;
    tripBaselinePercentageError: number;
    tripActualCost: number;

    estimationDirections: any;
    estimationSegments: any;

    hostUrl: string;

    // visual bools
    estimateShown = true;
    routeLoading = false;
    routeLoaded = false;
    tripLoaded = false;
    tripLoading = false;
    usingSegmentModel = true;

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

            this.printSegsDirection(res);
        });
    }

    getTrip() {
        const url = this.hostUrl + '/predict?trip=' + this.tripId;
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

                this.printSegsDirection(res);
            },
            error1 => {
                this.tripLoaded = false;
                this.tripLoading = false;
                console.log(error1.error);
            }
        );
    }

    private printSegsDirection(res: any) {
        const segmentKeys = res.features.map(seg => seg.properties.segmentkey);
        const segmentKeysString = segmentKeys.join(', ');
        console.log('Segmentkeys of trip:');
        console.log(segmentKeysString);
        const directions = res.features.map(seg => seg.properties.direction);
        const directionsString = directions.join(', ');
        console.log('Directions of trip:');
        console.log(directionsString);
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
                tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 18,
                    attribution: this.attribution
                })
            ],
            zoom: 13,
            center: this.aalLatLong
        };
        this.layers = [];
        this.getModels();
    }

    useSegmentModel(b: boolean) {
        console.log("TODO: Change geojson layers");
        this.usingSegmentModel = b;
    }
}
