import { MenuIcon, PlusIcon } from "./Icons";
import StatusPill from "./StatusPill";

export default function Navbar({ health, onMenu, onNewChat, canReset }) {
  return (
    <header className="sticky top-0 z-30 h-14 border-b border-line bg-paper/85 backdrop-blur">
      <nav className="mx-auto flex h-full max-w-7xl items-center gap-3 px-3 sm:px-5" aria-label="Main">
        <button
          type="button"
          onClick={onMenu}
          className="-ml-1 rounded-lg p-2 text-muted hover:bg-surface hover:text-ink lg:hidden"
          aria-label="Open question history"
        >
          <MenuIcon />
        </button>

        <a href="/" className="flex items-center gap-2.5">
          <span aria-hidden="true" className="h-[18px] w-[14px] rounded-[2px_2px_2px_6px] bg-accent shadow-[4px_0_0_-1px_var(--mark)]" />
          <span className="font-semibold tracking-tight">HR Policy Desk</span>
        </a>

        <span className="ml-1 hidden rounded-md bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent md:inline">
          Employee handbook
        </span>

        <div className="ml-auto flex items-center gap-2">
          <StatusPill health={health} />
          <button
            type="button"
            onClick={onNewChat}
            disabled={!canReset}
            className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-surface px-2.5 py-1.5 text-sm font-medium hover:border-accent hover:text-accent disabled:pointer-events-none disabled:opacity-40 sm:px-3"
          >
            <PlusIcon width={16} height={16} />
            <span className="hidden sm:inline">New chat</span>
            <span className="sr-only sm:hidden">New chat</span>
          </button>
        </div>
      </nav>
    </header>
  );
}