interface ListeningAnimationProps {
  active: boolean;
}

export function ListeningAnimation({ active }: ListeningAnimationProps) {
  if (!active) return null;

  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
      <span className="absolute h-28 w-28 animate-pulse-ring rounded-full border border-accent/40" />
      <span
        className="absolute h-36 w-36 animate-pulse-ring rounded-full border border-cyan-400/30"
        style={{ animationDelay: "0.4s" }}
      />
      <span
        className="absolute h-44 w-44 animate-pulse-ring rounded-full border border-indigo-400/20"
        style={{ animationDelay: "0.8s" }}
      />
    </div>
  );
}
