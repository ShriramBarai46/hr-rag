import { useState } from "react";
import AnswerText from "./AnswerText";
import ReadingTrail from "./ReadingTrail";
import SourcePanel from "./SourcePanel";

export default function Entry({ entry }) {
  const [activeN, setActiveN] = useState(null);
  const streaming = entry.stage === "writing" || entry.stage === "reading";

  return (
    <article id={`q-${entry.id}`} className="scroll-mt-20 border-line py-7 first:pt-2 [&+&]:border-t">
      <h2 className="mb-2.5 text-[17px] leading-snug font-semibold tracking-tight">{entry.question}</h2>
      <ReadingTrail entry={entry} />

      {entry.stage === "error" ? (
        <p role="alert" className="text-danger">{entry.error}</p>
      ) : (
        (entry.text || streaming) && (
          <AnswerText
            text={entry.text}
            streaming={streaming}
            notFound={entry.found === false}
            activeN={activeN}
            onCite={(n) => setActiveN(activeN === n ? null : n)}
          />
        )
      )}

      {entry.found && entry.stage !== "searching" && (
        <SourcePanel sources={entry.sources} activeN={activeN} onSelect={setActiveN} />
      )}
    </article>
  );
}