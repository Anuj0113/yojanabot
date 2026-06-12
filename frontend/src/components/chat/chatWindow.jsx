import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import { Send, Mic, MicOff, RotateCcw } from "lucide-react";

const LANGUAGES = [
  { code: "en-IN", label: "EN", full: "English" },
  { code: "hi-IN", label: "हि", full: "Hindi" },
  { code: "gu-IN", label: "ગુ", full: "Gujarati" },
];

export default function ChatWindow({ messages, loading, onSend, onReset }) {
  const [input, setInput]         = useState("");
  const [lang, setLang]           = useState(LANGUAGES[0]);
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const bottomRef                 = useRef(null);
  const recognitionRef            = useRef(null);

  useEffect(() => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      setSupported(false);
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = lang.code;
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onstart = () => setListening(true);

    recognition.onresult = (e) => {
      const transcript = Array.from(e.results)
        .map(r => r[0].transcript)
        .join("");
      setInput(transcript);
    };

    recognition.onerror = () => setListening(false);
    recognition.onend   = () => setListening(false);

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  const handleSend = () => {
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput("");
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 rounded-2xl overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-white px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold text-lg">Y</div>
          <div>
            <div className="font-semibold text-gray-900">YojanaBot</div>
            <div className="text-xs text-green-500 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block"></span>
              Online
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Language selector */}
          <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
            {LANGUAGES.map(l => (
              <button key={l.code}
                onClick={() => setLang(l)}
                className={`text-xs px-2 py-1 rounded-md font-medium transition-colors
                  ${lang.code === l.code
                    ? "bg-white text-orange-600 shadow-sm"
                    : "text-gray-500 hover:text-gray-700"}`}>
                {l.label}
              </button>
            ))}
          </div>
          <button onClick={onReset} className="text-gray-400 hover:text-gray-600 transition-colors" title="Start over">
            <RotateCcw size={18} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-12">
            <div className="text-4xl mb-3">🇮🇳</div>
            <div className="text-sm font-medium text-gray-500">Namaste! Ask me about government schemes.</div>
            <div className="text-xs text-gray-400 mt-1">
              Speaking in <span className="text-orange-500 font-medium">{lang.full}</span> — tap 🎤 to speak
            </div>
            <div className="mt-6 flex flex-col gap-2">
              {[
                { en: "I am a farmer in Gujarat", hi: "मैं गुजरात का किसान हूँ", gu: "હું ગુજરાતનો ખેડૂત છું" },
                { en: "Muje ghar chahiye madad", hi: "मुझे घर चाहिए मदद", gu: "મને ઘર જોઈએ છે" },
                { en: "Health insurance for my family", hi: "परिवार के लिए स्वास्थ्य बीमा", gu: "પરિવાર માટે આરોગ્ય વીમો" },
              ].map((s, i) => {
                const text = lang.code === "hi-IN" ? s.hi : lang.code === "gu-IN" ? s.gu : s.en;
                return (
                  <button key={i} onClick={() => onSend(text)}
                    className="text-xs bg-white border border-orange-200 text-orange-600 rounded-full px-4 py-2 hover:bg-orange-50 transition-colors mx-auto">
                    {text}
                  </button>
                );
              })}
            </div>
          </div>
        )}
        {messages.map((msg, i) => <MessageBubble key={i} message={msg} />)}
        {loading && (
          <div className="flex justify-start mb-3">
            <div className="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center text-white text-sm font-bold mr-2 shrink-0">Y</div>
            <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm border border-gray-100">
              <div className="flex gap-1 items-center h-4">
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{animationDelay:"0ms"}}></span>
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{animationDelay:"150ms"}}></span>
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{animationDelay:"300ms"}}></span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Voice indicator */}
      {listening && (
        <div className="bg-red-50 border-t border-red-100 px-4 py-2 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-ping inline-block"></span>
          <span className="text-xs text-red-600 font-medium">Listening in {lang.full}... speak now</span>
          <button onClick={stopListening} className="ml-auto text-xs text-red-500 underline">Stop</button>
        </div>
      )}

      {/* Input */}
      <div className="bg-white px-4 py-3 border-t border-gray-100">
        <div className="flex items-center gap-2 bg-gray-50 rounded-xl px-4 py-2 border border-gray-200 focus-within:border-orange-400 transition-colors">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder={`Type in ${lang.full}...`}
            className="flex-1 bg-transparent text-sm outline-none text-gray-800 placeholder-gray-400"
            disabled={loading}
          />
          {supported && (
            <button
              onClick={listening ? stopListening : startListening}
              disabled={loading}
              className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors
                ${listening
                  ? "bg-red-500 text-white animate-pulse"
                  : "bg-gray-200 text-gray-500 hover:bg-orange-100 hover:text-orange-500"}`}>
              {listening ? <MicOff size={14} /> : <Mic size={14} />}
            </button>
          )}
          <button onClick={handleSend} disabled={!input.trim() || loading}
            className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center text-white disabled:opacity-40 hover:bg-orange-600 transition-colors">
            <Send size={14} />
          </button>
        </div>
        {!supported && (
          <div className="text-xs text-gray-400 mt-1 text-center">Voice not supported — use Chrome for voice input</div>
        )}
      </div>
    </div>
  );
}   