import React from 'react';

interface StatsCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: string;
  icon?: React.ReactNode;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  label,
  value,
  subtext,
  trend,
  icon
}) => {
  return (
    <div className="bg-[#121214] border border-[#27272a] rounded-md p-4 transition-colors hover:border-zinc-700">
      <div className="flex items-center justify-between text-zinc-400 mb-2">
        <span className="text-xs font-medium uppercase tracking-wider text-zinc-400">{label}</span>
        {icon && <span className="text-zinc-500">{icon}</span>}
      </div>
      <div className="text-2xl font-semibold tracking-tight text-white mono-num">
        {value}
      </div>
      {(subtext || trend) && (
        <div className="mt-1 flex items-center gap-2 text-xs text-zinc-500">
          {trend && <span className="font-medium text-emerald-400">{trend}</span>}
          {subtext && <span>{subtext}</span>}
        </div>
      )}
    </div>
  );
};
