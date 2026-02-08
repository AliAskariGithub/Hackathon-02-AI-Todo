# AI Todo Application

A full-stack AI-powered todo application built with modern web technologies. The project includes both frontend and backend components with authentication, task management, and testimonials system.

## 🚀 Features

### Core Features
- **User Authentication**: Complete login/signup flow with email/username and password
- **Task Management**: Full CRUD operations on tasks with optimistic updates
- **Testimonials System**: User-submitted testimonials with ratings and feedback
- **Responsive UI**: Mobile-friendly design with loading states and error handling
- **JWT Authentication**: Secure token-based authentication with proper session management
- **Database Integration**: PostgreSQL with Neon hosting for serverless scalability

### Interactive Chat Experience 🆕
- **AI Task Assistant**: Natural language chat interface for task management
- **Simple Language Mode**: AI responses in grade 6-8 reading level for better accessibility
- **Keyboard Shortcuts**: Power user navigation with visual indicators
  - `Cmd/Ctrl + K`: Focus chat input
  - `Enter`: Send message
  - `Shift + Enter`: New line
  - `Esc`: Exit focus mode
- **Focus Mode**: Distraction-free chat with smooth animations and centered layout
- **Task Navigation**: Click task references in chat to navigate directly to task details
- **JSON Display Toggle**: Switch between human-readable and structured JSON responses
- **Accessibility**: Full keyboard navigation, ARIA labels, reduced motion support

### Enhanced UI/UX
- **Custom Auth Pages**: Login/signup pages with Electric Lime theme (#0FFF50)
- **Testimonial Carousel**: Auto-rotating testimonials with smooth transitions
- **Dynamic Pages**: Contact page with form validation, Settings page with tabbed UI
- **Comprehensive Footer**: Multi-column responsive footer with navigation and social links
- **Smooth Animations**: Page transitions using Framer Motion with accessibility considerations
- **Theme System**: Dark/light mode toggle with consistent color scheme

## 🛠️ Tech Stack

### Frontend
- Next.js 16.1.2 with App Router
- React 19.2.3
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Lucide React icons
- Framer Motion 12.31.0 for animations
- Better Auth for authentication
- Zustand 5.0.11 for state management
- react-json-view 1.21.3 for JSON rendering
- Zod for form validation
- React Hook Form for form handling

### Backend
- Python 3.11+
- FastAPI
- SQLModel
- PostgreSQL (Neon serverless)
- JWT for authentication
- bcrypt for password hashing

## 📋 Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL database (or Neon account)

## 🚀 Quick Start

### Automated Setup (Recommended)

**For Windows:**
```bash
# Frontend
cd frontend
setup-local.bat

# Backend
cd backend
setup-local.bat
```

**For macOS/Linux:**
```bash
# Frontend
cd frontend
chmod +x setup-local.sh
./setup-local.sh

# Backend
cd backend
chmod +x setup-local.sh
./setup-local.sh
```

### Manual Setup

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy the environment file and configure:
```bash
# For local development
cp .env.example .env.local

# For production
cp .env.example .env.production
```

4. Edit `.env.local` with your configuration:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
NEXT_PUBLIC_SITE_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

5. Start the development server:
```bash
npm run dev
```

**Available on:**
- Primary: `http://localhost:3000`
- Alternative: `http://localhost:3001`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the environment file and configure:
```bash
# For local development
cp .env.example .env.local

# For production
cp .env.example .env.production
```

5. Edit `.env.local` with your configuration:
```env
DATABASE_URL=sqlite:///./ai_todo_dev.db
BETTER_AUTH_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
PORT=8001
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

6. Start the backend server:
```bash
python main.py
```

**Available on:**
- Primary: `http://localhost:8001`
- Alternative: `http://localhost:8000`
- API Docs: `http://localhost:8001/docs`

## 🔧 Environment Variables

### Frontend Environment Variables

Create `.env.local` for local development or `.env.production` for production:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001  # or production URL
NEXT_PUBLIC_SITE_URL=http://localhost:3000      # or production URL

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Development Settings
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_VERBOSE_LOGGING=true
```

### Backend Environment Variables

Create `.env.local` for local development or `.env.production` for production:

```env
# Database
DATABASE_URL=sqlite:///./ai_todo_dev.db  # or PostgreSQL URL

# Authentication (must match frontend)
BETTER_AUTH_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
JWT_EXPIRATION_DELTA_MINUTES=30

# AI Configuration
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile

# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=true
LOG_LEVEL=debug

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
ENABLE_RATE_LIMITING=false
RATE_LIMIT_PER_MINUTE=100
```

**Important:**
- Generate secure keys with: `openssl rand -base64 32`
- Never commit `.env.local` or `.env.production` to version control
- Ensure `BETTER_AUTH_SECRET` matches between frontend and backend

For detailed environment setup instructions, see [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md)

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/           # API routes
│   │   │   └── routers/   # API endpoints (tasks, chat, users, etc.)
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   ├── mcp/           # MCP tools and runners
│   │   └── utils/         # Utilities
│   ├── main.py            # Application entry point
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Environment template
│   └── setup-local.sh/bat # Setup scripts
├── frontend/               # Next.js frontend
│   ├── app/               # App Router pages
│   │   ├── (auth)/        # Auth pages (login, signup, settings)
│   │   ├── chat/          # Chat page (main route)
│   │   ├── contact/       # Contact page
│   │   ├── dashboard/     # Dashboard page
│   │   └── page.tsx       # Home page
│   ├── components/        # React components
│   │   ├── chat/          # Chat components
│   │   │   ├── FocusModeToggle.tsx
│   │   │   ├── FocusModeWrapper.tsx
│   │   │   ├── DisplayModeToggle.tsx
│   │   │   ├── JsonMessageView.tsx
│   │   │   ├── TaskLinkButton.tsx
│   │   │   └── KeyboardShortcutHint.tsx
│   │   ├── ui/            # UI components (shadcn/ui + custom)
│   │   │   ├── kbd.tsx    # Keyboard shortcut indicator
│   │   │   └── ...        # Other UI components
│   │   ├── Navbar.tsx     # Navigation bar
│   │   └── Footer.tsx     # Footer with links
│   ├── lib/               # Shared utilities
│   │   ├── animations.ts  # Framer Motion variants
│   │   └── utils/         # Utility functions
│   │       └── taskLinkGenerator.ts
│   ├── hooks/             # React hooks
│   │   ├── useKeyboardShortcuts.ts
│   │   ├── useReducedMotion.ts
│   │   └── use-toast.ts
│   ├── stores/            # Zustand stores
│   │   └── ui-store.ts    # UI state (focus mode, display mode)
│   ├── providers/         # React context providers
│   ├── services/          # API clients
│   ├── .env.example       # Environment template
│   └── setup-local.sh/bat # Setup scripts
├── specs/                 # Feature specifications
│   └── 008-todo-interactive-chat/
│       ├── spec.md        # Feature specification
│       ├── plan.md        # Implementation plan
│       └── tasks.md       # Task breakdown
├── history/               # Development history
│   ├── prompts/           # Prompt History Records
│   └── adr/               # Architecture Decision Records
├── CLAUDE.md              # Project instructions for Claude
├── ENVIRONMENT_SETUP.md   # Detailed environment setup guide
├── TESTING_GUIDE.md       # Testing instructions
└── README.md              # This file
```

## 🧪 Available Scripts

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run linter

### Backend
- `python -m uvicorn main:app --reload` - Start development server
- `python -m py_compile $(find . -name "*.py")` - Compile all Python files

## 🔐 Authentication Flow

1. Users register with email/username and password on custom-themed signup page
2. Passwords are securely hashed using bcrypt
3. Successful login returns a JWT token
4. Token is stored in localStorage and used for authenticated requests
5. Session is maintained using React Context
6. Custom login and signup pages feature Electric Lime theme (#0FFF50) with smooth animations
7. Settings page is protected and only accessible to authenticated users

## 📊 Database Schema

The application uses PostgreSQL with the following main entities:

- **Users**: Stores user information (email, username, hashed password, profile data)
- **Tasks**: User's todo items (title, description, completion status)
- **Testimonials**: User reviews (name, email, rating, message)
- **Settings**: User preferences and settings (theme, notifications, privacy settings)

## 🚀 Deployment

### Production URLs

**Frontend (Vercel):**
- Production: https://ai-y-todo.vercel.app
- Local: http://localhost:3000 or http://localhost:3001

**Backend (Hugging Face Spaces):**
- Production: https://aliaskariface-backend-todo-app.hf.space
- Local: http://localhost:8001 or http://localhost:8000

### Deployment Instructions

#### Frontend Deployment (Vercel)

1. **Prepare Environment Variables**

Set the following in Vercel dashboard:
```env
NEXT_PUBLIC_API_BASE_URL=https://aliaskariface-backend-todo-app.hf.space
NEXT_PUBLIC_SITE_URL=https://ai-y-todo.vercel.app
BETTER_AUTH_SECRET=<your-secure-production-key>
NEXT_PUBLIC_BETTER_AUTH_URL=https://ai-y-todo.vercel.app
NEXT_PUBLIC_DEBUG=false
NEXT_PUBLIC_VERBOSE_LOGGING=false
```

2. **Deploy via Vercel CLI**
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

Or connect your GitHub repository to Vercel for automatic deployments.

#### Backend Deployment (Hugging Face Spaces)

1. **Prepare Environment Variables**

Set the following in Hugging Face Spaces secrets:
```env
DATABASE_URL=<your-neon-postgresql-url>
BETTER_AUTH_SECRET=<same-as-frontend>
JWT_SECRET=<your-secure-jwt-key>
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=llama-3.3-70b-versatile
PORT=7860
DEBUG=false
LOG_LEVEL=info
ALLOWED_ORIGINS=https://ai-y-todo.vercel.app
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
```

2. **Deploy to Hugging Face Spaces**
- Create a new Space with Docker SDK
- Upload backend code
- Configure secrets in Space settings
- Deploy

### Local Development

For local development, use the automated setup scripts:

**Windows:**
```bash
# Frontend
cd frontend
setup-local.bat

# Backend
cd backend
setup-local.bat
```

**macOS/Linux:**
```bash
# Frontend
cd frontend
chmod +x setup-local.sh
./setup-local.sh

# Backend
cd backend
chmod +x setup-local.sh
./setup-local.sh
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Issues & Support

If you encounter any issues or have questions, please file an issue in the repository.