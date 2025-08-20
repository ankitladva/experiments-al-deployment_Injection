import { useEffect } from "react";

export default function useEffectAsync(effect: () => void, inputs: any[]): void {
    useEffect(() => {
        effect();
    }, inputs);
}
