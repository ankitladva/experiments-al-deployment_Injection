import React from 'react';

export function FaceOutline() {
  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div 
        className="w-[32rem] h-[38rem] border-4 absolute"
        style={{ 
          borderColor: '#22c55e', // Always green
          borderRadius: '50%/60%',
          boxShadow: '0 0 20px #22c55e'
        }}
      />
    </div>
  );
}