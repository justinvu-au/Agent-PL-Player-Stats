export interface PlayerStats {
  [key: string]: string;
}

export interface PlayerData {
  id: string;
  name: string;
  first_name: string;
  last_name: string;
  age: number;
  dob: string;
  nationality: string;
  height: string;
  weight: string;
  jersey: string;
  position: string;
  photo: string;
  slug: string;
  stats: PlayerStats;
  league: string;
  team: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  playerData?: PlayerData;
}

export interface ChatResponse {
  reply: string;
  player_data: PlayerData;
  player_name: string;
  api_calls_today: number;
}