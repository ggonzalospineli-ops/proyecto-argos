import { NextRequest, NextResponse } from "next/server";
import { destroySession } from "@/lib/auth";

export async function POST(req: NextRequest) {
  destroySession();
  return NextResponse.redirect(new URL("/login", req.url), { status: 303 });
}
