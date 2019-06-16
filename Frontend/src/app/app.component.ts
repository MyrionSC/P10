/* tslint:disable:max-line-length */
import {Component, Inject, OnInit} from '@angular/core';
import {Circle, Point, geoJSON, latLng, Layer, tileLayer, layerGroup, LatLng} from 'leaflet';
import {HttpClient} from '@angular/common/http';
import {DOCUMENT} from '@angular/platform-browser';
import {Feature, FeatureCollection, GeoJsonObject} from 'geojson';
import {LeafletLayerDiff} from '@asymmetrik/angular2-leaflet/dist/leaflet/layers/leaflet-layer-diff.model';
import {merge} from 'rxjs';

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
    pointSeparation = false;

    loadTrip(scrollTo: boolean) {
        const model = this.usingSegmentModel ? 'segment' : 'supersegment';
        const url = './assets/trip' + this.selectedTrip + '-' + model + '.json';
        console.log('GET: ' + url);

        this.tripLoading = true;
        this.leafLayers = [];

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

                // TODO: Need length on segments to calculate error per meters
                // Find max error for gradient calc
                // TODO: Instead of using max error decide on some error / meter range so models can be compared
                const maxErrorFeature = this.routeJson.features.reduce((prev, current) => {
                    return this.meterError(prev) > this.meterError(current) ? prev : current;
                });
                const maxError = this.meterError(maxErrorFeature);

                // route layer
                this.leafLayers[0] = geoJSON(this.routeJson, {style:
                        (feature) => {
                            const error = this.meterError(feature);
                            const rgbNormalisedError = ((error / maxError) * 256) - 1;
                            let greenHex = Number(Math.floor(255 - rgbNormalisedError)).toString(16);
                            greenHex = greenHex.length === 1 ? "0" + greenHex : greenHex;
                            let redHex = Number(Math.floor(rgbNormalisedError)).toString(16);
                            redHex = redHex.length === 1 ? "0" + redHex : redHex;
                            const hex = '#' + redHex + greenHex + '00';

                            return {
                                color: hex,
                                weight: 5,
                                opacity: 0.85};
                        },
                        onEachFeature: (feature, layer) => {
                            layer.bindPopup(feature.properties.id + ': Fejl per meter: ' + this.meterError(feature));
                        }
                });



                // point layer
                // unfortunately we cannot just take first and last LatLng from each feature because the individual segment's
                    // direction is not always right. Instead we remove all duplicates from merged list of linestrings coords
                    // and take first and last of these.
                if (this.pointSeparation) {
                    const pointsGroup = layerGroup();
                    for (const feature of this.routeJson.features) {
                        // flatten array and convert to LatLngs
                        // @ts-ignore
                        let merged: Array<any> = Array.prototype.concat.apply([], feature.geometry.coordinates);
                        merged = merged.map((item) => {
                            return new LatLng(item[1], item[0]);
                        });
                        // take only ones where no duplicate
                        merged = merged.filter((item: LatLng) => {
                            return merged.findIndex((item2: LatLng) => {
                                return item !== item2 && item.equals(item2);
                            }) === -1;
                        });

                        // The first and last are the ones we want
                        const startcircle = new Circle(merged[0], {
                            radius: 3,
                            color: '#444444'
                        });
                        pointsGroup.addLayer(startcircle);
                        const stopcircle = new Circle(merged[merged.length - 1], {
                            radius: 3,
                            color: '#444444'
                        });
                        pointsGroup.addLayer(stopcircle);
                    }
                    this.leafLayers[1] = pointsGroup;
                }

                if (scrollTo) {
                    this.scrollToTrip();
                }
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

    changeTrip() {
        this.loadTrip(true);
        // this.scrollToTrip();

    }

    scrollToTrip() {
        this.leafMap.fitBounds(this.leafLayers[0].getBounds());
    }

    mapReady(mp) {
        this.leafMap = mp;
        this.loadTrip(true);
        // scroll to layers
        // this.scrollToTrip();
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
        this.loadTrip(false);
    }

    usePointSeparation() {
        this.pointSeparation = !this.pointSeparation;
        this.loadTrip(false);
    }
}
