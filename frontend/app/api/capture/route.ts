import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const camera = req.nextUrl.searchParams.get("camera");
  const url = camera
    ? `${BACKEND_URL}/capture?camera=${camera}`
    : `${BACKEND_URL}/capture`;

  const res = await fetch(url, { method: "POST" });
  if (!res.ok) {
    return new NextResponse(await res.text(), { status: res.status });
  }
  return NextResponse.json(await res.json());
}
