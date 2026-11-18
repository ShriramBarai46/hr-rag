import { useEffect, useState } from "react";
import { getHealth } from "../api/client";

const CHECK_EVERY_MS = 30000;

export function useHealth() {
  const [health, setHealth] = useState({ state: "loading" });

  useEffect(() => {
    let alive = true;
    const check = () =>
      getHealth()
        .then((data) => alive && setHealth({ state: "ok", ...data }))
        .catch(() => alive && setHealth({ state: "down" }));

    check();
    const timer = setInterval(check, CHECK_EVERY_MS);
    window.addEventListener("focus", check);
    return () => {
      alive = false;
      clearInterval(timer);
      window.removeEventListener("focus", check);
    };
  }, []);

  return health;
}