'use client';

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { useSession } from '@/lib/auth';
import { useAuth } from '@/providers/auth-provider';
import { User, Menu, Settings, LogOut, X, Sparkles, LayoutDashboard, MessageSquare, Mail, ChevronDown } from 'lucide-react';
import { useState, useEffect } from 'react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { cn } from '@/lib/utils';
import { usePathname } from 'next/navigation';

const homeSections = [
  { name: 'Hero', href: '//' },
  { name: 'Stats', href: '/#stats' },
  { name: 'How It Works', href: '/#how-it-works' },
  { name: 'Features', href: '/#features' },
  { name: 'Pricing', href: '/#pricing' },
  { name: 'Testimonials', href: '//#testimonials' },
  { name: 'FAQ', href: '/#faq' },
  { name: 'Subscribe', href: '/#subscribe' },
];

export default function Navbar() {
  const { data: session } = useSession();
  const { logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState('hero');
  const prefersReducedMotion = useReducedMotion();
  const pathname = usePathname();

  // Track scroll position for navbar effects
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);

      // Detect active section
      const sections = ['hero', 'stats', 'features', 'testimonials', 'pricing', 'faq', 'subscribe'];
      for (const section of sections) {
        const element = document.getElementById(section);
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= 100 && rect.bottom >= 100) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navVariants: Variants = {
    hidden: { y: -100, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.6,
        ease: [0.22, 1, 0.36, 1] as const
      },
    },
  };

  const navContainerClasses = cn(
    "fixed z-50 left-1/2 -translate-x-1/2 transition-all duration-300 md:max-w-7xl w-full",
    scrolled ? "top-4 px-4" : "top-0 px-0"
  );

  const navInnerClasses = cn(
    "relative flex items-center justify-between px-6 transition-all duration-500",
    scrolled
      ? "py-3 bg-background/60 backdrop-blur-xl border border-white/10 shadow-2xl rounded-2xl md:rounded-full"
      : "py-4 bg-transparent border-b border-transparent md:border-b-white/5"
  );

  return (
    <>
      <motion.nav
        className={navContainerClasses}
        variants={navVariants}
        initial="hidden"
        animate="visible"
      >
        <div className={navInnerClasses}>
          {/* Logo */}
          <motion.div
            className="flex items-center gap-2"
            whileHover={prefersReducedMotion ? {} : { scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <div className={cn(
              "relative flex items-center justify-center p-2 rounded-xl transition-all duration-300 overflow-hidden group",
              scrolled ? "bg-primary/10" : "bg-transparent"
            )}>
              <div className="absolute inset-0 bg-linear-to-br from-primary to-emerald-400 opacity-20 group-hover:opacity-100 transition-opacity duration-300" />
              <Sparkles className={cn(
                "w-5 h-5 transition-colors relative z-10",
                scrolled ? "text-primary group-hover:text-primary-foreground" : "text-primary"
              )} />
            </div>
            <Link href="/" className="font-bold text-xl tracking-tight">
              Y-<span className="text-primary">Todo</span>
            </Link>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <nav className="flex items-center gap-4">
              {/* Home Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className={cn(
                    "relative px-4 py-2 text-sm font-medium transition-colors group flex items-center gap-1",
                    pathname === '/' ? "text-primary" : "text-muted-foreground hover:text-primary"
                  )}>
                    Home
                    <ChevronDown className="w-3 h-3 transition-transform group-data-[state=open]:rotate-180" />
                    <span className={cn(
                      "absolute inset-x-0 -bottom-1 h-0.5 bg-primary transition-transform origin-left rounded-full",
                      pathname === '/' ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"
                    )} />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="start"
                  className="w-48 p-2 rounded-2xl border border-white/10 bg-background/95 backdrop-blur-xl shadow-2xl"
                  sideOffset={8}
                >
                  {homeSections.map((section) => (
                    <Link key={section.name} href={section.href}>
                      <DropdownMenuItem className={cn(
                        "cursor-pointer h-10 rounded-xl transition-colors",
                        activeSection === section.name.toLowerCase()
                          ? "bg-primary/10 text-primary font-semibold"
                          : "hover:bg-primary/5"
                      )}>
                        <span>{section.name}</span>
                      </DropdownMenuItem>
                    </Link>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>


              {session?.user && (
                <NavLink href="/dashboard" icon={<LayoutDashboard className="w-4 h-4" />}>
                  Dashboard
                </NavLink>
              )}
              {session?.user && (
                <NavLink href="/chat" icon={<MessageSquare className="w-4 h-4" />}>
                  Chat
                </NavLink>
              )}
              <NavLink href="/contact" icon={<Mail className="w-4 h-4" />}>
                Contact
              </NavLink>
            </nav>

            <div className="h-4 w-px bg-border mx-2" />

            <div className="flex items-center gap-3">
              <ThemeToggle />

              {!session?.user ? (
                <>
                  <Link href="/login">
                    <Button variant="ghost" className="hover:bg-primary/5 rounded-full px-6">Login</Button>
                  </Link>
                  <Link href="/signup">
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button className="rounded-full px-6 shadow-lg shadow-primary/20 bg-linear-to-r from-primary to-emerald-500 hover:from-primary/90 hover:to-emerald-500/90 text-primary-foreground border-0">
                        Get Started
                      </Button>
                    </motion.div>
                  </Link>
                </>
              ) : (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="group relative flex items-center gap-2 pl-2 pr-4 h-11 rounded-full bg-white/5 border border-white/10 hover:border-primary/40 hover:bg-white/10 transition-all duration-300 shadow-lg shadow-black/5"
                    >
                      <div className="relative">
                        <div className="w-7 h-7 rounded-full bg-linear-to-br from-primary via-emerald-400 to-emerald-600 flex items-center justify-center text-[10px] font-black text-[#161616] shadow-inner relative z-10">
                          {session.user.name?.[0].toUpperCase() || 'U'}
                        </div>
                        <div className="absolute inset-0 bg-primary/40 rounded-full blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      </div>
                      <div className="flex flex-col items-start leading-tight">
                        <span className="text-sm font-bold tracking-tight">{session.user.name?.split(' ')[0] || 'User'}</span>
                      </div>
                    </motion.button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    align="end"
                    className="w-72 p-2 rounded-3xl border border-white/10 bg-background/80 backdrop-blur-2xl shadow-[0_32px_64px_-16px_rgba(0,0,0,0.3)] animate-in fade-in zoom-in-95 duration-200"
                    sideOffset={12}
                  >
                    {/* User Header */}
                    <div className="px-4 py-4 mb-2 rounded-2xl bg-primary/5 border border-primary/10">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-linear-to-br from-primary to-emerald-400 flex items-center justify-center text-xl font-black text-[#161616]">
                          {session.user.name?.[0].toUpperCase() || 'U'}
                        </div>
                        <div className="overflow-hidden">
                          <h4 className="font-bold text-base truncate">{session.user.name}</h4>
                          <p className="text-xs text-muted-foreground truncate">{session.user.email}</p>
                        </div>
                      </div>
                    </div>

                    <div className="px-2 py-1.5 text-[10px] font-black uppercase tracking-widest text-muted-foreground opacity-50 mb-1">Account</div>
                    <Link href="/dashboard" className="block outline-none">
                      <DropdownMenuItem className="cursor-pointer h-12 rounded-xl focus:bg-primary/10 focus:text-primary transition-colors group/item mb-1">
                        <div className="w-8 h-8 rounded-lg bg-blue-500/5 flex items-center justify-center mr-3 group-hover/item:bg-blue-500/20 transition-colors">
                          <User className="h-4 w-4 text-blue-500" />
                        </div>
                        <span className="font-bold">Profile</span>
                      </DropdownMenuItem>
                    </Link>

                    <Link href="/settings" className="block outline-none">
                      <DropdownMenuItem className="cursor-pointer h-12 rounded-xl focus:bg-primary/10 focus:text-primary transition-colors group/item mb-1">
                        <div className="w-8 h-8 rounded-lg bg-emerald-500/5 flex items-center justify-center mr-3 group-hover/item:bg-emerald-500/20 transition-colors">
                          <Settings className="h-4 w-4 text-emerald-500" />
                        </div>
                        <span className="font-bold">Settings</span>
                      </DropdownMenuItem>
                    </Link>

                    <div className="h-px bg-white/5 my-2 mx-2" />

                    <DropdownMenuItem
                      className="cursor-pointer h-12 rounded-xl text-red-500 focus:text-white focus:bg-red-500 transition-all duration-300 group/logout"
                      onClick={async () => {
                        await logout();
                        window.location.href = '/login';
                      }}
                    >
                      <div className="w-8 h-8 rounded-lg bg-red-500/5 flex items-center justify-center mr-3 group-hover/logout:bg-white/20 transition-colors">
                        <LogOut className="h-4 w-4" />
                      </div>
                      <span className="font-bold">Logout</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-4">
            <ThemeToggle />
            <motion.button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-full hover:bg-primary/10 transition-colors z-50 relative"
              whileTap={{ scale: 0.9 }}
            >
              <AnimatePresence mode="wait">
                {mobileMenuOpen ? (
                  <motion.div
                    key="close"
                    initial={{ rotate: -90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: 90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <X className="h-6 w-6" />
                  </motion.div>
                ) : (
                  <motion.div
                    key="menu"
                    initial={{ rotate: 90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: -90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Menu className="h-6 w-6" />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
          </div>
        </div>
      </motion.nav>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            className="fixed inset-0 z-40 bg-background/95 backdrop-blur-2xl md:hidden pt-24 px-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex flex-col space-y-4">
              <div className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-2">Navigation</div>
              <MobileNavLink href="/" onClick={() => setMobileMenuOpen(false)}>Home</MobileNavLink>
              {session?.user && (
                <MobileNavLink href="/dashboard" onClick={() => setMobileMenuOpen(false)}>Dashboard</MobileNavLink>
              )}
              {session?.user && (
                <MobileNavLink href="/chat" onClick={() => setMobileMenuOpen(false)}>Chat</MobileNavLink>
              )}
              <MobileNavLink href="/contact" onClick={() => setMobileMenuOpen(false)}>Contact</MobileNavLink>

              <div className="h-px bg-border my-4" />

              {!session?.user ? (
                <>
                  <Link href="/login" className="block" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" className="w-full justify-start text-lg rounded-xl h-12">Login</Button>
                  </Link>
                  <Link href="/signup" className="block" onClick={() => setMobileMenuOpen(false)}>
                    <Button className="w-full text-lg rounded-xl h-12 bg-primary text-primary-foreground">Get Started</Button>
                  </Link>
                </>
              ) : (
                <>
                  <div className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-2 mt-4">Account</div>
                  <Link href="/dashboard" className="block" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" className="w-full justify-start text-lg rounded-xl h-12">Profile</Button>
                  </Link>
                  <Link href="/settings" className="block" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" className="w-full justify-start text-lg rounded-xl h-12">Settings</Button>
                  </Link>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-lg rounded-xl h-12 text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={async () => {
                      await logout();
                      window.location.href = '/login';
                    }}
                  >
                    Logout
                  </Button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function NavLink({ href, children, icon }: { href: string; children: React.ReactNode; icon?: React.ReactNode }) {
  const pathname = usePathname();
  const isActive = pathname === href || (href !== '/' && pathname?.startsWith(href));

  return (
    <Link href={href} className={cn(
      "relative px-4 py-2 text-sm font-medium transition-colors group flex items-center gap-2",
      isActive ? "text-primary" : "text-muted-foreground hover:text-primary"
    )}>
      {icon}
      {children}
      <span className={cn(
        "absolute inset-x-0 -bottom-1 h-0.5 bg-primary transition-transform origin-left rounded-full",
        isActive ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"
      )} />
    </Link>
  );
}

function MobileNavLink({ href, onClick, children }: { href: string; onClick: () => void; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className="block text-2xl font-bold py-2 hover:text-primary transition-colors"
    >
      {children}
    </Link>
  );
}
