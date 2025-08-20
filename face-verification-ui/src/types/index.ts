export type VerificationState = 'initial' | 'starting' | 'verifying' | 'completed';
export type VerificationColor = 'default' | 'yellow' | 'green' | 'blue' | 'red';

export const COLORS:Record<string,string> = {
  "Black": "rgb(0, 0, 0)",
  "Blue": "rgb(0, 0, 255)",
  "Yellow": "rgb(255, 255, 0)",
  "Green": "rgb(0, 255, 0)",
  "Red": "rgb(255, 0, 0)",
  "Blue2": "rgb(0, 0, 255)",
  "Cyan": "rgb(0, 255, 255)",
  "Green2": "rgb(0, 255, 0)",
  "Green3": "rgb(0, 255, 0)",
  "Green4": "rgb(0, 255, 0)"
}