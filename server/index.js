// server/index.js
import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 8787;

const app = express();
app.use(express.json({ limit: "1mb" }));

// data file: ../delhi/reviews.json
const dataDir = path.resolve(__dirname, "..", "delhi");
const dbPath = path.join(dataDir, "reviews.json");

function load() {
  if (!fs.existsSync(dbPath)) {
    return { schema: 1, city: "Delhi", geohashPrecision: 7, reviews: [] };
  }
  return JSON.parse(fs.readFileSync(dbPath, "utf8"));
}
function save(db) {
  if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
  fs.writeFileSync(dbPath, JSON.stringify(db, null, 2));
}

// POST /submit — add/update a review (one per addr+geohash per 24h)
app.post("/submit", (req, res) => {
  try {
    const {
      addr,
      signature,
      proofHex,
      publicInputsHex,
      geohash7,
      review,
      expiresAt,
    } = req.body || {};
    if (
      !geohash7 ||
      !review ||
      !Array.isArray(review.categories) ||
      typeof review.rating !== "number" ||
      typeof review.text !== "string"
    ) {
      return res.status(400).json({ ok: false, error: "invalid payload" });
    }

    // Log the proof information for debugging
    console.log("Received proof data:");
    console.log("- Proof Hash:", proofHex);
    console.log("- Public Inputs:", publicInputsHex);
    console.log("- Expires At:", expiresAt);
    const now = Math.floor(Date.now() / 1000);
    const a =
      addr && typeof addr === "string"
        ? addr
        : "0x0000000000000000000000000000000000000000";

    const db = load();
    // 24h guardrail per (addr, geohash7)
    db.reviews = db.reviews.filter(
      (r) =>
        !(r.addr === a && r.geohash7 === geohash7 && now - r.timestamp < 86400)
    );
    db.reviews.push({
      addr: a,
      geohash7,
      categories: review.categories,
      rating: review.rating,
      text: review.text,
      timestamp: now,
      proofHex: proofHex || "0x",
      publicInputsHex: publicInputsHex || "0x",
      expiresAt: expiresAt || 0,
      signature: signature || null,
    });
    save(db);
    res.json({ ok: true, data: db });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok: false, error: String(e.message || e) });
  }
});

// GET /reviews?prefix=ttvj8 — fetch by geohash prefix (optional)
app.get("/reviews", (req, res) => {
  try {
    const prefix = (req.query.prefix || "").toString();
    const db = load();
    const rows = prefix
      ? db.reviews.filter((r) => r.geohash7.startsWith(prefix))
      : db.reviews;
    res.json({ reviews: rows });
  } catch (e) {
    res.status(500).json({ ok: false, error: String(e.message || e) });
  }
});

app.listen(PORT, () =>
  console.log(`relayer (off-chain) listening on :${PORT}`)
);
