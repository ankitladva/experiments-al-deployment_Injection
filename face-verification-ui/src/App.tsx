import Verification from "./pages/verification";
import FaceModelsProvider from "./providers/model-context";
import SocketContextProvider from "./providers/socket-context";

 // Replace with your Flask backend URL

function App() {
  return (
    <SocketContextProvider>
      <FaceModelsProvider>
        <Verification/>
      </FaceModelsProvider>
    </SocketContextProvider>
  )
}

export default App;