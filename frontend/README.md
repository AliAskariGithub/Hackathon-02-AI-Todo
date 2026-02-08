# Frontend - AI Todo Application

Next.js 16.1.2 frontend application with TypeScript, Tailwind CSS, and shadcn/ui components.

## 🚀 Features

### Core Features
- **Next.js 16.1.2** with App Router and Turbopack
- **React 19.2.3** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** component library
- **Framer Motion** for animations
- **Better Auth** for authentication
- **Zustand** for state management

### Interactive Chat Experience
- AI-powered task assistant with natural language interface
- Keyboard shortcuts (Cmd/Ctrl+K, Enter, Escape)
- Focus Mode for distraction-free chat
- JSON/Human display toggle
- Direct task navigation from chat
- Full accessibility support

### UI Components
- Custom authentication pages with Electric Lime theme (#0FFF50)
- Responsive navigation with mobile menu
- Dynamic testimonial carousel
- Contact form with validation
- Settings page with tabbed interface
- Comprehensive footer with social links

## 📋 Prerequisites

- Node.js 18+ (recommended: 20+)
- npm or yarn package manager

## 🚀 Quick Start

### Automated Setup (Recommended)

**Windows:**
```bash
setup-local.bat
```

**macOS/Linux:**
```bash
chmod +x setup-local.sh
./setup-local.sh
```

### Manual Setup

1. **Install Dependencies**
```bash
npm install
```

2. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your configuration
```

3. **Start Development Server**
```bash
npm run dev
```

The application will be available at:
- Primary: http://localhost:3000
- Alternative: http://localhost:3001 (if 3000 is in use)

## 🔧 Environment Variables

Create `.env.local` for local development:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Development Settings
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_VERBOSE_LOGGING=true
```

For production, create `.env.production`:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://aliaskariface-backend-todo-app.hf.space
NEXT_PUBLIC_SITE_URL=https://ai-y-todo.vercel.app

# Authentication
BETTER_AUTH_SECRET=<your-secure-production-key>
NEXT_PUBLIC_BETTER_AUTH_URL=https://ai-y-todo.vercel.app

# Production Settings
NEXT_PUBLIC_DEBUG=false
NEXT_PUBLIC_VERBOSE_LOGGING=false
```

**Important:**
- Generate secure keys: `openssl rand -base64 32`
- Never commit `.env.local` or `.env.production` to version control
- Ensure `BETTER_AUTH_SECRET` matches backend configuration

## 📁 Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Auth pages (login, signup, settings)
│   ├── chat/                # Chat page (main route)
│   ├── contact/             # Contact page
│   ├── dashboard/           # Dashboard page
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Home page
├── components/              # React components
│   ├── chat/               # Chat-specific components
│   │   ├── DisplayModeToggle.tsx
│   │   ├── FocusModeToggle.tsx
│   │   ├── FocusModeWrapper.tsx
│   │   ├── JsonMessageView.tsx
│   │   ├── KeyboardShortcutHint.tsx
│   │   └── TaskLinkButton.tsx
│   ├── ui/                 # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── kbd.tsx         # Keyboard shortcut indicator
│   │   └── ...
│   ├── Footer.tsx          # Footer component
│   ├── Navbar.tsx          # Navigation bar
│   └── ...
├── hooks/                  # Custom React hooks
│   ├── useKeyboardShortcuts.ts
│   ├── useReducedMotion.ts
│   └── use-toast.ts
├── lib/                    # Utilities and helpers
│   ├── animations.ts       # Framer Motion variants
│   ├── auth.ts            # Auth utilities
│   ├── proxy.ts           # API proxy configuration
│   └── utils/
│       └── taskLinkGenerator.ts
├── stores/                 # Zustand stores
│   └── ui-store.ts        # UI state (focus mode, display mode)
├── providers/              # React context providers
├── services/               # API clients
├── styles/                 # Global styles
├── .env.example           # Environment template
├── .env.local             # Local environment (gitignored)
├── .env.production        # Production environment (gitignored)
├── next.config.ts         # Next.js configuration
├── tailwind.config.ts     # Tailwind configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies and scripts
```

## 🧪 Available Scripts

### Development
```bash
npm run dev          # Start development server with Turbopack
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors automatically
```

### Type Checking
```bash
npm run type-check   # Run TypeScript compiler check
```

## 🎨 Key Components

### Chat Components
- **FocusModeWrapper**: Handles focus mode layout and animations
- **FocusModeToggle**: Button to toggle focus mode
- **DisplayModeToggle**: Switch between JSON and Human display
- **JsonMessageView**: Renders JSON with syntax highlighting
- **TaskLinkButton**: Clickable task links with validation
- **KeyboardShortcutHint**: Visual keyboard shortcut indicators

### UI Components
- **KBD**: Keyboard shortcut visual component
- **Button, Input, Textarea**: Form components
- **Tabs, Switch**: Interactive UI elements
- **Toast**: Notification system

### Layout Components
- **Navbar**: Responsive navigation with mobile menu
- **Footer**: Multi-column footer with links and social icons
- **PageWrapper**: Consistent page layout wrapper

## ⌨️ Keyboard Shortcuts

- `Cmd/Ctrl + K`: Focus chat input
- `Enter`: Send message
- `Shift + Enter`: New line in message
- `Escape`: Exit focus mode

## 🎯 Routes

- `/` - Home page
- `/login` - Login page
- `/signup` - Signup page
- `/dashboard` - User dashboard
- `/chat` - AI chat interface
- `/contact` - Contact form
- `/settings` - User settings

## 🔐 Authentication

The frontend uses JWT-based authentication with:
- Token storage in localStorage
- React Context for session management
- Protected routes with authentication checks
- Automatic token refresh

## 🎨 Styling

- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Pre-built accessible components
- **Framer Motion**: Animation library
- **Custom Theme**: Electric Lime accent (#0FFF50)
- **Dark Mode**: System preference detection

## ♿ Accessibility

- Full keyboard navigation support
- ARIA labels and roles
- Reduced motion preference detection
- Screen reader compatibility
- WCAG AA color contrast compliance

## 📦 Dependencies

### Core
- next: 16.1.2
- react: 19.2.3
- typescript: 5.7.3

### UI & Styling
- tailwindcss: 4.0.14
- framer-motion: 12.31.0
- lucide-react: 0.469.0
- @radix-ui/*: Various versions

### State & Forms
- zustand: 5.0.11
- react-hook-form: 7.54.2
- zod: 3.24.1

### Utilities
- react-json-view: 1.21.3
- clsx: 2.1.1
- tailwind-merge: 2.6.0

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect Repository**
   - Link GitHub repository to Vercel
   - Configure environment variables in Vercel dashboard

2. **Environment Variables**
   ```env
   NEXT_PUBLIC_API_BASE_URL=https://aliaskariface-backend-todo-app.hf.space
   NEXT_PUBLIC_SITE_URL=https://ai-y-todo.vercel.app
   BETTER_AUTH_SECRET=<production-secret>
   NEXT_PUBLIC_BETTER_AUTH_URL=https://ai-y-todo.vercel.app
   NEXT_PUBLIC_DEBUG=false
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Manual Deployment

1. **Build**
   ```bash
   npm run build
   ```

2. **Start**
   ```bash
   npm run start
   ```

## 🐛 Troubleshooting

### Port Already in Use
If port 3000 is in use, Next.js will automatically use port 3001.

### Build Errors
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

### Type Errors
```bash
# Run type check
npm run type-check
```

### Linting Issues
```bash
# Auto-fix linting errors
npm run lint:fix
```

## 📚 Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Framer Motion Documentation](https://www.framer.com/motion)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run linting and type checks
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details