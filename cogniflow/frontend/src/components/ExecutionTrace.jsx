import { useEffect, useState } from "react";
import { Check, LoaderCircle, ScanSearch, Sparkles } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

function statusLabel(status) {
  return status.replace(/\.\.\.$/, "").replace(/ started$/i, "");
}

export function ExecutionTrace({ agentStatus }) {
  const [completedSteps, setCompletedSteps] = useState([]);

  useEffect(() => {
    if (!agentStatus) return;
    const label = statusLabel(agentStatus);
    setCompletedSteps((steps) => {
      if (steps.length === 0 || steps[steps.length - 1] === label) return steps;
      return [...steps, steps[steps.length - 1]];
    });
  }, [agentStatus]);

  useEffect(() => {
    if (!agentStatus) setCompletedSteps([]);
  }, [agentStatus]);

  if (!agentStatus) return null;
  const currentLabel = statusLabel(agentStatus);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8, height: 0 }}
      animate={{ opacity: 1, y: 0, height: "auto" }}
      exit={{ opacity: 0, y: 8, height: 0 }}
      className="mb-4 overflow-hidden rounded-xl border border-indigo-400/20 bg-zinc-900/80 px-4 py-3 shadow-[0_0_35px_rgba(99,102,241,0.08)] backdrop-blur-xl"
    >
      <div className="mb-2 flex items-center justify-between text-[10px] font-medium uppercase tracking-[0.2em] text-zinc-500">
        <span className="flex items-center gap-2"><Sparkles size={12} className="text-indigo-400" /> Execution trace</span>
        <span className="text-indigo-300/70">Live</span>
      </div>
      <div className="space-y-2">
        <AnimatePresence initial={false}>
          {completedSteps.slice(0, -1).map((step, index) => (
            <motion.div key={`${step}-${index}`} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-2 text-xs text-zinc-500">
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-zinc-800 text-emerald-400"><Check size={10} /></span>
              <span>{step}</span>
            </motion.div>
          ))}
        </AnimatePresence>
        <motion.div layout className="flex items-center gap-2 text-xs font-medium text-zinc-200">
          <span className="relative flex h-5 w-5 items-center justify-center rounded-full bg-indigo-500/15 text-indigo-300">
            <span className="absolute inset-0 animate-ping rounded-full bg-indigo-400/20" />
            {currentLabel.toLowerCase().includes("query") ? <ScanSearch size={12} /> : <LoaderCircle size={12} className="animate-spin" />}
          </span>
          <span>{currentLabel}</span>
        </motion.div>
      </div>
    </motion.div>
  );
}
