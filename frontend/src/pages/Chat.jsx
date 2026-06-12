import ChatWindow from "../components/chat/ChatWindow";
import SchemeList from "../components/schemes/SchemeList";
import { useChat } from "../hooks/useChat";

export default function Chat() {
  const { messages, loading, profile, eligibleSchemes, partialSchemes, send, reset } = useChat();
  const hasResults = eligibleSchemes.length > 0 || partialSchemes.length > 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      {/* Top bar */}
      <div className="bg-white border-b border-gray-100 px-6 py-3 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold">Y</div>
        <div>
          <span className="font-bold text-gray-900">YojanaBot</span>
          <span className="text-gray-400 text-sm ml-2">Government Scheme Navigator</span>
        </div>
        <div className="ml-auto text-xs text-gray-400">🇮🇳 Hindi · Gujarati · English</div>
      </div>

      {/* Main layout */}
      <div className={`max-w-6xl mx-auto p-4 md:p-6 ${hasResults ? "grid grid-cols-1 md:grid-cols-2 gap-6" : "max-w-2xl"}`}>
        {/* Chat panel */}
        <div className="h-[calc(100vh-100px)]">
          <ChatWindow
            messages={messages}
            loading={loading}
            onSend={send}
            onReset={reset}
          />
        </div>

        {/* Results panel */}
        {hasResults && (
          <div className="h-[calc(100vh-100px)] overflow-y-auto">
            <SchemeList
              eligibleSchemes={eligibleSchemes}
              partialSchemes={partialSchemes}
            />
          </div>
        )}
      </div>
    </div>
  );
}