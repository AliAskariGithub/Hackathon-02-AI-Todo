# AI Todo - Frontend

Modern Next.js frontend for the AI Todo application with interactive chat, task management, and authentication.

## 🚀 Tech Stack

- **Framework**: Next.js 16.1.2 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **Animations**: Framer Motion 12.31.0
- **State Management**: Zustand 5.0.11
- **Forms**: React Hook Form + Zod validation
- **Authentication**: Better Auth
- **JSON Rendering**: react-json-view 1.21.3

## 📋 Prerequisites

- Node.js 18+ (LTS recommended)
- npm or yarn package manager

## 🛠️ Setup

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

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**
```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your configuration
```

3. **Environment variables:**
```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Authentication (optional for local dev)
BETTER_AUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Development Settings (optional)
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_VERBOSE_LOGGING=true
```

4. **Start development server:**
```bash
npm run dev
```

**Access at:**
- Primary: http://localhost:3000
- Alternative: http://localhost:3001

## 📜 Available Scripts

### Development
```bash
npm run dev          # Start development server with Turbopack
npm run dev:legacy   # Start development server without Turbopack
```

### Production
```bash
npm run build        # Build for production
npm run start        # Start production server
```

### Code Quality
```bash
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors automatically
npm run type-check   # Run TypeScript type checking
```

## 🏗️ Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Authentication routes
│   │   ├── login/           # Login page
│   │   └── signup/          # Signup page
│   ├── chat/                # AI chat interface
│   ├── dashboard/           # User dashboard
│   ├── settings/            # User settings
│   ├── contact/             # Contact page
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Homepage
│   └── globals.css          # Global styles
├── components/              # React components
│   ├── Auth/               # Authentication components
│   ├── chat/               # Chat interface components
│   ├── Dashboard/          # Dashboard components
│   ├── Testimonials/       # Testimonial components
│   ├── ui/                 # shadcn/ui components
│   ├── HeroSection.tsx     # Hero section
│   ├── Navbar.tsx          # Navigation bar
│   └── Footer.tsx          # Footer
├── lib/                    # Utilities
│   ├── animations.ts       # Framer Motion variants
│   └── utils/              # Helper functions
├── hooks/                  # Custom React hooks
│   ├── useKeyboardShortcuts.ts
│   ├── useReducedMotion.ts
│   └── use-toast.ts
├── stores/                 # Zustand stores
│   └── ui-store.ts         # UI state management
├── providers/              # React context providers
│   └── auth-provider.tsx   # Authentication provider
├── services/               # API clients
│   └── api.ts              # API service layer
├── public/                 # Static assets
├── .env.example            # Environment template
└── package.json            # Dependencies
```

## 🎨 Key Features

### Interactive Chat Experience
- **AI Task Assistant**: Natural language interface for task management
- **Simple Language Mode**: Grade 6-8 reading level for accessibility
- **Keyboard Shortcuts**:
  - `Cmd/Ctrl + K`: Focus chat input
  - `Enter`: Send message
  - `Shift + Enter`: New line
  - `Esc`: Exit focus mode
- **Focus Mode**: Distraction-free chat with smooth animations
- **Task Navigation**: Click task references to navigate directly
- **JSON Display Toggle**: Switch between human-readable and structured JSON
- **Full Accessibility**: ARIA labels, keyboard navigation, reduced motion support

### Authentication
- **Secure Cookie-Based Auth**: HTTP-only cookies for XSS protection
- **Automatic Token Refresh**: Seamless 14-minute token refresh
- **Protected Routes**: Automatic redirect for unauthenticated users

### UI/UX Enhancements
- **Custom Auth Pages**: Electric Lime theme (#0FFF50)
- **Testimonial Carousel**: Auto-rotating with smooth transitions
- **Theme System**: Dark/light mode toggle
- **Smooth Animations**: Framer Motion with accessibility considerations
- **Responsive Design**: Mobile-friendly across all pages

## 🔧 Configuration

### Environment Variables

**Required:**
- `NEXT_PUBLIC_API_BASE_URL`: Backend API URL
- `NEXT_PUBLIC_SITE_URL`: Frontend site URL

**Optional:**
- `BETTER_AUTH_SECRET`: Authentication secret (32+ characters)
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth URL
- `NEXT_PUBLIC_DEBUG`: Enable debug mode
- `NEXT_PUBLIC_VERBOSE_LOGGING`: Enable verbose logging

### Tailwind Configuration

Custom theme colors:
- **Electric Lime**: `#0FFF50` (primary brand color)
- **Dark Mode**: Automatic based on system preference

### TypeScript Configuration

- Strict mode enabled
- Path aliases configured (`@/` for root imports)
- Type checking on build

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t ai-todo-frontend:latest .
```

### Run Container
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
  -e NEXT_PUBLIC_SITE_URL=http://localhost:3000 \
  ai-todo-frontend:latest
```

### Docker Compose
```bash
# From project root
docker-compose up frontend
```

## ☸️ Kubernetes Deployment

### Using Helm
```bash
# From project root
helm install ai-todo ./charts/ai-todo
```

### Access via Port Forward
```bash
kubectl port-forward service/ai-todo-frontend 8080:80
# Access at: http://localhost:8080
```

## 🧪 Testing

### Manual Testing Checklist

**Authentication:**
- [ ] User can sign up with email and password
- [ ] User can log in with credentials
- [ ] User is redirected after login
- [ ] Protected routes redirect to login
- [ ] Logout clears session

**Task Management:**
- [ ] User can create new tasks
- [ ] User can view task list
- [ ] User can edit tasks
- [ ] User can delete tasks
- [ ] User can mark tasks as complete

**Chat Interface:**
- [ ] Chat input accepts text
- [ ] Messages are sent and displayed
- [ ] AI responses appear correctly
- [ ] Task links are clickable
- [ ] Keyboard shortcuts work
- [ ] Focus mode toggles correctly
- [ ] JSON display toggle works

**UI/UX:**
- [ ] Theme toggle works
- [ ] Animations are smooth
- [ ] Responsive on mobile
- [ ] Reduced motion respected
- [ ] Loading states display
- [ ] Error messages show

## 🔍 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port 3000
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Mac/Linux

# Kill process or use different port
PORT=3001 npm run dev
```

**Build errors:**
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

**API connection issues:**
- Verify `NEXT_PUBLIC_API_BASE_URL` is correct
- Check backend is running
- Verify CORS is configured on backend
- Check browser console for errors

**Authentication not working:**
- Verify `BETTER_AUTH_SECRET` matches backend
- Clear browser cookies
- Check backend `/api/auth` endpoints
- Verify token expiration settings

## 📚 Documentation

- **Main README**: [../README.md](../README.md)
- **Environment Setup**: [../ENVIRONMENT_SETUP.md](../ENVIRONMENT_SETUP.md)
- **Testing Guide**: [../TESTING_GUIDE.md](../TESTING_GUIDE.md)
- **Docker Guide**: [../docs/DOCKER_GUIDE.md](../docs/DOCKER_GUIDE.md)
- **Kubernetes Guide**: [../docs/MINIKUBE_GUIDE.md](../docs/MINIKUBE_GUIDE.md)

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Add proper error handling
4. Test on multiple screen sizes
5. Respect accessibility guidelines
6. Use semantic HTML
7. Follow React best practices

## 📄 License

See [../LICENSE](../LICENSE) for details.

---

**Built with ❤️ using Next.js 16.1.2**
