import { useContext, useEffect, useRef, useState } from 'react';
import { SCAN_COLORS } from '../common/constants';
import { SocketContext } from '../providers/socket-context';
import useEffectAsync from './use-effect-async';

interface UseFaceCapture {
  videoRef: React.RefObject<any>;
  isCapturing: boolean;
  currentColorIndex: number;
  scanPosition: number;
  previousColor: string;
}

export const useFaceCapture = ({
  videoRef,
  isCapturing,
  currentColorIndex,
  scanPosition,
}: UseFaceCapture) => {
  const { socket, sendMessage, sendBinaryMessage } = useContext(SocketContext);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const videoStartTimestamp = useRef<number | null>(null);
  const currentChunkStartTime = useRef<number | null>(null);
  const userId = useRef<string | null>(null);
  const lastCaptureColor = useRef<number>(-1);
  const isCompleting = useRef(false);
  const lastScanPosition = useRef<number>(0);
  const [isScanComplete, setIsScanComplete] = useState<boolean>(false);

  // Initialize video recording when capturing starts
  useEffect(() => {
    if (isCapturing) {
      handleStartCamera();
    }
    
    // Cleanup function
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    };
  }, [isCapturing]);

  const handleStartCamera = async () => {
    try {
      if (!videoRef.current) return;
  
      const stream = videoRef.current.video.captureStream();

      if (stream) {
        const recorder = new MediaRecorder(stream, {
          bitsPerSecond: 2500000,
          mimeType:undefined,
        });
        mediaRecorderRef.current = recorder;
        
        videoStartTimestamp.current = Date.now();
        currentChunkStartTime.current = videoStartTimestamp.current;
        
        recorder.ondataavailable = async (event) => {
          if (event.data.size > 0) {
            await sendChunk(event.data);
          }
        };

        sendMessage("video_start", { 
          timestamp: videoStartTimestamp.current, 
          mimeType: 'video/webm'
        });

        // Send chunks every second
        recorder.start(1000);
      }
    } catch (err) {
      console.error("Camera error:", err);
    }
  };

  const sendChunk = async (data: Blob, isFinalChunk = false) => {
    if (!socket) return;

    try {
      const chunkEndTime = Date.now();
      const buffer = await data.arrayBuffer();
      const chunk = new Uint8Array(buffer);

      sendBinaryMessage(
        "video_chunk",
        {
          startTime: currentChunkStartTime.current,
          endTime: chunkEndTime,
          fromEnd: isFinalChunk,
          mimeType: 'video/webm'
        },
        chunk
      );

      currentChunkStartTime.current = chunkEndTime;

      if (isFinalChunk) {
        await new Promise(resolve => setTimeout(resolve, 500));
        sendMessage("video_end", { 
          finalColorIndex: currentColorIndex
        });
      }
    } catch (err) {
      console.error("Error sending video chunk:", err);
    }
  };

  // Handle color changes and send color data
  useEffectAsync(async() => {
    if (!isCapturing || !socket) return;

    // Only process if scan position has actually reached the bottom
    // and we haven't processed this color index yet
    if (scanPosition >= 97 && lastScanPosition.current < 97)  {
      
      const timestamp = Date.now();
      const previousColorValue = currentColorIndex === 0 ? 'transparent' : SCAN_COLORS[currentColorIndex - 1];
      const currentColorValue = SCAN_COLORS[currentColorIndex];
      
      sendMessage("color_change", {
        previousColor: previousColorValue,
        newColor: currentColorValue,
        timestamp,
        video_start_time: videoStartTimestamp.current,
        colorIndex: currentColorIndex,
        isLastColor: currentColorIndex === SCAN_COLORS.length - 1
      });
      
      lastCaptureColor.current = currentColorIndex;
      
      if (currentColorIndex === SCAN_COLORS.length - 1) {
        isCompleting.current = true;
        console.log("Final color reached, stopping capture");
        await stopCapture();
      }
    }
    
    lastScanPosition.current = scanPosition;
  }, [isCapturing, scanPosition, currentColorIndex, socket]);

  // Stop recording and send final chunk
  const stopCapture = async () => {
    if (!mediaRecorderRef.current) return;
    
    return new Promise<void>((resolve) => {
      const handleCompletion = () => {
        setIsScanComplete(true);
        // socket?.disconnect();  // Disconnect old socket
        // reconnect();          // Create new connection
        resolve();
      };

      if (mediaRecorderRef.current!.state === 'inactive') {
        handleCompletion();
        return;
      }
      
      mediaRecorderRef.current!.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          await sendChunk(event.data, true);
        }
      };

      mediaRecorderRef.current!.onstop = handleCompletion;

      mediaRecorderRef.current!.stop();
    });
  };

  return {
    socket,
    userId: userId.current,
    stopCapture,
    isScanComplete
  };
};