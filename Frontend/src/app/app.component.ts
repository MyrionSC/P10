/* tslint:disable:max-line-length */
import {Component, Inject, OnInit} from '@angular/core';
import {geoJSON, latLng, tileLayer} from 'leaflet';
import {HttpClient} from '@angular/common/http';
import {DOCUMENT} from '@angular/platform-browser';
import {FeatureCollection, GeoJsonObject} from 'geojson';

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
    leafOptions = {};
    leafLayers = [];
    leafMap: any;
    aalLatLong = latLng(57.046707, 9.935932);
    attribution = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors,' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>';

    // Estimation
    routeJson: FeatureCollection;
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
            (res: FeatureCollection) => {
                this.routeJson = res;
                console.log(res);

                // this.tripDistance = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_length / 1000;
                // this.tripActualCost = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_actual;
                // this.tripModelCost = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_cost;
                // this.tripBaselineCost = this.routeJson.features[this.routeJson.features.length - 1].properties.agg_baseline;
                //
                // this.tripBaselineAbsError = Math.abs(this.tripActualCost - this.tripBaselineCost);
                // this.tripBaselinePercentageError = (this.tripBaselineAbsError / this.tripActualCost) * 100;
                // this.tripModelAbsError = Math.abs(this.tripActualCost - this.tripModelCost);
                // this.tripModelPercentageError = (this.tripModelAbsError / this.tripActualCost) * 100;

                // style: function(feature) {
                //     switch (feature.properties.party) {
                //         case 'Republican': return {color: "#ff0000"};
                //         case 'Democrat':   return {color: "#0000ff"};
                //     }
                // }



                // TODO: Need length on segments to calculate error per meters
                // Find max error for gradent calc
                const maxErrorFeature = this.routeJson.features.reduce((prev, current) => {
                    return this.meterError(prev) > this.meterError(current) ? prev : current;
                });
                const maxError = this.meterError(maxErrorFeature);
                console.log(maxError);




                // actual: 51.0916672646999
                // endpoint: 1088151
                // id: 4338709
                // predicted: 54.5486
                // segmentno: 1
                // startpoint: 85611
                // trip_actual: 51.0916672646999
                // trip_predicted: 54.5486

                // ff0000 red
                // 0000FF blue
                // const hex = Number(200).toString(16);

                this.leafLayers[0] = geoJSON(this.routeJson, {style:
                        (feature) => {
                            // console.log(feature);

                            const error = this.meterError(feature);
                            const rgbNormalisedError = ((error / maxError) * 256) - 1;
                            console.log(rgbNormalisedError);
                            let greenHex = Number(Math.floor(255 - rgbNormalisedError)).toString(16);
                            greenHex = greenHex.length === 1 ? "0" + greenHex : greenHex;
                            console.log(Math.floor(255 - rgbNormalisedError) + " " + greenHex);
                            let redHex = Number(Math.floor(rgbNormalisedError)).toString(16);
                            redHex = redHex.length === 1 ? "0" + redHex : redHex;
                            console.log(Math.floor(rgbNormalisedError) + " " + redHex);
                            const hex = '#' + redHex + greenHex + '00';
                            console.log(hex);
                            console.log('-');


                            return {
                                color: hex,
                                weight: 5,
                                opacity: 0.85};
                        },
                        onEachFeature: (feature, layer) => {
                            layer.bindPopup('Fejl per meter: ' + this.meterError(feature));
                        }
                });




                this.leafMap.fitBounds(this.leafLayers[0].getBounds());
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
        this.leafMap = mp;
        this.showTrip();
    }

    ngOnInit(): void {
        this.leafOptions = {
            layers: [
                tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 18,
                    attribution: this.attribution
                })
            ],
            zoom: 13,
            center: this.aalLatLong
        };
    }

    meterError(feature: any) {
        // TODO: When segment distance is available, use it here
        return Math.abs(feature.properties.predicted - feature.properties.actual);
    }

    useSegmentModel(b: boolean) {
        this.usingSegmentModel = b;
        this.showTrip();
    }
}
