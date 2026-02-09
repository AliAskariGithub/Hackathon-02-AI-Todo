// Temporary: Removing Better Auth integration since we're using custom backend authentication
// This file is kept to satisfy import references but returns basic responses

export const GET = async () => {
  return new Response(JSON.stringify({ message: "Auth API placeholder" }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};

export const POST = async () => {
  return new Response(JSON.stringify({ message: "Auth API placeholder" }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};