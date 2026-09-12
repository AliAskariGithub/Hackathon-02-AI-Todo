import { createAuthClient } from 'better-auth/react';

export const NEON_AUTH_URL =
  process.env.NEXT_PUBLIC_NEON_AUTH_URL ||
  'https://ep-green-water-ag3obeuv.neonauth.c-2.eu-central-1.aws.neon.tech/neondb/auth';

export const authClient = createAuthClient({
  baseURL: NEON_AUTH_URL,
});

export const { signIn, signUp, signOut, useSession } = authClient;
