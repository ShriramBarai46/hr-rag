import { useCallback, useEffect, useRef, useState } from "react";
import Composer from "./components/Composer";
import EmptyState from "./components/EmptyState";
import Entry from "./components/Entry";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import { useChat } from "./hooks/useChat";
import { useHealth } from "./hooks/useHealth";

const nearBottom = () =>
  window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 200;

export default function App() {
  const health = useHealth();
  const { entries, busy, send, stop, reset } = useChat();
  const [menuOpen, setMenuOpen] = useState(false);
  const countRef = useRef(0);

  // Follow the answer as it streams, unless the user has scrolled up to read
  useEffect(() => {
    const isNewEntry = entries.length > countRef.current;
    countRef.current = entries.length;
    if (isNewEntry || nearBottom()) {
      window.scrollTo({ top: document.documentElement.scrollHeight });
    }
  }, [entries]);

  const closeMenu = useCallback(() => setMenuOpen(false), []);

  const jumpTo = (id) => {
    setMenuOpen(false);
    document.getElementById(`q-${id}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="min-h-dvh">
      <Navbar
        health={health}
        onMenu={() => setMenuOpen(true)}
        onNewChat={reset}
        canReset={entries.length > 0}
      />

      

      <div className="mx-auto flex max-w-7xl">
        <Sidebar entries={entries} health={health} open={menuOpen} onClose={closeMenu} onPick={jumpTo} />

        <div className="flex min-h-[calc(100dvh-3.5rem)] min-w-0 flex-1 flex-col">
          <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-6 sm:px-6 sm:py-8">
            {entries.length === 0 ? (
              <EmptyState onPick={send} />
            ) : (
              entries.map((entry) => <Entry key={entry.id} entry={entry} />)
            )}
          </main>
          <Composer onSend={send} onStop={stop} busy={busy} />
        </div>
      </div>
    </div>
  );
}