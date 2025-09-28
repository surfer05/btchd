import { MapContainer, TileLayer } from "react-leaflet";
import MapLabels from "./MapLabels";
import ZoomWatcher from "./ZoomWatcher";
import { useState, useEffect } from "react";
import "leaflet/dist/leaflet.css";
import axios from "axios";
// import { level0, level1, level2, level3 } from "../../../data/delhi_labels";

const Map = () => {
  const [zoom, setZoom] = useState(13);
  const [datasets, setDatasets] = useState({
    level0: [],
    level1: [],
    level2: [],
    level3: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ✅ Fetch all datasets only once
  useEffect(() => {
    console.log("Fetching datasets...");
    const fetchAll = async () => {
      try {
        const urls = {
          level0:
            "https://stunning-parakeet-67q75rwv7pv3rpq-5000.app.github.dev/label?city=delhi&level=0",
          level1:
            "https://stunning-parakeet-67q75rwv7pv3rpq-5000.app.github.dev/label?city=delhi&level=1",
          level2:
            "https://stunning-parakeet-67q75rwv7pv3rpq-5000.app.github.dev/label?city=delhi&level=2",
          level3:
            "https://stunning-parakeet-67q75rwv7pv3rpq-5000.app.github.dev/label?city=delhi&level=3",
        };

        const results = await Promise.all(
          Object.entries(urls).map(async ([key, url]) => {
            const response = await axios.get(url);
            return [key, response.data.data]; // take only the array
          })
        );

        setDatasets(Object.fromEntries(results));
      } catch (err) {
        setError(err.message || "Failed to fetch data");
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, []);

  // ✅ Progressive accumulation of points by zoom
  const getDataForZoom = (zoom) => {
    if (!datasets) return [];

    if (zoom < 12) {
      return datasets.level3;
    } else if (zoom < 14) {
      return datasets.level2;
    } else if (zoom < 16) {
      return datasets.level1;
    } else {
      return datasets.level0;
    }
  };

  const points = getDataForZoom(zoom);

  return (
    <MapContainer
      center={[28.6139, 77.209]} // Delhi
      zoom={zoom}
      style={{ height: "100vh", width: "100vw" }}
      maxBounds={[
        [28.35, 76.85],
        [28.9, 77.6],
      ]}
      maxZoom={18}
      minZoom={11}
      maxBoundsViscosity={1.0}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      <ZoomWatcher onZoomChange={setZoom} />
      {!loading && !error && points.length > 0 && <MapLabels points={points} />}
      {/* <MapLabels points={points} /> */}
    </MapContainer>
  );
};

export default Map;

// let points = level3;
// // ✅ Progressive accumulation of points by zoom
// const getDataForZoom = (zoom) => {
//   if (zoom < 12) {
//     return (points = level3);
//   } else if (zoom < 14) {
//     return (points = level2);
//   } else if (zoom < 16) {
//     return (points = level1);
//   } else {
//     return (points = level0);
//   }
// };
// points = getDataForZoom(zoom);
