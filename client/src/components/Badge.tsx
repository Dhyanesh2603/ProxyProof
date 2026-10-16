import React from 'react';

interface BadgeProps {
  status: string;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ status, className = '' }) => {
  const norm = status.toUpperCase();

  let dotColor = 'bg-zinc-400';
  let textColor = 'text-zinc-300';
  let borderColor = 'border-zinc-800';
  let bgColor = 'bg-zinc-900/50';

  if (norm === 'PRESENT' || norm === 'ACTIVE' || norm === 'APPROVED' || norm === 'HEALTHY') {
    dotColor = 'bg-emerald-400';
    textColor = 'text-emerald-300';
    borderColor = 'border-emerald-950/60';
    bgColor = 'bg-emerald-950/20';
  } else if (norm === 'LATE' || norm === 'PENDING' || norm === 'WARNING') {
    dotColor = 'bg-amber-400';
    textColor = 'text-amber-300';
    borderColor = 'border-amber-950/60';
    bgColor = 'bg-amber-950/20';
  } else if (norm === 'REJECTED' || norm === 'CRITICAL' || norm === 'ENDED') {
    dotColor = 'bg-rose-400';
    textColor = 'text-rose-300';
    borderColor = 'border-rose-950/60';
    bgColor = 'bg-rose-950/20';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium border ${bgColor} ${borderColor} ${textColor} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      <span>{status}</span>
    </span>
  );
};
