import { useCallback, useRef, useState } from "react";
import { askStream } from "../api/client";

const newId = () => crypto.randomUUID();

export function useChat() {
  const [entries, setEntries] = useState([]);
  const [busy, setBusy] = useState(false);
  const controllerRef = useRef(null);

  const update = (id, change) =>
    setEntries((prev) => prev.map((e) => (e.id === id ? { ...e, ...change(e) } : e)));

  const send = useCallback(
    async (text) => {
      const question = text.trim();
      if (question.length < 2 || busy) return;

      const id = newId();
      const startedAt = performance.now();
      setEntries((prev) => [
        ...prev,
        { id, question, stage: "searching", sources: [], found: null, text: "", error: null, ms: null },
      ]);
      setBusy(true);

      const controller = new AbortController();
      controllerRef.current = controller;

      try {
        await askStream(question, {
          signal: controller.signal,
          onEvent: (event) => {
            if (event.type === "status") update(id, () => ({ stage: event.stage }));
            if (event.type === "sources")
              update(id, () => ({ sources: event.sources, found: event.found, stage: "reading" }));
            if (event.type === "token") update(id, (e) => ({ text: e.text + event.text }));
            if (event.type === "done")
              update(id, () => ({ stage: "done", ms: performance.now() - startedAt }));
            if (event.type === "error") update(id, () => ({ stage: "error", error: event.message }));
          },
        });
      } catch (err) {
        if (err.name === "AbortError") {
          update(id, () => ({ stage: "stopped", ms: performance.now() - startedAt }));
        } else {
          update(id, () => ({ stage: "error", error: `Couldn't reach the HR assistant: ${err.message}` }));
        }
      } finally {
        controllerRef.current = null;
        setBusy(false);
      }
    },
    [busy]
  );

  const stop = useCallback(() => controllerRef.current?.abort(), []);

  // Start over: stop any answer in progress and clear the page
  const reset = useCallback(() => {
    controllerRef.current?.abort();
    setEntries([]);
  }, []);

  return { entries, busy, send, stop, reset };
}