import { NextResponse } from "next/server";

const AGENT_URL = process.env.AGENT_URL ?? "http://pl-stats-agent-svc:8000";

export async function GET() {
  const response = await fetch(`${AGENT_URL}/health`);
  const data = await response.json();
  return NextResponse.json(data);
}