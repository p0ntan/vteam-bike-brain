/**
 * This script is to transform route data
 * into an csv file that can be analyzed for example inexcel, see example excel file.
 * Note! This script does not run automatically, run this script after you have generated the json bike files
 */

const fs = require('fs');
const counter = require("../counter.json");
const geoTools = require('geo-tools');

fs.writeFileSync("./stats.csv", `"bike","route","length_meter", "length_birdway","duration_sec", "duration_time", "count_coords", "seconds per interval"\r\n`);

for (let i = 1; i < counter.bike; i++) {
    const bike = require(`./${i}.json`);

    for (let j = 0; j<bike.trips.length; j++) {
        const from = {
            lng: bike.trips[j].coords[0][0],
            lat: bike.trips[j].coords[0][1]
        }
        const to = {
            lng: bike.trips[j].coords[bike.trips[j].coords.length - 1][0],
            lat: bike.trips[j].coords[bike.trips[j].coords.length - 1][1]
        }
        const meters = toMeters(distance(from, to));
        fs.appendFileSync("./stats.csv", `"${i}","${j+1}","${bike.trips[j].summary.distance}","${meters}","${bike.trips[j].summary.duration}","${Math.floor(bike.trips[j].summary.duration/60)} min ${Math.round(bike.trips[j].summary.duration % 60)} sec","${bike.trips[j].coords.length}","${bike.trips[j].summary.duration != "" ? bike.trips[j].coords.length / bike.trips[j].summary.duration : "" }"\r\n`);
    }
}