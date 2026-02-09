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

  // Check if the current route is public
  const isPublicRoute = publicRoutes.some(route =>
    pathname === route || pathname.startsWith(`${route}/`)
  );

  // Check if the current route is an auth route (login/signup)
  const isAuthRoute = authRoutes.some(route => pathname === route);

  // Get the access_token cookie
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
