export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center text-white text-sm font-bold mr-2 shrink-0 mt-1">
          Y
        </div>
      )}
      <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed
        ${isUser
          ? "bg-orange-500 text-white rounded-tr-sm"
          : "bg-white text-gray-800 rounded-tl-sm shadow-sm border border-gray-100"
        }`}>
        {message.content}
      </div>
    </div>
  );
}