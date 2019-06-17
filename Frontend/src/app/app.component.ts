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
        '240',
        '5678'
    ];
    selectedTrip = "202094";
    usingModel = "supersegment";

    // leaflet stuff
    leafOptions = {};
    leafLayers = [];
    leafMap: any;
    aalLatLong = latLng(57.046707, 9.935932);
    attribution = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors,' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>';
    routeJson: FeatureCollection;

    // metrics
    tripDistance: number;
    tripSegmentsNum: number;
    tripActualCost: number;
    tripPredictedCost: number;
    tripMAError: number;
    tripMAMError: number;
    tripErrorPercentage: number;

    // visual bools
    estimateShown = true;
    tripLoaded = false;
    tripLoading = false;
    pointSeparation = false;

    loadTrip(scrollTo: boolean) {
        // const model = this.usingSegmentModel ? 'segment' : 'supersegment';

        const url = './assets/trip' + this.selectedTrip + '-' + this.usingModel + '.json';
        console.log('GET: ' + url);

        this.tripLoading = true;
        this.leafLayers = [];

        this.http.get(url).subscribe(
            (res: FeatureCollection) => {
                this.routeJson = res;
                console.log(res);

                // Vis: længde, antal segmenter, aktuelt energiforbrug, estimeret energiforbrug, fejl, fejl i procent
                this.tripDistance = this.routeJson.features.reduce((total, item) => total + item.properties.length, 0) / 1000;
                this.tripSegmentsNum = this.routeJson.features.length;
                this.tripActualCost = this.routeJson.features.reduce((total, item) => total + item.properties.actual, 0);
                this.tripPredictedCost = this.routeJson.features.reduce((total, item) => total + item.properties.predicted, 0);
                this.tripMAError = Math.abs(this.tripActualCost - this.tripPredictedCost);
                this.tripMAMError = Math.abs(this.tripActualCost - this.tripPredictedCost) / (this.tripDistance * 1000);
                this.tripErrorPercentage = (this.tripMAError / this.tripActualCost) * 100;

                // Find max error for gradient calc
                // TODO: Instead of using max error decide on some error / meter range so models can be compared
                // const maxErrorFeature = this.routeJson.features.reduce((prev, current) => {
                //     return this.segmentMAME(prev) > this.segmentMAME(current) ? prev : current;
                // });
                // const maxError = this.segmentMAME(maxErrorFeature);
                // const maxError = 0.3;

                // route layer
                this.leafLayers[0] = geoJSON(this.routeJson, {style:
                        (feature) => {
                            const error = this.segmentMAME(feature);

                            let hex = "";
                            if (error < 0.2) {
                                hex = "#a1aff6";
                            } else if (error < 0.4) {
                                hex = "#d89fd3";
                            } else if (error < 0.6) {
                                hex = "#df65b0";
                            } else if (error < 0.8) {
                                hex = "#dd1c77";
                            } else {
                                hex = "#980043";
                            }

                            return {
                                color: hex,
                                weight: 5,
                                opacity: 0.85};
                        },
                        onEachFeature: (feature, layer) => {
                            layer.bindPopup(feature.properties.id + ': Fejl per meter: ' + this.segmentMAME(feature));
                        }
                });



                // point layer
                // unfortunately we cannot just take first and last LatLng from each feature because the individual segment's
                    // direction is not always right. Instead we remove all duplicates from merged list of linestrings coords
                    // and take first and last of these.
                if (this.pointSeparation) {
                    const pointsGroup = layerGroup();
                    for (const feature of this.routeJson.features) {

                        // @ts-ignore
                        let coords = feature.geometry.coordinates;
                        if (feature.geometry.type === 'MultiLineString') {
                            // flatten array to LineString syntax
                            coords = Array.prototype.concat.apply([], feature.geometry.coordinates);
                        }
                        coords = coords.map((item) => {
                            return new LatLng(item[1], item[0]);
                        });

                        // take only ones where no duplicate
                        coords = coords.filter((item: LatLng) => {
                            return coords.findIndex((item2: LatLng) => {
                                return item !== item2 && item.equals(item2);
                            }) === -1;
                        });

                        // The first and last are the ones we want
                        const startcircle = new Circle(coords[0], {
                            radius: 3,
                            color: '#444444'
                        });
                        pointsGroup.addLayer(startcircle);
                        const stopcircle = new Circle(coords[coords.length - 1], {
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

    changeModel(model: string) {
        this.usingModel = model;
        this.loadTrip(false);
    }

    changeTrip() {
        // TODO: change trip
        this.loadTrip(true);
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

    segmentMAME(feature: any) {
        return Math.abs(feature.properties.predicted - feature.properties.actual) / feature.properties.length;
    }

    usePointSeparation() {
        this.pointSeparation = !this.pointSeparation;
        this.loadTrip(false);
    }
}
