import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Define public routes that don't require authentication
const publicRoutes = [
  '/',
  '/login',
  '/signup',
  '/forgot-password',
  '/contact',
  '/api/auth/callback',
];

// Define routes that should redirect to dashboard if already authenticated
const authRoutes = ['/login', '/signup'];

export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // IMPORTANT: In production, we use localStorage tokens (client-side only)
  // Middleware runs on server-side and CANNOT access localStorage
  // So we disable server-side auth checks in production
  // Client-side auth (auth-provider.tsx) handles authentication
  const isProduction = process.env.NODE_ENV === 'production' ||
                       process.env.NEXT_PUBLIC_API_BASE_URL?.includes('hf.space');

  if (isProduction) {
    // In production, allow all requests through
    // Client-side auth provider will handle redirects
    console.log('[Proxy] Production mode - allowing all requests through');
    return NextResponse.next();
  }

  // LOCAL DEVELOPMENT ONLY: Cookie-based auth checks below

  // Check if the current route is public
  const isPublicRoute = publicRoutes.some(route =>
    pathname === route || pathname.startsWith(`${route}/`)
  );

  // Check if the current route is an auth route (login/signup)
  const isAuthRoute = authRoutes.some(route => pathname === route);

  // Get the access_token cookie (only works in local dev)
  const accessToken = request.cookies.get('access_token');
  const hasValidSession = !!accessToken?.value;

  // If user is authenticated and trying to access auth routes, redirect to dashboard
  if (hasValidSession && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // If user is not authenticated and trying to access protected route, redirect to login
  if (!hasValidSession && !isPublicRoute) {
    const loginUrl = new URL('/login', request.url);
    // Add the original URL as a redirect parameter
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Allow the request to proceed
  return NextResponse.next();
}

// Configure which routes the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
