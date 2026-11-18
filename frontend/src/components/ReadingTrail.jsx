const pagesOf = (sources) => {
  const seen = new Set();
  return sources
    .map((s) => s.page ?? s.section)
    .filter((p) => (seen.has(p) ? false : seen.add(p)));
};

export default function ReadingTrail({ entry }) {
  const { stage, sources, found, ms } = entry;
  if (stage === "error") return null;

  const pages = pagesOf(sources);
  const working = ["searching", "reading", "writing"].includes(stage);

  let label;
  if (stage === "searching") label = "Searching the policy";
  else if (found === false) label = "No matching passage in the policy";
  else if (stage === "stopped") label = "Stopped";
  else if (stage === "done") label = `Answered from ${sources.length} passages in ${(ms / 1000).toFixed(1)} s`;
  else if (stage === "writing") label = "Writing from";
  else label = "Reading";

  return (
    <div role="status" aria-live="polite" className="relative mb-3 flex min-h-[26px] flex-wrap items-center gap-2 text-[13px] text-muted">
      <span className={`${working ? "dots" : "text-faint"}`}>{label}</span>

      {found !== false && pages.length > 0 && stage !== "done" && (
        <span className="inline-flex flex-wrap gap-1.5">
          {pages.map((p, i) => (
            <span
              key={p}
              style={{ animationDelay: `${i * 90}ms` }}
              className="animate-chip-in rounded bg-accent-soft px-2 py-0.5 font-medium tabular-nums text-accent"
            >
              {typeof p === "number" ? `p.${p}` : p}
            </span>
          ))}
        </span>
      )}

      {stage === "searching" && (
        <span aria-hidden="true" className="absolute -bottom-1 left-0 h-0.5 w-28 overflow-hidden rounded bg-line">
          <span className="absolute inset-y-0 left-0 w-2/5 animate-scan rounded bg-accent" />
        </span>
      )}
    </div>
  );
}