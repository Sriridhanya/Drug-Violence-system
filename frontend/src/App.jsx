import { useRef, useState } from "react";
import axios from "axios";

const API = "http://localhost:8080"; // Spring Boot

export default function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [alert, setAlert] = useState("");
  const [risk, setRisk] = useState(0);
  const [socialText, setSocialText] = useState("");
  const [textResult, setTextResult] = useState("");

  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
  };

  const captureFrameBase64 = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    // base64 jpeg (remove prefix for backend)
    return canvas.toDataURL("image/jpeg");
  };

  const detect = async (type) => {
    setAlert("");
    const imageDataUrl = captureFrameBase64();
    const res = await axios.post(`${API}/api/detect/${type}`, { imageDataUrl });
    const { detected, score, riskDelta, message } = res.data;

    if (detected) setAlert(message || `⚠ ${type} detected`);
    setRisk((prev) => Math.min(100, Math.max(0, prev + (riskDelta ?? 0))));
  };

  const analyzeText = async () => {
    const res = await axios.post(`${API}/api/text/analyze`, { text: socialText });
    setTextResult(res.data.summary);
    setRisk((prev) => Math.min(100, Math.max(0, prev + (res.data.riskDelta ?? 0))));
  };

  const riskStatus =
    risk > 70 ? "High Risk" : risk > 40 ? "Moderate Risk" : "Low Risk";

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f5f1e8" }}>
      <div style={{ width: 230, padding: 20, background: "#e8dfcf" }}>
        <h2 style={{ color: "#8b6f47" }}>AI Dashboard</h2>
      </div>

      <div style={{ flex: 1, padding: 25 }}>
        <h1 style={{ marginBottom: 20, color: "#8b6f47" }}>
          AI-Based Drug Violence Detection & Prevention System
        </h1>

        <div style={cardStyle}>
          <h3 style={h3Style}>1. Surveillance Monitoring</h3>
          <video ref={videoRef} autoPlay style={videoStyle} />
          <canvas ref={canvasRef} style={{ display: "none" }} />
          <div style={{ marginTop: 10 }}>
            <button style={btnStyle} onClick={startCamera}>Start Camera</button>
            <button style={btnStyle} onClick={() => detect("weapon")}>Detect Weapon</button>
            <button style={btnStyle} onClick={() => detect("violence")}>Detect Violence</button>
          </div>
          {alert && <div style={alertStyle}>{alert}</div>}
        </div>

        <div style={cardStyle}>
          <h3 style={h3Style}>2. Digital Drug Trafficking Detection</h3>
          <textarea
            rows={3}
            value={socialText}
            onChange={(e) => setSocialText(e.target.value)}
            placeholder="Enter suspicious social media text..."
            style={inputStyle}
          />
          <button style={btnStyle} onClick={analyzeText}>Analyze Text</button>
          <p>{textResult}</p>
        </div>

        <div style={cardStyle}>
          <h3 style={h3Style}>5. Risk Scoring Dashboard</h3>
          <div style={{ fontSize: 22, fontWeight: "bold", color: "#5c4b3b" }}>
            {risk.toFixed(2)}% — {riskStatus}
          </div>
          <div style={{ height: 15, background: "#e8dfcf", borderRadius: 20, overflow: "hidden", marginTop: 10 }}>
            <div style={{ height: "100%", width: `${risk}%`, background: "#8b6f47", transition: "0.4s" }} />
          </div>
        </div>
      </div>
    </div>
  );
}

const cardStyle = {
  background: "white",
  padding: 25,
  borderRadius: 15,
  marginBottom: 20,
  boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
};
const h3Style = { marginBottom: 15, color: "#8b6f47" };
const inputStyle = {
  width: "100%",
  padding: 10,
  margin: "8px 0",
  border: "1px solid #d6c7b2",
  borderRadius: 8,
  background: "#f9f6f0",
};
const btnStyle = {
  padding: "8px 15px",
  background: "#8b6f47",
  border: "none",
  color: "white",
  cursor: "pointer",
  borderRadius: 8,
  marginRight: 8,
};
const videoStyle = { width: "100%", maxWidth: 350, borderRadius: 10, border: "2px solid #d6c7b2" };
const alertStyle = { marginTop: 10, padding: 10, background: "#c0392b", color: "white", borderRadius: 8 };