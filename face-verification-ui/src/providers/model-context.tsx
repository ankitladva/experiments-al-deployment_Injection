import React, { createContext, useState } from "react";
import useEffectAsync from "../hooks/use-effect-async";
import { FaceDetector, FilesetResolver } from "@mediapipe/tasks-vision";

export interface FaceModelsContextType {
    faceDetector: any;
    setFaceDetector: React.Dispatch<any>;
}
export const FaceModelsContext = createContext<FaceModelsContextType>({
    faceDetector: null,
    setFaceDetector: () => {},
});

const FaceModelsProvider = (props: any): JSX.Element => {
    const [faceDetector, setFaceDetector] = useState<any>(null);

    useEffectAsync(async()=>{
        const loadModels = async (): Promise<void> => {
            try {
                const vision = await FilesetResolver.forVisionTasks("/model");
                const faceDetectorInstance = await FaceDetector.createFromOptions(vision, {
                    baseOptions: {
                        modelAssetPath: "/model/blaze_face_short_range.tflite",
                        delegate: "GPU" // Prefer GPU delegation when available
                    },
                    runningMode: "IMAGE"
                });
                setFaceDetector(faceDetectorInstance);
            } catch (error) {
                console.error("Error loading face detection model:", error);
            }
        };
        await loadModels();
    },[])

    return (
        <FaceModelsContext.Provider
            value={{
                setFaceDetector,
                faceDetector,
            }}
        >
            {props.children}
        </FaceModelsContext.Provider>
    );
};

export default FaceModelsProvider;
