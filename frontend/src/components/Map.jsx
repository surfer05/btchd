import { MapContainer, TileLayer } from "react-leaflet";
import MapLabels from "./MapLabels";
import { useFetchData } from "../hooks/useFetchData";
import ZoomWatcher from "./ZoomWatcher"; // from above
import { useState } from "react";
import "leaflet/dist/leaflet.css";

const Map = () => {
  const [zoom, setZoom] = useState(13);

  // Define data sources per zoom level
  const getUrlForZoom = (zoom) => {
    if (zoom < 13)
      return "https://super-duper-space-waffle-xx49jw799gw3pg7g-5000.app.github.dev/label?city=delhi&level=0";
    if (zoom < 15)
      return "https://super-duper-space-waffle-xx49jw799gw3pg7g-5000.app.github.dev/label?city=delhi&level=3";
    if (zoom < 17)
      return "https://super-duper-space-waffle-xx49jw799gw3pg7g-5000.app.github.dev/label?city=delhi&level=3";
    else
      return "https://super-duper-space-waffle-xx49jw799gw3pg7g-5000.app.github.dev/label?city=delhi&level=3";
  };

  const url = getUrlForZoom(zoom);
  const { data: points, loading, error } = useFetchData(url);

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
      {!loading && !error && <MapLabels points={points} />}
    </MapContainer>
  );
};

export default Map;
