import ReactMarkdown from "react-markdown";
import { Bot, UserRound } from "lucide-react";

function renderInline(children) {
  return (Array.isArray(children) ? children : [children]).flatMap((child, index) => {
    if (typeof child !== "string") return child;
    return child.split(/(\[[^\]]+\])/g).map((part, partIndex) =>
      /^\[[^\]]+\]$/.test(part) ? (
        <button key={`${index}-${partIndex}`} type="button" title={`Open source ${part}`} className="mx-0.5 inline-flex -translate-y-px items-center rounded-md border border-indigo-400/25 bg-indigo-500/10 px-1.5 py-0.5 align-middle text-[11px] font-medium leading-none text-indigo-300 transition hover:-translate-y-0.5 hover:border-indigo-300/60 hover:bg-indigo-500/20">
          {part.slice(1, -1)}
        </button>
      ) : part,
    );
  });
}

export function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <article className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-emerald-400/20 bg-emerald-400/10 text-emerald-300">
          <Bot size={16} strokeWidth={1.8} />
        </div>
      )}
      <div
        className={`max-w-[min(720px,85%)] text-[15px] leading-7 ${
          isUser
            ? "rounded-2xl rounded-br-md bg-emerald-300 px-5 py-3 text-[#07100f] shadow-[0_8px_30px_rgba(110,231,183,0.12)]"
            : "min-w-0 text-slate-200"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
            <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-3 last:mb-0">{renderInline(children)}</p>,
              strong: ({ children }) => <strong className="font-semibold text-indigo-200">{renderInline(children)}</strong>,
              code: ({ children }) => <code className="rounded bg-white/10 px-1.5 py-0.5 text-[13px] text-amber-200">{children}</code>,
              a: ({ children, href }) => <a className="text-emerald-300 underline decoration-emerald-300/40 underline-offset-4" href={href}>{children}</a>,
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>
      {isUser && (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/10 text-slate-300">
          <UserRound size={16} strokeWidth={1.8} />
        </div>
      )}
    </article>
  );
}
