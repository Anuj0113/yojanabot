import { useState } from "react";
import { ChevronDown, ChevronUp, MapPin, Globe, Phone, FileText, ListChecks } from "lucide-react";

const SCHEME_ICONS = {
  housing: "🏠", health: "🏥", farming: "🌾", education: "📚",
  women: "👩", labour: "👷", banking: "🏦", business: "💼",
  insurance: "🛡️", disability: "♿", "girl child": "👧", default: "📋",
};

function getIcon(tags = []) {
  for (const tag of tags) {
    if (SCHEME_ICONS[tag.toLowerCase()]) return SCHEME_ICONS[tag.toLowerCase()];
  }
  return SCHEME_ICONS.default;
}

export default function SchemeCard({ scheme, status }) {
  const [expanded, setExpanded] = useState(false);
  const isEligible = status === "eligible";

  return (
    <div className={`bg-white rounded-xl border shadow-sm transition-shadow hover:shadow-md
      ${isEligible ? "border-green-200" : "border-yellow-200"}`}>

      {/* Header */}
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl shrink-0">{getIcon(scheme.scheme?.tags || [])}</div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium border
                ${isEligible
                  ? "bg-green-100 text-green-700 border-green-200"
                  : "bg-yellow-100 text-yellow-700 border-yellow-200"}`}>
                {isEligible ? "✓ Eligible" : "? Possibly Eligible"}
              </span>
              <span className="text-xs text-gray-400">{Math.round(scheme.confidence * 100)}% match</span>
            </div>
            <div className="font-semibold text-gray-900 text-sm leading-snug">{scheme.scheme_name}</div>

            {scheme.matched_conditions?.slice(0, 1).map((c, i) => (
              <div key={i} className="text-xs text-green-600 mt-1 flex items-start gap-1">
                <span className="shrink-0">✓</span><span>{c}</span>
              </div>
            ))}

            {scheme.missing_info?.length > 0 && (
              <div className="text-xs text-yellow-600 mt-1">
                Need: {scheme.missing_info.join(", ")}
              </div>
            )}
          </div>

          <button onClick={() => setExpanded(!expanded)}
            className="text-gray-400 hover:text-orange-500 transition-colors shrink-0 mt-1">
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-gray-100 p-4 space-y-3">

          {/* Where to apply */}
          {scheme.where_to_apply && (
            <div className="flex items-start gap-2">
              <MapPin size={14} className="text-orange-500 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-semibold text-gray-600 mb-0.5">Where to Apply</div>
                <div className="text-xs text-gray-700">{scheme.where_to_apply}</div>
              </div>
            </div>
          )}

          {/* Online URL */}
          {scheme.online_url && (
            <div className="flex items-start gap-2">
              <Globe size={14} className="text-blue-500 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-semibold text-gray-600 mb-0.5">Apply Online</div>
                <a href={scheme.online_url} target="_blank" rel="noopener noreferrer"
                  className="text-xs text-blue-600 underline break-all">{scheme.online_url}</a>
              </div>
            </div>
          )}

          {/* Helpline */}
          {scheme.helpline && (
            <div className="flex items-start gap-2">
              <Phone size={14} className="text-green-500 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-semibold text-gray-600 mb-0.5">Helpline</div>
                <div className="text-xs text-gray-700">{scheme.helpline}</div>
              </div>
            </div>
          )}

          {/* Documents */}
          {scheme.documents_required?.length > 0 && (
            <div className="flex items-start gap-2">
              <FileText size={14} className="text-purple-500 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-semibold text-gray-600 mb-1">Documents Required</div>
                <ul className="space-y-0.5">
                  {scheme.documents_required.map((doc, i) => (
                    <li key={i} className="text-xs text-gray-700 flex items-start gap-1">
                      <span className="shrink-0 text-gray-400">•</span>{doc}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Steps */}
          {scheme.apply_steps?.length > 0 && (
            <div className="flex items-start gap-2">
              <ListChecks size={14} className="text-orange-500 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-semibold text-gray-600 mb-1">How to Apply</div>
                <ol className="space-y-1">
                  {scheme.apply_steps.map((step, i) => (
                    <li key={i} className="text-xs text-gray-700">{step}</li>
                  ))}
                </ol>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}