import SchemeCard from "./SchemeCard";

export default function SchemeList({ eligibleSchemes, partialSchemes }) {
  const hasResults = eligibleSchemes.length > 0 || partialSchemes.length > 0;

  if (!hasResults) return null;

  return (
    <div className="flex flex-col gap-4">
      <div className="bg-orange-50 border border-orange-100 rounded-xl px-4 py-3">
        <div className="font-semibold text-orange-800 text-sm">
          Found {eligibleSchemes.length + partialSchemes.length} schemes for you
        </div>
        <div className="text-xs text-orange-600 mt-0.5">
          {eligibleSchemes.length} eligible · {partialSchemes.length} need more info
        </div>
      </div>

      {eligibleSchemes.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 px-1">
            Eligible Now
          </div>
          <div className="flex flex-col gap-2">
            {eligibleSchemes.map(s => (
              <SchemeCard key={s.scheme_id} scheme={s} status="eligible" />
            ))}
          </div>
        </div>
      )}

      {partialSchemes.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 px-1">
            Possibly Eligible
          </div>
          <div className="flex flex-col gap-2">
            {partialSchemes.map(s => (
              <SchemeCard key={s.scheme_id} scheme={s} status="partial" />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}