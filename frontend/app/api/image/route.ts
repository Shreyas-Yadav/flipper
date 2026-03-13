import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function GET(req: NextRequest) {
  const filePath = req.nextUrl.searchParams.get("path");
  if (!filePath) {
    return new NextResponse("Missing path", { status: 400 });
  }

  const res = await fetch(
    `${BACKEND_URL}/image?path=${encodeURIComponent(filePath)}`
  );
  if (!res.ok) {
    return new NextResponse("Image not found", { status: res.status });
  }

  const buffer = await res.arrayBuffer();
  return new NextResponse(buffer, {
    headers: { "Content-Type": "image/jpeg" },
  });
}
