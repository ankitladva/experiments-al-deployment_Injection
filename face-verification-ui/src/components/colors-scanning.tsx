import {  useState, useEffect } from "react";
import { SCAN_CONFIG, SCAN_COLORS } from "../common/constants";

export interface ScanData {
    currentColorIndex: number;
    scanPosition: number;
    previousColor: string;
  }

const ColorScanning = ({ onScanUpdate }: { onScanUpdate: (data: ScanData) => void }) => {
    const [isCapturing, setIsCapturing] = useState(true);
    const [currentColorIndex, setCurrentColorIndex] = useState(0);
    const [scanPosition, setScanPosition] = useState(-SCAN_CONFIG.SCAN_HEIGHT);
    const [previousColor, setPreviousColor] = useState('transparent');
  
    useEffect(() => {
        // ... existing animation code ...
        
        // Add callback to parent when values change
        onScanUpdate({
          currentColorIndex,
          scanPosition,
          previousColor
        });
        
      }, [currentColorIndex, scanPosition, previousColor]);

    useEffect(() => {
      let animationFrame: number;
      let startTime: number;
      let currentColor = 0;
  
      const animate = (timestamp: number) => {
        if (!startTime) startTime = timestamp;
        const progress = timestamp - startTime;
        const totalDuration = SCAN_CONFIG.DURATION_PER_COLOR;
  
        if (progress < totalDuration) {
            const position = Math.min(
                100,
                (progress / totalDuration) * (100 + SCAN_CONFIG.SCAN_HEIGHT) - SCAN_CONFIG.SCAN_HEIGHT
              );
          setScanPosition(position);
          animationFrame = requestAnimationFrame(animate);
        } else {
          if (currentColor < SCAN_COLORS.length - 1) {
            setPreviousColor(SCAN_COLORS[currentColor]);
            currentColor++;
            setCurrentColorIndex(currentColor);
            startTime = timestamp;
            setScanPosition(-SCAN_CONFIG.SCAN_HEIGHT);
            animationFrame = requestAnimationFrame(animate);
          } else {
            setIsCapturing(false);
            setScanPosition(-SCAN_CONFIG.SCAN_HEIGHT);
            setCurrentColorIndex(0);
            setPreviousColor('transparent');
          }
        }
      };
  
      if (isCapturing) {
        animationFrame = requestAnimationFrame(animate);
      }
  
      return () => {
        if (animationFrame) {
          cancelAnimationFrame(animationFrame);
        }
      };
    }, [isCapturing]);
  
    return (
      isCapturing && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            opacity: 0.9,
            zIndex: 10000000,
            background: `linear-gradient(180deg, 
              ${SCAN_COLORS[currentColorIndex]} 0%, 
              ${SCAN_COLORS[currentColorIndex]} ${scanPosition}%, 
              ${previousColor} ${scanPosition}%, 
              ${previousColor} 100%)`,
            display: "flex",
            justifyContent: "center",
            alignItems: "center"
          }}
        >
        </div>
      )
    );
  };

export default ColorScanning;