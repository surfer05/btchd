import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "./MapLabels.css";

const MapLabels = ({ points }) => {
  if (!points || points.length === 0) return null;

  // Get min and max strength
  const strengths = points.map((p) => p.strength);
  const minStrength = Math.min(...strengths);
  const maxStrength = Math.max(...strengths);

  const minFont = 14; // px
  const maxFont = 36; // px - increased from 28

  // Sort DESCENDING by strength so higher strength overlays lower (appears on top)
  const sortedPoints = [...points].sort((a, b) => b.strength - a.strength);

  return (
    <>
      {sortedPoints.map((point, idx) => {
        // Map strength to font size
        // Replace norm computation
        // norm remap to boost top strengths without inflating all labels
        const raw =
          maxStrength - minStrength
            ? (point.strength - minStrength) / (maxStrength - minStrength)
            : 0;
        const norm = Math.pow(raw, 1.25); // mild, adjust 1.2–1.4 for effect [web:16][web:10]

        // Calculate z-index based on strength (higher strength = higher z-index)
        const zIndexValue = 1000 + point.strength * 100;

        const icon = L.divIcon({
          // Pass CSS variables; avoid inline font-size so CSS can be responsive
          html: `<div class="label-text" style="--scale:${norm};--z:${zIndexValue}">${point.label}</div>`,
          className: "casual-label",
          // Let CSS/content drive size & anchor; do not force nulls
          // iconSize: undefined,
          // iconAnchor: undefined,
        });

        return (
          <Marker
            key={`${point.lat}-${point.lon}-${idx}`}
            position={[point.lat, point.lon]}
            icon={icon}
            zIndexOffset={-point.strength * 100}
          />
        );
      })}
    </>
  );
};

export default MapLabels;
