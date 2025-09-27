import { Marker, Popup } from "react-leaflet";
import L from "leaflet";

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
        const fontSize =
          minFont +
          ((point.strength - minStrength) / (maxStrength - minStrength || 1)) *
            (maxFont - minFont);

        // Calculate z-index based on strength (higher strength = higher z-index)
        const zIndexValue = 1000 + point.strength * 100;

        const icon = L.divIcon({
          html: `<div style="
            font-size: ${fontSize}px;
            font-weight: bold;
            color: white;
            white-space: nowrap;
            font-family: 'Comic Sans MS', cursive, fantasy;
            text-align: center;
            position: relative;
            z-index: ${zIndexValue};
            text-shadow: 
              -1px -1px 0 black,
              1px -1px 0 black,
              -1px 1px 0 black,
              1px 1px 0 black;
            -webkit-text-stroke: 0.5px black;
          ">${point.name}</div>`,
          className: "casual-label",
          iconSize: [null, null], // Auto size
          iconAnchor: [null, null], // Auto anchor
        });

        return (
          <Marker
            key={`${point.latitude}-${point.longitude}-${idx}`}
            position={[point.latitude, point.longitude]}
            icon={icon}
            zIndexOffset={point.strength * 100} // Higher strength = higher z-index
          >
            <Popup>
              <div style={{ fontFamily: "Comic Sans MS, cursive, fantasy" }}>
                <b>{point.name}</b>
                <br />
                <span style={{ color: "#666", fontSize: "13px" }}>
                  Strength: {point.strength}
                </span>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
};

export default MapLabels;
