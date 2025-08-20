import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { get } from "lodash";
import { FaceModelsContext } from "../providers/model-context";
import { useMobile } from "./use-mobile";

// interface UseFaceDetectionReturn {
//     isOverlay: boolean;
//     isFaceInsideBoundary: boolean;
//     canvasRef: any;
//     showOverlayOnly?: boolean;
// }

export const randomIntFromInterval = (min: number, max: number): number => {
    return Math.random() * (max - min) + min;
};

// Threshold constants for face detection and positioning
export const FACE_DETECTION_THRESHOLDS = {
    // Initial position (farther)
    INITIAL_MIN_FACE_SIZE_RATIO: 0.35,
    INITIAL_MAX_FACE_SIZE_RATIO: 0.45,
    
    // Final position (closer)
    FINAL_MIN_FACE_SIZE_RATIO: 0.50,
    FINAL_MAX_FACE_SIZE_RATIO: 0.60,
    
    ALIGNMENT_THRESHOLD: 0.3,
    BORDER_PROXIMITY_THRESHOLD: 15,
    FACE_CHECK_INTERVAL: 500,
    
    DIRECTION: {
        VERTICAL_THRESHOLD: 0.15,
        HORIZONTAL_THRESHOLD: 0.15,
    },
};


interface FacePositionStatus {
    isFaceFar: boolean;
    isFaceAlignedWithOverlay: boolean;
    isFaceTooClose: boolean;
    isFaceNearBorder: boolean;
    isIdealStartPosition: boolean;
    faceDirection: {
        isLookingLeft: boolean;
        isLookingRight: boolean;
    };
}

export const useFaceDetection = (props: any): any => {
    const { isMobileView } = useMobile();
    const DEFAULT_SHAPE_WIDTH = !isMobileView?220:220;

    const DEFAULT_SHAPE_HEIGHT = !isMobileView?280:280;
    const DEFAULT_OVERLAY_SHAPE = "oval";
    
    const { overlay, videoPlayerRef } = props;

    const { faceDetector } = useContext(FaceModelsContext);

    const canvasRef = useRef<any>();
    const [isOverlay, setIsOverlay] = useState<boolean>(false);
    const [isFaceInsideBoundary, setIsFaceInsideBoundary] = useState<any>(false);
    const [boundaryScale, setBoundaryScale] = useState<number>(1);
    const [facePositionStatus, setFacePositionStatus] = useState<FacePositionStatus>({
        isFaceFar: false,
        isFaceAlignedWithOverlay: false,
        isFaceTooClose: false,
        isFaceNearBorder: false,
        isIdealStartPosition:false,
        faceDirection: {
            isLookingLeft: false,
            isLookingRight: false
        }
    });
    const [faceBox, setFaceBox] = useState<FaceBox | null>(null);
    

    const overlayConfig = get(overlay, isMobileView ? "mobile" : "desktop", overlay);
    const showOverlayOnly = get(overlayConfig, "showOverlayOnly",false);
    const dynamicBorderColor = get(overlayConfig, "dynamicBorderColor","green");
    const dynamicSize = get(overlayConfig, "shape.dynamicSize", false);
    const backgroundColor = "rgba(255,255,255,1)";

    useEffect(() => {
        const checkVideoReady = () => {
            if (videoPlayerRef.current?.video) {
                if (videoPlayerRef.current.video.readyState === 4) {
                    setIsOverlay(true);
                }else{
                    setIsOverlay(false);
                }
            }else{
                setIsOverlay(false);
            }
        };
    
        // Check initially
        checkVideoReady();
    
        // Add event listener for loadeddata
        const videoElement = videoPlayerRef.current?.video;
        if (videoElement) {
            videoElement.addEventListener('loadeddata', checkVideoReady);
            videoElement.addEventListener('loadedmetadata', checkVideoReady);
        }
    
        return () => {
            if (videoElement) {
                videoElement.removeEventListener('loadeddata', checkVideoReady);
                videoElement.removeEventListener('loadedmetadata', checkVideoReady);
            }
        };
    }, [videoPlayerRef.current]);

    useEffect(() => {
        if (isOverlay && canvasRef.current) {
            canvasRef.current.style.width = "100%";
            canvasRef.current.style.height = "100%";
            canvasRef.current.width = canvasRef.current.offsetWidth;
            canvasRef.current.height = canvasRef.current.offsetHeight;
        }
    }, [canvasRef, isOverlay, isMobileView]);

    interface Offset {
        xoffset: number;
        yoffset: number;
    }

    interface GetOffsetParam {
        canvas: any;
        width?: number;
        height?: number;
    }

    const getRectangleOffset = ({ canvas, width, height }: GetOffsetParam): Offset => {
        const xoffset = canvas.width / 2 - (width as number) / 2;
        const yoffset = canvas.height / 2 - (height as number) / 2;
        return { xoffset, yoffset };
    };

    const getOvalOffset = ({ canvas }: GetOffsetParam): Offset => {
        const xoffset = canvas.width / 2;
        const yoffset = canvas.height / 2;
        return { xoffset, yoffset };
    };

    const getOffset = ({ canvas, width, height }: GetOffsetParam): Offset => {
        const shapeOffsetFactory = {
            oval: getOvalOffset,
            rectangle: getRectangleOffset,
        };
        const shape = get(overlayConfig, "shape.type", DEFAULT_OVERLAY_SHAPE);
        return get(shapeOffsetFactory, shape)?.({ canvas, width, height });
    };

    const drawCanvasOval = ({ canvas, ctx }: any): void => {
        const { xoffset, yoffset } = getOffset({ canvas });
        const { width, height } = getShapeSize();
        const widthRadius = width / 2;
        const heightRadius = height / 2;
        ctx.ellipse(xoffset, yoffset, widthRadius, heightRadius, 0, 0, 2 * Math.PI);
    };

    const drawRectangle = ({ canvas, ctx }: any): void => {
        const { width, height } = getShapeSize();
        const { xoffset, yoffset } = getOffset({ canvas, width, height });
        ctx.rect(xoffset, yoffset, width, height);
    };

    const drawShape = ({ ctx, canvas }: any): void => {
        const shapeFactory = {
            oval: drawCanvasOval,
            rectangle: drawRectangle,
        };
        const shape = get(overlayConfig, "shape.type", DEFAULT_OVERLAY_SHAPE);
        get(shapeFactory, shape)?.({ ctx, canvas });
    };

    const drawOverlay = useCallback(() => {
        const canvas = canvasRef.current;
        const ctx = canvasRef.current?.getContext("2d", { willReadFrequently: true });
        if (canvas && ctx) {
            // Enable anti-aliasing (for images, but affects general rendering)
            ctx.imageSmoothingEnabled = true; // For shapes/strokes, this helps indirectly
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw a translucent background to shadow everything
            ctx.fillStyle = backgroundColor; // Semi-transparent black
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Define the overlay shape area as a clipping region
            ctx.save(); // Save the current state
            ctx.beginPath();
            drawShape({ ctx, canvas });
            ctx.clip(); // Use the shape as a clipping region

            // Clear the overlay shape area by drawing a transparent rectangle over it
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.restore(); // Restore the state to remove the clipping region

            // Draw the border of the shape
            ctx.beginPath();
            drawShape({ ctx, canvas });
            if (dynamicBorderColor) {
                ctx.strokeStyle = (isFaceInsideBoundary||facePositionStatus?.isFaceAlignedWithOverlay) ? "green" : "red";
            } else {
                ctx.strokeStyle = get(overlayConfig, "borderColor", "white");
            }
            ctx.lineWidth = get(overlayConfig, "borderWidth", 3);
            // Ensure smooth strokes
            ctx.lineJoin = 'round'; // Round line joins for smoother corners
            ctx.lineCap = 'round';  // Round line caps for smoother ends
            ctx.stroke();
        }
    }, [boundaryScale, isMobileView, isFaceInsideBoundary,facePositionStatus]);

    const getOvalSize = (): ShapeSizeReturnType => {
        let width = get(overlayConfig, "shape.widthRadius");
        let height = get(overlayConfig, "shape.heightRadius");
        if (!width) {
            width = DEFAULT_SHAPE_WIDTH / 2;
        }
        if (!height) {
            height = DEFAULT_SHAPE_HEIGHT / 2;
        }
        width *= 2;
        height *= 2;
        return { width, height };
    };

    const getRectangleSize = (): ShapeSizeReturnType => {
        const width = get(overlayConfig, "shape.width", DEFAULT_SHAPE_WIDTH);
        const height = get(overlayConfig, "shape.height", DEFAULT_SHAPE_HEIGHT);
        return { width, height };
    };

    interface ShapeSizeReturnType {
        width: number;
        height: number;
    }

    const getShapeSize = (): ShapeSizeReturnType => {
        const shapeSizeFactory = {
            oval: getOvalSize,
            rectangle: getRectangleSize,
        };
        const shape = get(overlayConfig, "shape.type", DEFAULT_OVERLAY_SHAPE);
        const shapeFunction = get(shapeSizeFactory, shape);
        if (!shapeFunction) {
            throw new Error(`Invalid shape type: ${shape}`);
        }
        let { width, height } = shapeFunction();
        width *= boundaryScale;
        height *= boundaryScale;
        return { width, height };
    };

    const getOvalShapeCoordinates = (): ShapeCoordinates => {
        const { width, height } = getShapeSize();
        const { xoffset, yoffset } = getOffset({
            canvas: canvasRef.current,
            width,
            height,
        });
        const shapeX = xoffset - width / 2;
        const shapeY = yoffset - height / 2;
        return { shapeX, shapeY };
    };

    const getRectangleShapeCoordinates = (): ShapeCoordinates => {
        const { width, height } = getShapeSize();
        const { xoffset, yoffset } = getOffset({
            canvas: canvasRef.current,
            width,
            height,
        });
        return { shapeX: xoffset, shapeY: yoffset };
    };

    interface ShapeCoordinates {
        shapeX: number;
        shapeY: number;
    }

    const getShapeCoordinates = (): ShapeCoordinates => {
        const shapeCoordinateFactory = {
            oval: getOvalShapeCoordinates,
            rectangle: getRectangleShapeCoordinates,
        };
        const shape = get(overlayConfig, "shape.type", DEFAULT_OVERLAY_SHAPE);
        return get(shapeCoordinateFactory, shape)?.();
    };

  

    const checkFaceDistanceAndAlignment = useCallback((faceBox: FaceBox): FacePositionStatus => {
        const { width: shapeWidth, height: shapeHeight } = getShapeSize();
        const { shapeX, shapeY } = getShapeCoordinates();
        const canvas = canvasRef.current;
    
        // Adjust thresholds based on aspect ratio
        const aspectRatio = canvas.width / canvas.height;
        const aspectRatioAdjustment = Math.min(aspectRatio, 1/aspectRatio);
        
        // Calculate adjusted face size ratio
        const faceSize = Math.max(faceBox.width, faceBox.height);
        const overlaySize = Math.max(shapeWidth, shapeHeight);
        const faceSizeRatio = (faceSize / overlaySize) * aspectRatioAdjustment;
    
        // Adjust thresholds dynamically
        const adjustedInitialMin = FACE_DETECTION_THRESHOLDS.INITIAL_MIN_FACE_SIZE_RATIO * aspectRatioAdjustment;
        const adjustedInitialMax = FACE_DETECTION_THRESHOLDS.INITIAL_MAX_FACE_SIZE_RATIO * aspectRatioAdjustment;
        const adjustedFinalMax = FACE_DETECTION_THRESHOLDS.FINAL_MAX_FACE_SIZE_RATIO * aspectRatioAdjustment;
    
        const isIdealStartPosition = 
            faceSizeRatio >= adjustedInitialMin && 
            faceSizeRatio <= adjustedInitialMax;
    
        const isFaceFar = faceSizeRatio < adjustedInitialMin;
        const isFaceTooClose = faceSizeRatio > adjustedFinalMax;
    
        // Calculate face center
        const faceCenterX = faceBox.originX + faceBox.width / 2;
        const faceCenterY = faceBox.originY + faceBox.height / 2;
        
        // Calculate shape center
        const shapeCenterX = shapeX + shapeWidth / 2;
        const shapeCenterY = shapeY + shapeHeight / 2;
        
        // Calculate alignment - how centered the face is within the shape
        const xAlignmentDiff = Math.abs(faceCenterX - shapeCenterX) / (shapeWidth / 2);
        const yAlignmentDiff = Math.abs(faceCenterY - shapeCenterY) / (shapeHeight / 2);
        
        // Check directional alignment
        const {  HORIZONTAL_THRESHOLD } = FACE_DETECTION_THRESHOLDS.DIRECTION;
        const faceDirection = {
            isLookingLeft: xAlignmentDiff < -HORIZONTAL_THRESHOLD,
            isLookingRight: xAlignmentDiff > HORIZONTAL_THRESHOLD
        };
    
        // Face is aligned if it's within the threshold from center
        const isFaceAlignedWithOverlay = 
            Math.abs(xAlignmentDiff) < FACE_DETECTION_THRESHOLDS.ALIGNMENT_THRESHOLD && 
            Math.abs(yAlignmentDiff) < FACE_DETECTION_THRESHOLDS.ALIGNMENT_THRESHOLD;
    
        
        // Check if face is near the border
        const borderThreshold = FACE_DETECTION_THRESHOLDS.BORDER_PROXIMITY_THRESHOLD;
        const leftDistance = Math.abs(faceBox.originX - shapeX);
        const rightDistance = Math.abs((faceBox.originX + faceBox.width) - (shapeX + shapeWidth));
        const topDistance = Math.abs(faceBox.originY - shapeY);
        const bottomDistance = Math.abs((faceBox.originY + faceBox.height) - (shapeY + shapeHeight));
        
        const isFaceNearBorder = 
            leftDistance < borderThreshold || 
            rightDistance < borderThreshold || 
            topDistance < borderThreshold || 
            bottomDistance < borderThreshold;
        
        return {
            isFaceFar,
            isFaceAlignedWithOverlay,
            isFaceTooClose,
            isFaceNearBorder,
            faceDirection,
            isIdealStartPosition
        };
    }, [getShapeSize, getShapeCoordinates]);

    interface FaceBox {
        originX: number;
        originY: number;
        width: number;
        height: number;
    }

    const checkFacePosition = useCallback(async () => {
        if (faceDetector && videoPlayerRef.current && videoPlayerRef.current.video.readyState === 4) {
            const canvas = canvasRef.current;
            // Add check for canvas existence
            if (!canvas) return;
            const imageSrc = videoPlayerRef.current.getScreenshot();
            const image = new Image();
            image.src = imageSrc;
            image.onload = async () => {
                const imgCanvas = document.createElement("canvas");
                imgCanvas.width = canvas.width;
                imgCanvas.height = canvas.height;
                const ctx: any = imgCanvas.getContext("2d", { willReadFrequently: true });
                ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

                const imageBitmap = await createImageBitmap(imgCanvas);

                let detections = await faceDetector.detect(imageBitmap, performance.now());
                detections = detections?.detections;
                if (detections.length > 0) {
                    const detection = detections[0];
                    const faceBox: FaceBox = detection.boundingBox;
                    setFaceBox(faceBox)
                    const { width, height } = getShapeSize();
                    const { shapeX, shapeY } = getShapeCoordinates();
                    const faceX: number = faceBox.originX;
                    const faceY: number = faceBox.originY;

                    const isFaceInsideBoundary =
                        faceX > shapeX &&
                        faceY > shapeY &&
                        faceX + faceBox.width < shapeX + width &&
                        faceY + faceBox.height < shapeY + height;
                    setIsFaceInsideBoundary(isFaceInsideBoundary);
                    
                    // Calculate additional face position metrics
                    const facePositionStatus = checkFaceDistanceAndAlignment(faceBox);
                    setFacePositionStatus(facePositionStatus);
                } else {
                    setFaceBox(null); 
                    setIsFaceInsideBoundary(false);
                    setFacePositionStatus({
                        isFaceFar: false,
                        isFaceAlignedWithOverlay: false,
                        isFaceTooClose: false,
                        isFaceNearBorder: false,
                        isIdealStartPosition:false,
                        faceDirection:{
                            isLookingLeft: false,
                            isLookingRight: false
                        }
                    });
                }
            };
        }
    }, [boundaryScale, faceDetector, isMobileView, checkFaceDistanceAndAlignment]);

    useEffect(() => {
        let intervalId: any;
        if (isOverlay) {
            drawOverlay();
            if (!showOverlayOnly) {
                intervalId = setInterval(async () => {
                    await checkFacePosition();
                }, FACE_DETECTION_THRESHOLDS.FACE_CHECK_INTERVAL);
            }
        }
        return () => {
            clearInterval(intervalId);
        };
    }, [checkFacePosition, boundaryScale, isOverlay, isMobileView, isFaceInsideBoundary,facePositionStatus]);

    useEffect(() => {
        if (!showOverlayOnly && dynamicSize) {
            setBoundaryScale(randomIntFromInterval(0.5, 1));
        }
    }, [isOverlay]);

    // useEffect(() => {
    //     setIsOverlay(Boolean(!isCaptured && overlayConfig?.isApplicable));
    // }, [isCaptured, overlayConfig, isMobileView]);

    return {
        isOverlay,
        isFaceInsideBoundary,
        canvasRef,
        showOverlayOnly,
        getShapeSize,
        getShapeCoordinates,
        faceBox, // Add this
        ...facePositionStatus
    };
};
