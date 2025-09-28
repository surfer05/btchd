// MapLabels.jsx
import { Marker } from "react-leaflet";
import L from "leaflet";
import "./MapLabels.css";

import { scaleSequential } from "d3-scale";
import { interpolateViridis } from "d3-scale-chromatic";
const colorScale = scaleSequential(interpolateViridis).domain([0, 1]);

const MapLabels = ({ points }) => {
  if (!points || points.length === 0) return null;

  const minFont = 10; // px
  const maxFont = 36; // px

  // Sort DESCENDING by strength so higher strength overlays lower (appears on top)
  const sortedPoints = [...points].sort((a, b) => b.confidence - a.confidence);

  return (
    <>
      {sortedPoints.map((point, idx) => {
        // Linear font size mapping
        // If only one point, use maxFont
        const fontSize =
          points.length === 1
            ? maxFont
            : minFont + (maxFont - minFont) * point.confidence;
        // Color mapping
        // const color = interpolateColor(point.confidence);
        const color = colorScale(point.confidence); // returns a hex color

        // Calculate z-index based on confidence (higher confidence = higher z-index)
        const zIndexValue = 1000 + point.confidence * 100;

        const icon = L.divIcon({
          html: `<div class="label-text" style="--fontSize:${fontSize}px;--labelColor:${color};--z:${zIndexValue}">${point.tag}</div>`,
          className: "casual-label",
        });

        return (
          <Marker
            key={`${point.lat}-${point.lon}-${idx}`}
            position={[point.lat + 0.1, point.lon - 0.1]}
            icon={icon}
            zIndexOffset={-point.confidence * 100}
          />
        );
      })}
    </>
  );
};

export default MapLabels;
