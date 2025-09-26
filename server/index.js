import express from "express";

const app = express();
app.use(express.json({ limit: "5mb" }));

app.post("/assert", async (req, res) => {
  // For demo: accept and log. Add real App Attest verification later.
  const { keyId, assertion, proof, publicInputs } = req.body ?? {};
  console.log("assert key:", keyId, "proof bytes:", proof?.length ?? 0, "pubs:", publicInputs?.length ?? 0);
  return res.json({ ok: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`server listening on :${PORT}`));
