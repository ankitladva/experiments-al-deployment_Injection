export const SCAN_CONFIG = {
    DURATION_PER_COLOR: 700, // milliseconds for each color scan
    TRANSITION_SPEED: 1,   // milliseconds for color transition
    SCAN_HEIGHT: 5,         // height of scanning line in pixels
};

// export const SCAN_COLORS = [
//     { hex: "#00000000", name: "transparent" }, // Actual face (middle)
//     { hex: "#000000", name: "black" },
//     { hex: "#0000FF", name: "blue" },
//     { hex: "#FFFF00", name: "yellow" },
//     { hex: "#00FF00", name: "green" },
//     { hex: "#00000000", name: "transparent" }, // Actual face (middle)
//     { hex: "#FF0000", name: "red" },
//     { hex: "#0000FF", name: "blue" },
//     { hex: "#00FFFF", name: "cyan" },
//     { hex: "#00FF00", name: "green" },
//     { hex: "#00000000", name: "transparent" }, // Actual face (end)
// ];

export const SCAN_COLORS = [
    "#00000000", // transparent (Actual face - middle)
    "#000000",   // black
    "#0000FF",   // blue
    "#FFFF00",   // yellow
    "#00FF00",   // green
    "#00000000", // transparent (Actual face - middle)
    "#FF0000",   // red
    "#0000FF",   // blue
    "#00FFFF",   // cyan
    "#00FF00",   // green
    "#00000000", // transparent (Actual face - end)
];
