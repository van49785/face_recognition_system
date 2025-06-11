// src/components/employee/WebcamCapture.jsx
import React, { useRef, useState } from "react";
import Webcam from "react-webcam";

const WebcamCapture = () => {
  const webcamRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [cameraOn, setCameraOn] = useState(true); // ✅ Trạng thái bật/tắt cam

  const capture = () => {
    const image = webcamRef.current.getScreenshot();
    setImageSrc(image);
  };

  const toggleCamera = () => {
    setCameraOn(!cameraOn);
    setImageSrc(null); // Xoá ảnh khi tắt/mở lại
  };

  return (
    <div style={{ textAlign: "center" }}>
      <h2>Face attendance</h2>

      <button onClick={toggleCamera}>
        {cameraOn ? "🔌 Turn off Camera" : "📷 Turn on Camera"}
      </button>

      <br /><br />

      {cameraOn && !imageSrc && (
        <>
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            width={400}
            height={300}
            videoConstraints={{
              facingMode: "user",
            }}
          />
          <br />
          <button onClick={capture}>📸 Take a photo</button>
        </>
      )}

      {imageSrc && (
        <div>
          <h3>Photo just taken:</h3>
          <img src={imageSrc} alt="captured" width={400} />
          <br />
          <button onClick={() => setImageSrc(null)}>🔄 Take a picture</button>
        </div>
      )}
    </div>
  );
};

export default WebcamCapture;
