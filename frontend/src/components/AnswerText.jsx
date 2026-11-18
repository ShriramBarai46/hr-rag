const CITATION = /(\[\d+\])/g;

export default function AnswerText({ text, streaming, onCite, activeN, notFound }) {
  const parts = text.split(CITATION);

  return (
    <p className={`whitespace-pre-wrap break-words font-serif text-[17px] leading-[1.65] sm:text-[19px] ${notFound ? "italic text-warn" : ""}`}>
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (!match) return <span key={i}>{part}</span>;
        const n = Number(match[1]);
        return (
          <button
            key={i}
            type="button"
            onClick={() => onCite(n)}
            aria-label={`Show source ${n}`}
            className={`mark-stroke mx-px inline-flex h-[1.35em] min-w-[1.35em] animate-mark cursor-pointer items-center justify-center rounded-[3px] px-1 align-[0.3em] font-sans text-[0.72em] leading-none font-semibold text-mark-ink hover:outline-[1.5px] hover:outline-offset-1 hover:outline-mark-ink ${
              activeN === n ? "outline-[1.5px] outline-offset-1 outline-mark-ink" : ""
            }`}
          >
            {n}
          </button>
        );
      })}
      {streaming && (
        <span aria-hidden="true" className="ml-0.5 inline-block h-[1.05em] w-0.5 animate-blink bg-accent align-[-0.15em]" />
      )}
    </p>
  );
}