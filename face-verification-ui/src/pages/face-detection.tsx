// src/FaceDetection.tsx
import  { useEffect, useRef, useState } from "react";
import { FACE_DETECTION_THRESHOLDS, useFaceDetection } from "../hooks/use-face-detection";
import Webcam from "react-webcam";
import ColorScanning, { ScanData } from "../components/colors-scanning";
import { useFaceCapture } from "../hooks/use-face-capture";
import { SCAN_COLORS } from "../common/constants";
import { useMobile } from "../hooks/use-mobile";

// Constants for face and overlay thresholds

const SIMULATE_SCAN = true; // Set to true for data collection

const FaceDetection = () => {
  const videoRef = useRef<any>(null);
  
  const [isCapturing, setIsCapturing] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [scanData, setScanData] = useState<ScanData>({
    currentColorIndex: 0,
    scanPosition: 0,
    previousColor: 'transparent'
  });
  const [verificationStage, setVerificationStage] = useState<'initial' | 'moving-closer' | 'scanning'>('initial');
  const [alignmentProgress, setAlignmentProgress] = useState(0);
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<string>('');

  const {isMobileView} = useMobile();

  const {
    isOverlay,
    canvasRef,
    isFaceInsideBoundary,
    isFaceFar,
    isFaceAlignedWithOverlay,
    isFaceTooClose,
    // isFaceNearBorder, // TODO Use this later
    getShapeSize,
    faceBox,                  // Add this
    isIdealStartPosition  ,
  } = useFaceDetection({
    videoPlayerRef: videoRef,
  });

  // Add this new useEffect for getting camera devices
  useEffect(() => {
    const getDevices = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        setDevices(videoDevices);
        if (videoDevices.length > 0) {
          setSelectedCamera(videoDevices[0].deviceId);
        }
      } catch (error) {
        console.error('Error getting devices:', error);
      }
    };

    getDevices();
  }, []);

  // Add cleanup function for camera
  useEffect(() => {
    return () => {
      if (videoRef.current?.video?.srcObject) {
        const stream = videoRef.current.video.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const { stopCapture ,isScanComplete} = useFaceCapture({
    videoRef,
    isCapturing,
    ...scanData
  });

  useEffect(() => {
    if (isScanComplete) {
      handleScanComplete();
    }
  }, [isScanComplete]);

  const handleUserMedia = () => {
    setIsCameraReady(true);
  };

  const handleScanComplete = async () => {
    await stopCapture();
    setIsCapturing(false);
    setIsCompleted(true);
    setIsCameraReady(false); // Reset camera ready state

    // Stop camera stream
    if (videoRef.current?.video?.srcObject) {
      const stream = videoRef.current.video.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.video.srcObject = null;
    }
  };

  const handleScanUpdate = (data: ScanData) => {
    if (SIMULATE_SCAN) {
      // Simulate scan progress
      let nextColorIndex = data.currentColorIndex;
      let nextScanPosition = data.scanPosition + 20; // Increase by 20% per call

      if (nextScanPosition >= 100) {
        nextScanPosition = 100;
        nextColorIndex += 1;
      }

      if (nextColorIndex >= SCAN_COLORS.length) {
        // All colors scanned, complete
        handleScanComplete();
        return;
      }

      setScanData({
        ...data,
        currentColorIndex: nextColorIndex,
        scanPosition: nextScanPosition,
        previousColor: SCAN_COLORS[nextColorIndex - 1] || 'transparent'
      });
    } else {
      setScanData(data);
      if (data.currentColorIndex === SCAN_COLORS.length - 1 && data.scanPosition >= 99.9) {
        handleScanComplete();
      }
    }
  };

  const getFaceStatusMessage = () => {
    const messages = {
      initial: {
        tooClose: { text: "Move back slightly", icon: "↔️" },
        tooFar: { text: "Move closer to the camera", icon: "↔️" },
        notIdeal: { text: "Center your face in the frame", icon: "🎯" },
        perfect: { text: "Perfect position", icon: "✅" }
      },
      moving: {
        notCentered: { text: "Keep your face centered", icon: "🎯" },
        tooFar: { text: "Slowly move closer...", icon: "" },
        tooClose: { text: "Move back slightly", icon: "" },
        perfect: { text: "Hold position", icon: "✅" }
      },
      scanning: { text: "Stay still while scanning", icon: "⏳" }
    };
  
    if (verificationStage === 'initial') {
      if (!isIdealStartPosition) {
        if (isFaceTooClose) return messages.initial.tooClose;
        if (isFaceFar) return messages.initial.tooFar;
        return messages.initial.notIdeal;
      }
      return messages.initial.perfect;
    }
  
    if (verificationStage === 'moving-closer') {
      if (!isFaceInsideBoundary) return messages.moving.notCentered;
      if (isFaceFar) return messages.moving.tooFar;
      if (isFaceTooClose) return messages.moving.tooClose;
      if(alignmentProgress < 98) return messages.moving.tooFar;
      return messages.moving.perfect;
    }
  
    return messages.scanning;
  };

  useEffect(() => {
    if (SIMULATE_SCAN) {
      if (verificationStage === 'moving-closer') {
        setVerificationStage('scanning');
        setIsCapturing(true);
      }
      return;
    }
    if (verificationStage === 'moving-closer' && faceBox) { // Check if faceBox exists
        const { width: shapeWidth, height: shapeHeight } = getShapeSize();
        const faceSize = Math.max(faceBox.width, faceBox.height);
        const overlaySize = Math.max(shapeWidth, shapeHeight);
        const faceSizeRatio = faceSize / overlaySize;
        
        // Reset progress if face is too far or too close
        if (faceSizeRatio < FACE_DETECTION_THRESHOLDS.INITIAL_MIN_FACE_SIZE_RATIO) {
          setAlignmentProgress(0);
            return;
        }
        
        // Calculate normalized progress only when face is in valid range
        const normalizedProgress = (
            (faceSizeRatio - FACE_DETECTION_THRESHOLDS.INITIAL_MIN_FACE_SIZE_RATIO) /
            (FACE_DETECTION_THRESHOLDS.FINAL_MIN_FACE_SIZE_RATIO - FACE_DETECTION_THRESHOLDS.INITIAL_MIN_FACE_SIZE_RATIO)
        );
      
        // Smoother easing function
        const easedProgress = Math.min(100, Math.max(0,
            Math.pow(normalizedProgress, 1.5) * 100
        ));      
        setAlignmentProgress(easedProgress);
        
        // Start scanning when aligned perfectly
        if (easedProgress >= 98 && 
          isFaceInsideBoundary && 
          !isFaceTooClose && 
          !isFaceFar && 
          isFaceAlignedWithOverlay) {
          setVerificationStage('scanning');
          setIsCapturing(true);
      }
    }
}, [faceBox, verificationStage, getShapeSize, isFaceInsideBoundary, isFaceTooClose]);

  // Modify the restart button handler
  const handleRestart = () => {
    window.location.reload(); // Reload the page to reset the u
  
  };

  const handleStartCapture = () => {
    setIsCapturing(true);
    setVerificationStage('moving-closer');

  };

  const isValidFacePosition = true;

  const cameraWidth = isMobileView ? "90vw" : "30vw";
  const cameraHeight = isMobileView ? "60vh" : "25vw";
  const canvasWidth = isMobileView ? "95vw" : "35vw";
  const canvasHeight = isMobileView ? "65vw" : "30vw";
  const statusFontSize = isMobileView ? "1rem" : "1.1rem";
  const statusPadding = isMobileView ? "10px 12px" : "12px 20px";
  const buttonFontSize = isMobileView ? "1rem" : "1.1rem";
  const buttonPadding = isMobileView ? "12px 0" : "10px 20px";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        minHeight: "100vh",
        background: isMobileView ? "white" : "white",
        padding: isMobileView ? "10px 0" : "0"
      }}
    >
      <h1
        style={{
          fontSize: isMobileView ? "1.3rem" : "1.8rem",
          color: "#1e293b",
          marginBottom: isMobileView ? "1rem" : "1.5rem",
          fontWeight: "500"
        }}
      >
        Face Verification
      </h1>

      {isCompleted ? (
        <div
          style={{
            textAlign: "center",
            padding: isMobileView ? "1.2rem" : "2rem",
            backgroundColor: "#f0f9ff",
            borderRadius: "12px",
            margin: isMobileView ? "1rem" : "2rem",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            transition: "all 0.3s ease"
          }}
        >
          <h2 style={{ color: "#0369a1", marginBottom: "1rem" }}>Thank You!</h2>
          <p style={{ color: "#64748b" }}>
            Your verification is complete.
          </p>
          <button
            onClick={handleRestart}
            style={{
              marginTop: "1rem",
              padding: buttonPadding,
              fontSize: buttonFontSize,
              backgroundColor: "#0284c7",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              width: isMobileView ? "90vw" : undefined,
              maxWidth: "350px"
            }}
          >
            Start New Verification
          </button>
        </div>
      ) : (
        <>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              backgroundColor: isValidFacePosition ? "#f0fdf4" : "#fef2f2",
              padding: statusPadding,
              borderRadius: "8px",
              marginBottom: isMobileView ? "10px" : "20px",
              transition: "all 0.3s ease",
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              zIndex: 10000001
            }}
          >
            <span style={{ fontSize: "1.5rem", lineHeight: "1" }}>
              {getFaceStatusMessage().icon}
            </span>
            <span
              style={{
                color: isValidFacePosition ? "#16a34a" : "#dc2626",
                fontSize: statusFontSize,
                fontWeight: "500",
                transition: "color 0.3s ease"
              }}
            >
              {getFaceStatusMessage().text}
            </span>
          </div>

          {verificationStage === "moving-closer" && (
            <div
              style={{
                width: isMobileView ? "90vw" : "100%",
                maxWidth: isMobileView ? "90vw" : "28rem",
                margin: "1rem auto 1.5rem auto"
              }}
            >
              <div
                style={{
                  width: "100%",
                  background: "#f1f5f9",
                  borderRadius: "999px",
                  height: "8px"
                }}
              >
                <div
                  style={{
                    background: "#2563eb",
                    height: "8px",
                    borderRadius: "999px",
                    width: `${alignmentProgress}%`,
                    transition: "all 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
                  }}
                />
              </div>
            </div>
          )}

          <div
            style={{
              position: "relative",
              borderRadius: "12px",
              overflow: "hidden",
              boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
              transition: "all 0.3s ease",
              width: cameraWidth,
              height: cameraHeight,
              maxWidth: "100vw",
              maxHeight: isMobileView?"80vh":"80vw",
            }}
          >
            <Webcam
              audio={false}
              height={"100%"}
              width={"100%"}
              ref={videoRef}
              screenshotFormat="image/jpeg"
              autoPlay={true}
              playsInline={true}
              onUserMedia={handleUserMedia}
              muted={true}
              style={{
                width: cameraWidth,
                height: cameraHeight,
                objectFit: "cover",
                transition: "all 0.3s ease",
                borderRadius: "12px"
              }}
              videoConstraints={{
                deviceId: selectedCamera,
                ...{
                  width: {
                      min: 320,
                      ideal: 640,
                  },
                  height: {
                      min: 240,
                      ideal: 480,
                  },
                  frameRate: { min: 15, ideal: 30, max: 30 },
                  facingMode: 'user',
              }
              }}
              mirrored={true}
              screenshotQuality={1}
            />
            {isOverlay && isCameraReady && (
              <canvas
                ref={canvasRef}
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: canvasWidth,
                  height: canvasHeight,
                  transition: "all 0.3s ease",
                  pointerEvents: "none"
                }}
              />
            )}
            {verificationStage === "scanning" && isCapturing && (
              <ColorScanning onScanUpdate={handleScanUpdate} />
            )}
          </div>

          {verificationStage === "initial" && devices.length > 1 && (
            <select
              value={selectedCamera}
              onChange={(e) => setSelectedCamera(e.target.value)}
              style={{
                marginTop: isMobileView ? "0.7rem" : "1rem",
                padding: isMobileView ? "0.5rem" : "0.5rem",
                borderRadius: "4px",
                border: "1px solid #e2e8f0",
                backgroundColor: "white",
                cursor: "pointer",
                fontSize: isMobileView ? "1rem" : "0.9rem",
                width: isMobileView ? "90vw" : undefined,
                maxWidth: "350px"
              }}
            >
              {devices.map((device) => (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label || `Camera ${devices.indexOf(device) + 1}`}
                </option>
              ))}
            </select>
          )}

          {verificationStage === "initial" && !isValidFacePosition && (
            <div
              style={{
                marginTop: isMobileView ? "0.7rem" : "1rem",
                padding: isMobileView ? "0.6rem 0.7rem" : "0.75rem 1rem",
                backgroundColor: "#fee2e2",
                borderRadius: "8px",
                color: "#991b1b",
                fontSize: isMobileView ? "0.95rem" : "0.9rem",
                transition: "all 0.3s ease",
                width: isMobileView ? "90vw" : undefined,
                maxWidth: "350px"
              }}
            >
              Please position your face fully within the frame.
            </div>
          )}

          <button
            onClick={handleStartCapture}
            style={{
              padding: buttonPadding,
              backgroundColor: isValidFacePosition ? "#2563eb" : "#cccccc",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: isValidFacePosition ? "pointer" : "not-allowed",
              marginTop: isMobileView ? "1.2rem" : "20px",
              fontSize: buttonFontSize,
              width: isMobileView ? "90vw" : undefined,
              maxWidth: "350px",
              transition: "all 0.3s ease"
            }}
            disabled={!isValidFacePosition || isCapturing}
          >
            {isCapturing ? "Scanning..." : "Start Verification"}
          </button>
        </>
      )}
    </div>
  );
};

export default FaceDetection;
