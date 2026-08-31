import { useState } from "react";
import { Activity, ArrowUp, Cable, Command, Plus, Sparkles } from "lucide-react";
import { ChatMessage } from "./components/ChatMessage";
import { ExecutionTrace } from "./components/ExecutionTrace";
import { useChat } from "./hooks/useChat";
import { AnimatePresence, motion } from "framer-motion";

const SESSION_ID = "demo-session";
const USER_ID = "demo-user";

function App() {
  const [input, setInput] = useState("");
  const {
    messages,
    isConnected,
    agentStatus,
    currentStreamingMessage,
    sendMessage,
  } = useChat(SESSION_ID, USER_ID);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (sendMessage(input)) setInput("");
  };

  return (
    <main className="min-h-screen overflow-hidden bg-zinc-900 text-zinc-100 selection:bg-indigo-500 selection:text-white">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_55%_-10%,rgba(99,102,241,0.16),transparent_34%),linear-gradient(120deg,rgba(255,255,255,0.025),transparent_40%)]" />
      <div className="relative mx-auto flex min-h-screen max-w-[1440px]">
        <aside className="hidden w-[240px] shrink-0 flex-col border-r border-white/[0.07] px-5 py-6 lg:flex">
          <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500 text-white shadow-glow">
              <Sparkles size={18} />
            </div>
            <div>
              <p className="font-display text-[15px] font-semibold tracking-tight">CogniFlow</p>
              <p className="text-[10px] uppercase tracking-[0.22em] text-zinc-500">Agent workspace</p>
            </div>
          </div>
          <button className="mt-12 flex items-center gap-2 rounded-xl border border-zinc-700/80 bg-zinc-800/70 px-3 py-2.5 text-left text-sm text-zinc-200 transition hover:border-indigo-400/50 hover:bg-indigo-500/10">
            <Plus size={16} className="text-indigo-400" /> New conversation
          </button>
          <div className="mt-auto space-y-3 text-xs text-zinc-500">
            <div className="flex items-center gap-2"><Cable size={14} /> 2 live connectors</div>
            <div className="flex items-center gap-2"><Activity size={14} /> Memory synchronized</div>
          </div>
        </aside>

        <section className="flex min-h-screen min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-zinc-800 px-5 py-5 sm:px-10">
            <div className="flex items-center gap-3 lg:hidden">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500 text-white"><Sparkles size={16} /></div>
              <span className="font-display text-sm font-semibold">CogniFlow</span>
            </div>
            <div className="hidden items-center gap-2 text-xs text-zinc-500 sm:flex"><Command size={14} /> Command center / Live session</div>
            <div className="flex items-center gap-2 text-xs">
              <span className={`h-2 w-2 rounded-full ${isConnected ? "bg-indigo-400 shadow-[0_0_10px_#818cf8]" : "bg-amber-300"}`} />
              <span className="text-zinc-400">{isConnected ? "Connected" : "Connecting"}</span>
            </div>
          </header>

          <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col px-5 pb-44 pt-12 sm:px-10 sm:pt-20">
            {messages.length === 0 && !currentStreamingMessage ? (
              <div className="my-auto pb-20">
                <p className="mb-5 text-xs font-medium uppercase tracking-[0.3em] text-indigo-400/90">Autonomous intelligence</p>
                <h1 className="max-w-2xl font-display text-4xl font-semibold leading-[1.08] tracking-tight text-white sm:text-6xl">Ask the work.<br /><span className="text-zinc-500">Get the signal.</span></h1>
                <p className="mt-6 max-w-lg text-base leading-7 text-zinc-400">CogniFlow reasons across your live tools, remembers what matters, and shows its work as it happens.</p>
                <div className="mt-10 flex flex-wrap gap-2">
                  {["Summarize Project X risks", "What is blocking Q3?", "Find my open tickets"].map((suggestion) => (
                    <button key={suggestion} onClick={() => { setInput(suggestion); }} className="rounded-full border border-zinc-700 px-4 py-2 text-xs text-zinc-400 transition hover:border-indigo-400/50 hover:text-indigo-200">{suggestion}</button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-8">
                {messages.map((message, index) => <ChatMessage key={`${message.role}-${index}`} message={message} />)}
                {currentStreamingMessage && <ChatMessage message={{ role: "assistant", content: currentStreamingMessage }} />}
              </div>
            )}
          </div>
        </section>
      </div>

      <div className="fixed inset-x-0 bottom-0 z-10 bg-gradient-to-t from-zinc-900 via-zinc-900/95 to-transparent px-5 pb-5 pt-12 sm:px-10">
        <div className="mx-auto max-w-4xl">
          <AnimatePresence initial={false}><ExecutionTrace agentStatus={agentStatus} /></AnimatePresence>
          <form onSubmit={handleSubmit} className="flex items-end gap-3 rounded-2xl border border-zinc-700/80 bg-zinc-800/75 p-2 shadow-[0_12px_60px_rgba(0,0,0,0.45)] backdrop-blur-2xl focus-within:border-indigo-400/60">
            <textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); handleSubmit(event); } }} rows={1} placeholder="Ask CogniFlow anything..." className="max-h-32 min-h-12 flex-1 resize-none bg-transparent px-3 py-3 text-sm text-white outline-none placeholder:text-zinc-500" />
            <motion.button type="submit" disabled={!isConnected || !input.trim()} aria-label="Send message" animate={isConnected && !agentStatus ? { boxShadow: ["0 0 0 rgba(99,102,241,0)", "0 0 22px rgba(99,102,241,0.42)", "0 0 0 rgba(99,102,241,0)"] } : { boxShadow: "0 0 0 rgba(99,102,241,0)" }} transition={{ duration: 2.2, repeat: Infinity }} className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-500 text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-30"><ArrowUp size={18} /></motion.button>
          </form>
          <p className="mt-3 text-center text-[10px] uppercase tracking-[0.18em] text-slate-600">Live evidence retrieval enabled</p>
        </div>
      </div>
    </main>
  );
}

export default App;
