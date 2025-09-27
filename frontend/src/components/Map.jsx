import { MapContainer, TileLayer } from "react-leaflet";
import MapLabels from "./MapLabels";
import { useFetchData } from "../hooks/useFetchData";

const Map = () => {
  // Replace this URL with your API endpoint
  const { data: points, loading, error } = useFetchData("/api/points.json");

  return (
    <MapContainer
      center={[28.6139, 77.209]} // Delhi
      zoom={13}
      style={{ height: "100vh", width: "100vw" }}
      maxBounds={[
        [28.35, 76.85], // southwest
        [28.9, 77.6], // northeast
      ]}
      maxZoom={18}
      minZoom={11}
      maxBoundsViscosity={1.0} // restrict panning outside Delhi
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      {!loading && !error && <MapLabels points={points} />}
    </MapContainer>
  );
};

export default Map;
