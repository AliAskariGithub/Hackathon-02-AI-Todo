import { NextRequest, NextResponse } from 'next/server';

// Define protected routes
const protectedRoutes = ['/pages'];

export default function middleware(request: NextRequest) {
  // Check if the current path is a protected route
  const isProtectedRoute = protectedRoutes.some(route =>
    request.nextUrl.pathname.startsWith(route)
  );

  if (isProtectedRoute) {
    // For protected page routes, check for authentication token in cookies
    // Look for Better Auth specific cookie names (common patterns)
    const sessionToken = request.cookies.get('better-auth.session_token')?.value ||
                        request.cookies.get('better-auth.csrf')?.value ||
                        request.cookies.get('better-auth.client_id')?.value ||
                        request.cookies.get('better-auth.session')?.value ||  // Better Auth session cookie
                        request.cookies.get('auth-token')?.value; // Our custom auth token

    const headerToken = request.headers.get('authorization')?.replace('Bearer ', '');

    // If no token is found in cookies or headers, redirect to login
    if (!sessionToken && !headerToken) {
      const url = request.nextUrl.clone();
      url.pathname = '/login'; // Redirect to login page
      return NextResponse.redirect(url);
    }
  }

  // For API routes, check for authentication token
  const isApiRoute = request.nextUrl.pathname.startsWith('/api');
  if (isApiRoute) {
    let token = request.headers.get('authorization')?.replace('Bearer ', '');

    if (!token) {
      token = request.cookies.get('auth-token')?.value;
    }

    // If this is an API route that requires authentication (excluding public routes like login/register)
    const isPublicApiRoute = request.nextUrl.pathname.includes('/login') ||
                            request.nextUrl.pathname.includes('/register');

    // If it's a protected API route and no token is found, return unauthorized
    if (!isPublicApiRoute && !token) {
      return NextResponse.json({ error: 'Authentication required' }, { status: 401 });
    }
  }

  // Continue with the request for all other cases
  return NextResponse.next();
}

// Specify which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes handled separately in the code)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - login, register (public auth pages)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|login|register|dashboard|settings|chat).*)',
  ],
};

