const SUGGESTIONS = [
  { q: "How many earned leaves do I get in a year?", topic: "Leave" },
  { q: "How many leaves can I carry forward?", topic: "Leave" },
  { q: "What are the office timings?", topic: "Attendance" },
  { q: "Which Saturday is off?", topic: "Attendance" },
  { q: "What can I wear to office on Saturday?", topic: "Dress code" },
  { q: "What is the bike allowance per km?", topic: "Travel" },
];

export default function EmptyState({ onPick }) {
  return (
    <section className="pt-[6vh] sm:pt-[9vh]">
      <h1 className="font-serif text-[2.4rem] leading-[1.05] tracking-tight sm:text-5xl">
        Ask the HR policy.
      </h1>
      <p className="mt-4 max-w-[34em] text-[17px] leading-relaxed text-muted">
        Every answer is written from the policy document and shows the page it came from.
      </p>

      <ul className="mt-8 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-2" aria-label="Example questions">
        {SUGGESTIONS.map(({ q, topic }) => (
          <li key={q} className="bg-surface">
            <button
              type="button"
              onClick={() => onPick(q)}
              className="group flex h-full w-full flex-col gap-1 px-4 py-3.5 text-left transition-colors hover:bg-accent-soft"
            >
              <span className="text-xs font-medium text-faint group-hover:text-accent">{topic}</span>
              <span className="text-[15px] leading-snug">{q}</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}