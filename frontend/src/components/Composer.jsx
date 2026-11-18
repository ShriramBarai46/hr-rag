import { useEffect, useRef, useState } from "react";

const MAX_HEIGHT = 160;

export default function Composer({ onSend, onStop, busy }) {
  const [value, setValue] = useState("");
  const ref = useRef(null);

  // Grow the box with its content, up to MAX_HEIGHT
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_HEIGHT)}px`;
  }, [value]);

  const canSend = value.trim().length >= 2 && !busy;

  const submit = () => {
    if (!canSend) return;
    onSend(value);
    setValue("");
  };

  return (
    <div className="sticky bottom-0 bg-linear-to-t from-paper from-70% to-transparent px-3 pt-3 pb-3 sm:px-6 sm:pb-4">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          busy ? onStop() : submit();
        }}
        className="mx-auto flex max-w-2xl items-end gap-2 rounded-2xl border border-line bg-surface py-2 pr-2 pl-4 shadow-[0_8px_24px_-16px_rgba(15,18,21,0.35)] transition-colors focus-within:border-accent"
      >
        <label htmlFor="question" className="sr-only">Your question</label>
        <textarea
          id="question"
          ref={ref}
          rows={1}
          value={value}
          maxLength={500}
          placeholder="Ask about leave, timings, travel, dress code…"
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          className="max-h-40 flex-1 resize-none bg-transparent py-2 leading-normal outline-none placeholder:text-faint focus-visible:outline-none"
        />
        <button
          type="submit"
          disabled={!busy && !canSend}
          className={`shrink-0 rounded-xl px-4 py-2.5 font-semibold transition-opacity disabled:cursor-not-allowed disabled:opacity-35 sm:px-5 ${
            busy ? "bg-ink text-paper" : "bg-accent text-on-accent"
          }`}
        >
          {busy ? "Stop" : "Ask"}
        </button>
      </form>
      <p className="mx-auto mt-2 hidden max-w-2xl text-center text-xs text-faint sm:block">
        Enter to ask, Shift + Enter for a new line
      </p>
    </div>
  );
}