import { useState, useRef, useCallback } from 'react';

export function useCamera() {
  const [isVideoReady, setIsVideoReady] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const startCamera = useCallback(async () => {
    if (!videoRef.current) return;

    try {
      const constraints = {
        video: {
          width: 1920,
          height: 1280,
          facingMode: "user",
          deviceId:"c660fa6f8a45e9255ddd0850e12e04112f7f0c5c14308a19ceca3c576e4eb21a"
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      videoRef.current.srcObject = stream;
      
      await new Promise<void>((resolve) => {
        if (videoRef.current) {
          videoRef.current.onloadedmetadata = () => {
            videoRef.current?.play().then(() => {
              setIsVideoReady(true);
              resolve();
            });
          };
        }
      });
    } catch (err) {
      console.error('Camera error:', err);
      throw new Error('Failed to access camera. Please ensure camera permissions are granted.');
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (videoRef.current) {
      const stream = videoRef.current.srcObject as MediaStream;
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      videoRef.current.srcObject = null;
    }
  }, []);

  return {
    videoRef,
    isVideoReady,
    setIsVideoReady,
    startCamera,
    stopCamera
  };
}