import { createContext, useEffect, useState } from "react";
import { BACKEND_URL } from "../config/config";

export interface SocketContextType {
    socket: WebSocket | null;
    sendMessage: (event: string, data: any) => void;
    sendBinaryMessage: (event: string, data: any, binaryData: Uint8Array) => void;
}

export const SocketContext = createContext<SocketContextType>({
    socket: null,
    sendMessage: () => {},
    sendBinaryMessage: () => {},
});

const SocketContextProvider = (props: any): JSX.Element => {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [userId, setUserId] = useState<string | null>(null);

    useEffect(() => {
        if (!socket?.OPEN) {
            // Use ws/wss based on current page protocol
            const wsUrl = BACKEND_URL.replace(/^http/, 'ws') + '/ws';
    
            console.log("Attempting to connect to WebSocket URL:", wsUrl);
    
            const socketConnection = new WebSocket(wsUrl);
            
            socketConnection.onopen = () => {
                console.log("WebSocket connection established");
            };
    
            socketConnection.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    if (message.event === "user_id") {
                        setUserId(message.data.user_id);
                    }
                } catch (error) {
                    console.error("Error parsing WebSocket message:", error);
                }
            };
    
            socketConnection.onerror = (error) => {
                console.error("WebSocket error:", error);
            };
    
            socketConnection.onclose = () => {
                console.log("WebSocket connection closed");
            };
    
            setSocket(socketConnection);
        }
    }, []);
    

    const sendMessage = (event: string, data: any) => {
        if (socket?.readyState === WebSocket.OPEN) {
            const message = {
                event,
                data: {
                    ...data,
                    user_id: userId
                }
            };
            socket.send(JSON.stringify(message));
        }
    };

    const sendBinaryMessage = (event: string, data: any, binaryData: Uint8Array) => {
        if (socket?.readyState === WebSocket.OPEN) {
            // First send the metadata
            sendMessage(event, data);
            
            // Then send the binary data
            socket.send(binaryData);
        }
    };

    return (
        <SocketContext.Provider
            value={{
                socket,
                sendMessage,
                sendBinaryMessage
            }}
        >
            {props.children}
        </SocketContext.Provider>
    );
};

export default SocketContextProvider;
