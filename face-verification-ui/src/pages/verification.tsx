import { useState } from "react";
import { Button } from "@mui/material";
import FaceDetection from "./face-detection";
import { useMobile } from "../hooks/use-mobile";
 // Replace with your Flask backend URL

function Verification() {
    const [start, setStart] = useState(false);

    const {isMobileView} = useMobile()

    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center",marginTop:isMobileView?"0":"50px" }}>
        {!start ? (
          <Button
            variant="contained"
            color="primary"
            onClick={() => setStart(true)}
            style={{ padding: "10px 30px", fontSize: "18px",bottom:"10vh",position:"absolute" }}
          >
            Start Verification
          </Button>
        ) : (
          <FaceDetection />
        )}
      </div>
    );
}

export default Verification;