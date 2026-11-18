const shortSection = (section) => section.split(" > ").slice(-1)[0];

function tabLabel(s) {
  const section = shortSection(s.section);
  if (!s.page) return section;
  if (section === `Page ${s.page}`) return `p.${s.page}`;
  return `${section}, p.${s.page}`;
}

export default function SourcePanel({ sources, activeN, onSelect }) {
  if (!sources.length) return null;
  const active = sources.find((s) => s.n === activeN);

  return (
    <div className="mt-4">
      <div role="tablist" aria-label="Sources" className="flex flex-wrap items-center gap-1.5">
        <span className="mr-1 text-[13px] text-faint">Sources</span>
        {sources.map((s) => {
          const selected = activeN === s.n;
          return (
            <button
              key={s.n}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => onSelect(selected ? null : s.n)}
              className={`inline-flex items-center gap-1.5 rounded-md border py-1 pr-2.5 pl-1 text-[13px] transition-colors ${
                selected ? "border-accent bg-accent-soft" : "border-line bg-surface hover:border-accent"
              }`}
            >
              <span className="grid size-5 place-items-center rounded bg-mark text-xs font-semibold text-mark-ink">{s.n}</span>
              {tabLabel(s)}
            </button>
          );
        })}
      </div>

      <div className={`grid transition-[grid-template-rows] duration-300 ${active ? "grid-rows-[1fr]" : "grid-rows-[0fr]"}`}>
        <div className="overflow-hidden">
          {active && (
            <blockquote role="tabpanel" className="mt-2.5 rounded-r-lg border border-l-[3px] border-line border-l-mark bg-surface px-4 py-3.5">
              <p className="whitespace-pre-wrap font-serif text-base leading-relaxed">{active.text}</p>
              <footer className="mt-2.5 text-xs text-faint">
                {active.source}
                {active.page ? `, page ${active.page}` : ""}. Relevance {active.rerank_score.toFixed(1)}
              </footer>
            </blockquote>
          )}
        </div>
      </div>
    </div>
  );
}