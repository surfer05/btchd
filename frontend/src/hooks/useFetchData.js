import { useState, useEffect } from "react";

export const useFetchData = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    try {
      // Hardcoded JSON
      const json = [
        {
          latitude: 28.6139,
          longitude: 77.209,
          name: "Too much smoke",
          strength: 3,
        },
        {
          latitude: 28.6448,
          longitude: 77.2167,
          name: "Heavy traffic",
          strength: 5,
        },
        {
          latitude: 28.5355,
          longitude: 77.391,
          name: "Crowded market",
          strength: 4,
        },
        {
          latitude: 28.4089,
          longitude: 77.3178,
          name: "Construction noise",
          strength: 2,
        },
        {
          latitude: 28.4595,
          longitude: 77.0266,
          name: "Green park",
          strength: 1,
        },
        {
          latitude: 28.7041,
          longitude: 77.1025,
          name: "Street festival",
          strength: 4,
        },
        {
          latitude: 28.6692,
          longitude: 77.4538,
          name: "Shopping mall",
          strength: 3,
        },
        {
          latitude: 28.5273,
          longitude: 77.0689,
          name: "Busy intersection",
          strength: 5,
        },
        {
          latitude: 28.6129,
          longitude: 77.2295,
          name: "Quiet lane",
          strength: 1,
        },
        {
          latitude: 28.7025,
          longitude: 77.1113,
          name: "Old monument",
          strength: 2,
        },
      ];

      // Simulate async fetch with a short delay
      setTimeout(() => {
        setData(json);
        setLoading(false);
      }, 100); // 100ms delay
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  }, []);

  return { data, loading, error };
};
