import { useState, useEffect } from "react";
import { useMapEvents } from "react-leaflet";

const ZoomWatcher = ({ onZoomChange }) => {
  const map = useMapEvents({
    zoomend: () => {
      const currentZoom = map.getZoom();
      onZoomChange(currentZoom);
    },
  });

  return null; // this component just listens, no UI
};
export default ZoomWatcher;
