import { useEffect, useState } from "react";

function getCurrentScreenDimensions(): any {
    return {
        width: window.innerWidth,
        height: window.innerHeight,
    };
}

export const useMobile = (): any => {
    const [screenSize, setScreenSize] = useState<any>(getCurrentScreenDimensions());

    const [isMobileView, setIsMobileView] = useState<boolean>(false);

    useEffect(() => {
        const updateDimension = (): any => {
            setScreenSize(getCurrentScreenDimensions());
        };

        window.addEventListener("resize", updateDimension);

        return () => {
            window.removeEventListener("resize", updateDimension);
        };
    }, []);

    useEffect(() => {
        if (screenSize.width <= 800) {
            setIsMobileView(true);
        } else {
            setIsMobileView(false);
        }
    }, [screenSize, isMobileView]);

    return { isMobileView };
};
