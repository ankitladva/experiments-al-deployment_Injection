import { useEffect, useState } from "react";
import { Button } from "@mui/material";
import FaceDetection from "./face-detection";
import { useMobile } from "../hooks/use-mobile";
 // Replace with your Flask backend URL

function Verification() {
    const [start, setStart] = useState(false);
    const [hasCameraAccess, setHasCameraAccess] = useState<boolean | null>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const {isMobileView} = useMobile()

    useEffect(() => {
      let mounted = true;
      const checkPermission = async () => {
        try {
          // Some browsers support Permissions API for camera under name: 'camera'
          // Fallback behavior will be handled by attempting getUserMedia on button click
          // @ts-ignore - TS may not recognize 'camera' in PermissionName
          if (navigator.permissions && (navigator.permissions as any).query) {
            // @ts-ignore
            const status = await navigator.permissions.query({ name: 'camera' });
            if (!mounted) return;
            if (status.state === 'granted') setHasCameraAccess(true);
            else if (status.state === 'denied') setHasCameraAccess(false);
            else setHasCameraAccess(null); // 'prompt'
            status.onchange = () => {
              if (!mounted) return;
              // @ts-ignore
              const state = status.state;
              if (state === 'granted') setHasCameraAccess(true);
              else if (state === 'denied') setHasCameraAccess(false);
              else setHasCameraAccess(null);
            };
          }
        } catch {
          // Ignore; not all browsers support Permissions API for camera
        }
      };
      checkPermission();
      return () => { mounted = false; };
    }, []);

    const requestCameraAndStart = async () => {
      setErrorMessage(null);
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        // Immediately stop tracks; FaceDetection will manage its own stream
        stream.getTracks().forEach(t => t.stop());
        setHasCameraAccess(true);
        setStart(true);
      } catch (err: any) {
        setHasCameraAccess(false);
        const msg = err?.name === 'NotAllowedError' || err?.name === 'SecurityError'
          ? 'Camera access is required. Please allow camera permissions in your browser settings and try again.'
          : 'Failed to access the camera. Please ensure no other app is using it and try again.';
        setErrorMessage(msg);
      }
    };

    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: isMobileView ? "0" : "50px" }}>
        {!start ? (
          <>
            {errorMessage ? (
              <div style={{
                background: '#fee2e2',
                color: '#991b1b',
                padding: '10px 14px',
                borderRadius: 8,
                marginBottom: 12,
                maxWidth: 420,
                textAlign: 'center'
              }}>
                {errorMessage}
              </div>
            ) : null}
            <Button
              variant="contained"
              color="primary"
              onClick={requestCameraAndStart}
              style={{ padding: "10px 30px", fontSize: "18px",bottom:"10vh",position:"absolute" }}
            >
              {hasCameraAccess ? 'Start Verification' : 'Enable Camera to Start'}
            </Button>
          </>
        ) : (
          <FaceDetection />
        )}
      </div>
    );
}

export default Verification;