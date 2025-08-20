import { Square, Triangle, Star, Circle } from 'lucide-react';
import { COLORS } from '../types';

interface ShapeIndicatorsProps {
  currentColor: string;
}

export function ShapeIndicators({ currentColor }: ShapeIndicatorsProps) {
  return (
    <div className="p-4 flex justify-center gap-8">
      {[Square, Triangle, Star, Circle].map((Icon, index) => (
        <Icon
          key={index}
          className="w-6 h-6 transition-colors duration-300"
          style={{ color: COLORS[currentColor] }}
        />
      ))}
    </div>
  );
}