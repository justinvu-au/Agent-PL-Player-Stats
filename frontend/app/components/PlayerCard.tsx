
import { PlayerData } from "@/app/types";

interface Props {
  player: PlayerData;
}

// Map raw stat keys to readable labels
const STAT_LABELS: Record<string, string> = {
  "General — APP":    "Appearances",
  "General — YC":     "Yellow Cards",
  "General — RC":     "Red Cards",
  "General — FC":     "Fouls Committed",
  "General — FA":     "Fouls Suffered",
  "General — OG":     "Own Goals",
  "General — SUBIN":  "Sub Appearances",
  "Offensive — G":    "Goals",
  "Offensive — A":    "Assists",
  "Offensive — SH":   "Shots",
  "Offensive — SG":   "Shots on Target",
  "Offensive — OF":   "Offsides",
  "Goal Keeping — SV":  "Saves",
  "Goal Keeping — GA":  "Goals Against",
  "Goal Keeping — SHF": "Shots Faced",
};

export default function PlayerCard({ player }: Props) {
  const displayStats = Object.entries(player.stats)
    .map(([key, value]) => ({
      label: STAT_LABELS[key] ?? key,
      value,
    }))
    .filter(({ value }) => value !== "0" && value !== "");

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm w-full">

      {/* Header */}
      <div className="bg-gradient-to-r from-purple-700 to-purple-500 px-5 py-4 flex items-center gap-4">
        {/* Country flag */}
        <img
          src={player.photo}
          alt={player.nationality}
          className="w-12 h-12 rounded-full object-cover border-2 border-white/40 bg-white/10"
          onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
        />
        <div className="flex-1 min-w-0">
          <h2 className="text-white font-bold text-lg leading-tight truncate">
            {player.name}
          </h2>
          <p className="text-purple-200 text-sm">
            {player.team} · {player.position}
          </p>
        </div>
        {player.jersey && (
          <div className="text-white/80 text-2xl font-bold">
            #{player.jersey}
          </div>
        )}
      </div>

      {/* Bio row */}
      <div className="grid grid-cols-4 divide-x divide-gray-100 border-b border-gray-100">
        {[
          { label: "Age",         value: player.age },
          { label: "Nationality", value: player.nationality },
          { label: "Height",      value: player.height },
          { label: "Weight",      value: player.weight },
        ].map(({ label, value }) => (
          <div key={label} className="px-3 py-2 text-center">
            <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
            <p className="text-sm font-semibold text-gray-800 truncate">{value ?? "—"}</p>
          </div>
        ))}
      </div>

      {/* Stats grid */}
      <div className="p-4">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
          Season Stats · {player.league}
        </p>
        <div className="grid grid-cols-3 gap-2">
          {displayStats.map(({ label, value }) => (
            <div
              key={label}
              className="bg-gray-50 rounded-xl px-3 py-2 text-center"
            >
              <p className="text-lg font-bold text-purple-700">{value}</p>
              <p className="text-xs text-gray-500 leading-tight">{label}</p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}