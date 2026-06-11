"use client";

// Posting-time heatmap: 7 weekdays x 24 hours of post counts.
export function Heatmap({
  matrix,
  weekdays,
}: {
  matrix: number[][];
  weekdays: string[];
}) {
  const max = Math.max(1, ...matrix.flat());
  const hours = Array.from({ length: 24 }, (_, h) => h);

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[520px]">
        <div className="flex">
          <div className="w-10" />
          <div className="grid flex-1 grid-cols-12 text-[10px] text-slate-600">
            {[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22].map((h) => (
              <span key={h}>{h}h</span>
            ))}
          </div>
        </div>
        {matrix.map((row, d) => (
          <div key={d} className="mt-1 flex items-center">
            <div className="w-10 text-[11px] text-slate-500">{weekdays[d]}</div>
            <div className="grid flex-1 grid-cols-24 gap-[3px]" style={{ gridTemplateColumns: "repeat(24, 1fr)" }}>
              {hours.map((h) => {
                const v = row[h] ?? 0;
                const intensity = v / max;
                return (
                  <div
                    key={h}
                    title={`${weekdays[d]} ${h}:00 — ${v} post(s)`}
                    className="aspect-square rounded-[3px]"
                    style={{
                      background:
                        v === 0
                          ? "rgba(255,255,255,0.04)"
                          : `rgba(124,92,255,${0.2 + intensity * 0.8})`,
                      boxShadow:
                        intensity > 0.6
                          ? "0 0 8px rgba(124,92,255,0.5)"
                          : "none",
                    }}
                  />
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
