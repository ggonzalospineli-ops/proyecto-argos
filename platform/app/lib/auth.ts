import { createHmac, randomBytes, scryptSync, timingSafeEqual } from "crypto";
import { cookies } from "next/headers";
import { prisma } from "./db";

// Auth minima por credenciales (roles ADMIN/MEMBER/VIEWER), sin SSO ni
// librerias externas: scrypt (nativo de Node) para hashear passwords, y
// una cookie firmada con HMAC para la sesion. Ver OPEN_QUESTIONS.md — el
// MVP explicitamente no necesita mas que esto.

const SESSION_COOKIE = "argos_session";

function getSecret(): string {
  const secret = process.env.SESSION_SECRET;
  if (!secret) {
    throw new Error(
      "SESSION_SECRET no esta configurado (ver .env.example)."
    );
  }
  return secret;
}

export function hashPassword(password: string): string {
  const salt = randomBytes(16).toString("hex");
  const hash = scryptSync(password, salt, 64).toString("hex");
  return `${salt}:${hash}`;
}

export function verifyPassword(password: string, stored: string): boolean {
  const [salt, hash] = stored.split(":");
  if (!salt || !hash) return false;
  const candidate = scryptSync(password, salt, 64);
  const expected = Buffer.from(hash, "hex");
  if (candidate.length !== expected.length) return false;
  return timingSafeEqual(candidate, expected);
}

interface SessionPayload {
  userId: string;
  role: "ADMIN" | "MEMBER" | "VIEWER";
  exp: number;
}

function sign(payload: SessionPayload): string {
  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const signature = createHmac("sha256", getSecret()).update(body).digest("base64url");
  return `${body}.${signature}`;
}

function verify(token: string): SessionPayload | null {
  const [body, signature] = token.split(".");
  if (!body || !signature) return null;
  const expected = createHmac("sha256", getSecret()).update(body).digest("base64url");
  if (expected !== signature) return null;
  const payload = JSON.parse(Buffer.from(body, "base64url").toString()) as SessionPayload;
  if (payload.exp < Date.now()) return null;
  return payload;
}

export async function createSession(userId: string, role: SessionPayload["role"]) {
  const payload: SessionPayload = {
    userId,
    role,
    exp: Date.now() + 1000 * 60 * 60 * 24 * 7, // 7 dias
  };
  const token = sign(payload);
  cookies().set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
}

export function destroySession() {
  cookies().delete(SESSION_COOKIE);
}

export async function getSession(): Promise<SessionPayload | null> {
  const token = cookies().get(SESSION_COOKIE)?.value;
  if (!token) return null;
  return verify(token);
}

export async function getCurrentUser() {
  const session = await getSession();
  if (!session) return null;
  return prisma.user.findUnique({ where: { id: session.userId } });
}

export async function requireUser() {
  const user = await getCurrentUser();
  if (!user) {
    throw new Error("No autenticado.");
  }
  return user;
}
