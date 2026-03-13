import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(_req: NextRequest) {
  const res = await fetch(`${BACKEND_URL}/flip`, { method: "POST" });
  if (!res.ok) {
    return new NextResponse(await res.text(), { status: res.status });
  }
  return NextResponse.json(await res.json());
}
