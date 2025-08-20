import { Circle as RecordIcon } from 'lucide-react';
import { COLORS } from '../types';

interface StatusBarProps {
  verificationState: string;
  currentColor: string;
}

export function StatusBar({ verificationState, currentColor }: StatusBarProps) {
  // Get the appropriate background color
  const getBackgroundColor = () => {
    if (verificationState === 'completed') {
      return '#4ade80'; // A softer, more professional green
    }
    return COLORS[currentColor];
  };

  return (
    <>
      {/* Recording indicator */}
      {verificationState !== 'initial' && verificationState !== 'completed' && (
        <div className="absolute top-4 left-4 flex items-center gap-1 z-10">
          <RecordIcon className="w-4 h-4 text-red-500 animate-pulse" />
          <span className="text-xs text-red-500">REC</span>
        </div>
      )}

      {/* Status text */}
      <div 
        className="px-6 py-3 text-center transition-colors duration-300"
        style={{ backgroundColor: getBackgroundColor() }}
      >
        <p className="text-white font-medium">
          {verificationState === 'initial' ? 'Face Verification' :
           verificationState === 'starting' ? 'Click the button to start verification' :
           verificationState === 'verifying' ? 'Hold Still While We Verify' :
           'Thank you, you have been verified!'}
        </p>
      </div>
    </>
  );
}