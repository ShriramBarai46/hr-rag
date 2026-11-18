import { useEffect } from "react";
import { CloseIcon } from "./Icons";

const dotFor = (e) => {
  if (e.stage === "error") return "bg-danger";
  if (e.found === false) return "bg-warn";
  if (["searching", "reading", "writing"].includes(e.stage)) return "bg-accent animate-pulse";
  return "bg-accent";
};

function SidebarBody({ entries, health, onPick, onClose }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between px-4 pt-5 pb-3">
        <h2 className="text-sm font-semibold">This session</h2>
        {onClose && (
          <button type="button" onClick={onClose} className="rounded-lg p-1.5 text-muted hover:bg-paper hover:text-ink" aria-label="Close question history">
            <CloseIcon width={18} height={18} />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        {entries.length === 0 ? (
          <p className="px-2 py-2 text-sm leading-relaxed text-faint">Questions you ask will appear here, so you can jump back to any answer.</p>
        ) : (
          <ol className="space-y-0.5">
            {entries.map((e) => (
              <li key={e.id}>
                <button
                  type="button"
                  onClick={() => onPick(e.id)}
                  className="flex w-full items-start gap-2.5 rounded-lg px-2 py-2 text-left text-sm text-muted hover:bg-paper hover:text-ink"
                >
                  <span className={`mt-1.5 size-1.5 shrink-0 rounded-full ${dotFor(e)}`} />
                  <span className="line-clamp-2">{e.question}</span>
                </button>
              </li>
            ))}
          </ol>
        )}
      </div>

      <div className="m-3 rounded-xl border border-line bg-paper p-3 text-xs leading-relaxed text-muted">
        <p className="font-medium text-ink">Knowledge base</p>
        <p className="mt-1">
          {health.state === "ok"
            ? `${health.chunks} passages from the HR policy. ${health.llm_enabled ? "Answers written by OpenAI." : "OpenAI key not set, showing passages only."}`
            : health.state === "down"
              ? "The assistant is offline right now."
              : "Connecting…"}
        </p>
      </div>
    </div>
  );
}

export default function Sidebar({ entries, health, open, onClose, onPick }) {
  // Close the mobile drawer with the Escape key
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <>
      {/* Desktop: fixed column */}
      <aside className="sticky top-14 hidden h-[calc(100dvh-3.5rem)] w-64 shrink-0 border-r border-line bg-surface/60 lg:block">
        <SidebarBody entries={entries} health={health} onPick={onPick} />
      </aside>

      {/* Mobile and tablet: slide-in drawer */}
      <div className={`fixed inset-0 z-40 transition-[visibility] duration-300 lg:hidden ${open ? "visible" : "invisible"}`}>
        <div
          onClick={onClose}
          className={`absolute inset-0 bg-black/40 transition-opacity duration-300 ${open ? "opacity-100" : "opacity-0"}`}
        />
        <aside
          className={`absolute inset-y-0 left-0 w-72 max-w-[85vw] bg-surface transition-transform duration-300 ease-out ${open ? "translate-x-0 shadow-xl" : "-translate-x-full"}`}
          aria-label="Question history"
        >
          <SidebarBody entries={entries} health={health} onPick={onPick} onClose={onClose} />
        </aside>
      </div>
    </>
  );
}