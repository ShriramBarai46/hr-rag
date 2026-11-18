export default function StatusPill({ health }) {
  const live = health.state === "ok";
  const down = health.state === "down";

  const text = health.state === "loading"
    ? "Connecting"
    : down
      ? "Offline"
      : health.llm_enabled
        ? `Live, ${health.chunks} passages`
        : "Retrieval only";

  return (
    <span
      title={live ? `${health.chunks} passages indexed` : undefined}
      className={`inline-flex items-center gap-2 rounded-full border bg-surface px-3 py-1 text-xs sm:text-[13px] ${
        down ? "border-danger/40 text-danger" : live ? "border-line text-ink" : "border-line text-muted"
      }`}
    >
      <span className="relative flex size-2">
        {live && <span className="absolute inline-flex size-full animate-ping rounded-full bg-accent opacity-50" />}
        <span className={`relative inline-flex size-2 rounded-full ${down ? "bg-danger" : live ? "bg-accent" : "bg-faint"}`} />
      </span>
      <span className="hidden sm:inline">{text}</span>
      <span className="sm:hidden">{down ? "Offline" : live ? "Live" : "…"}</span>
    </span>
  );
}