import { NextRequest, NextResponse } from "next/server";

const AGENT_URL = process.env.AGENT_URL ?? "http://pl-stats-agent-svc:8000";

export async function POST(req: NextRequest) {
  const body = await req.json();

  const response = await fetch(`${AGENT_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json();

  if (!response.ok) {
    return NextResponse.json(data, { status: response.status });
  }

  return NextResponse.json(data);
}