import { useEffect, useState, type DependencyList } from "react";

export function useAsyncData<T>(load: () => Promise<T>, fallback: T, deps: DependencyList = []) {
  const [data, setData] = useState<T>(fallback);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    load()
      .then((nextData) => {
        if (active) setData(nextData);
      })
      .catch(() => {
        if (active) setData(fallback);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, deps);

  return { data, loading };
}

export function asArray<T>(value: T[] | undefined | null): T[] {
  return Array.isArray(value) ? value : [];
}
