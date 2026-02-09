"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import apiClient from "@/services/api-client";
import { useAuth } from "@/providers/auth-provider";
import { motion } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { toast } from "@/hooks/use-toast";

interface User {
  id: string;
  email: string;
  name?: string;
  user_name?: string;
}

export default function LoginForm() {
  const [identifier, setIdentifier] = useState(""); // Can be email or username
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [redirecting, setRedirecting] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const { login } = useAuth();
  const router = useRouter();
  const prefersReducedMotion = useReducedMotion();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setRedirecting(false);

    try {
      // Determine if identifier is email or username
      const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identifier);
      let userName;

      if (isEmail) {
        userName = identifier.split('@')[0]; // Extract username from email
      } else {
        userName = identifier;
      }

      // Call the backend API to login the user
      // Backend will set HTTP-only cookies automatically
      const response = await apiClient.post<{ user: User; access_token?: string }>('/api/users/login', {
        user_name: userName,
        email: isEmail ? identifier : "",
        password,
      });

      if (response.user) {
        // Store access token for cross-domain authentication (production)
        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
        }

        // Update auth context with user data
        login(response.user);

        setRedirecting(true);

        // Show success toast
        toast({
          variant: "success",
          title: "Login Successful!",
          description: "Welcome back! Redirecting to dashboard...",
        });

        // Use Next.js router for client-side navigation (no page reload)
        setTimeout(() => {
          router.push("/dashboard");
        }, 300);
      } else {
        const errorMsg = "Login failed. Please try again.";
        setError(errorMsg);
        toast({
          variant: "destructive",
          title: "Login Failed",
          description: errorMsg,
        });
      }
    } catch (err: unknown) {
      console.error("Login error:", err);

      let errorMessage = "An error occurred during login";

      if (typeof err === 'object' && err !== null && 'message' in err) {
        const errorObj = err as { message?: string; response?: { data?: { detail?: string } } };

        if (errorObj.message?.includes("401")) {
          errorMessage = "Invalid email or password";
        } else if (errorObj.response?.data?.detail) {
          errorMessage = errorObj.response.data.detail;
        } else if ('message' in errorObj && typeof errorObj.message === 'string') {
          errorMessage = errorObj.message;
        }
      }

      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "Login Failed",
        description: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: prefersReducedMotion ? 0 : 0.6,
      },
    },
  };

  const inputClasses = (fieldName: string) => `
    w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border rounded-lg shadow-sm 
    transition-all duration-300 ease-out
    ${focusedField === fieldName
      ? 'border-primary ring-2 ring-primary/20 scale-[1.01]'
      : 'border-gray-300 dark:border-gray-700'
    }
    focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20
  `;

  return (
    <motion.div
      className="w-full max-w-md mx-auto"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="bg-linear-to-br from-gray-900 to-black p-1 rounded-2xl shadow-2xl">
        <div className="bg-background rounded-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <motion.div
              className="text-center mb-6"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: prefersReducedMotion ? 0 : 0.2 }}
            >
              <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-linear-to-r from-primary-custom to-[#0CCC40]">
                Welcome Back
              </h2>
              <p className="mt-2 text-gray-600 dark:text-gray-300 ">
                Login to your account to continue
              </p>
            </motion.div>

            {error && (
              <motion.div
                className="bg-destructive/20 border border-destructive/30 text-destructive px-4 py-3 rounded-lg relative animate-shake"
                role="alert"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <span className="block sm:inline">{error}</span>
              </motion.div>
            )}

            {redirecting && (
              <motion.div
                className="bg-primary/20 border border-primary/30 text-primary px-4 py-3 rounded-lg relative"
                role="alert"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <span className="block sm:inline">Successfully logged in. Redirecting to dashboard...</span>
              </motion.div>
            )}

            <div className="space-y-4 mt-2">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: prefersReducedMotion ? 0 : 0.3 }}
              >
                <label htmlFor="identifier" className={`block text-sm font-medium mb-2 transition-colors duration-200 ${focusedField === 'identifier' ? 'text-primary' : 'text-gray-700 dark:text-gray-300'
                  }`}>
                  Email or Username
                </label>
                <div className="relative">
                  <input
                    id="identifier"
                    type="text"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    onFocus={() => setFocusedField('identifier')}
                    onBlur={() => setFocusedField(null)}
                    required
                    aria-describedby="identifier-help"
                    className={inputClasses('identifier')}
                    placeholder="Enter your email or username"
                  />
                </div>
                <p id="identifier-help" className="sr-only">Enter your email or username</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: prefersReducedMotion ? 0 : 0.4 }}
              >
                <label htmlFor="password" className={`block text-sm font-medium mb-2 transition-colors duration-200 ${focusedField === 'password' ? 'text-primary' : 'text-gray-700 dark:text-gray-300'
                  }`}>
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setFocusedField('password')}
                    onBlur={() => setFocusedField(null)}
                    required
                    aria-describedby="password-help"
                    className={inputClasses('password')}
                    placeholder="Enter your password"
                  />
                </div>
                <p id="password-help" className="sr-only">Enter your password</p>
              </motion.div>
            </div>

            <motion.div
              className="flex items-center justify-between"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: prefersReducedMotion ? 0 : 0.5 }}
            >
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded transition-transform duration-200 hover:scale-110"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <a href="/forgot-password" className="font-medium text-primary hover:text-[#0CCC40] transition-colors underline-slide">
                  Forgot password?
                </a>
              </div>
            </motion.div>

            <motion.button
              type="submit"
              disabled={loading || redirecting}
              className={`w-full flex justify-center py-3 px-4 rounded-lg shadow-md text-base font-semibold transition-all duration-300 ${loading || redirecting
                  ? "bg-gray-400 text-gray-700 cursor-not-allowed"
                  : "bg-linear-to-r from-primary-custom to-[#0CCC40] text-[#161616] hover:from-[#0CCC40] hover:to-[#0AAA30] hover:shadow-lg hover:shadow-primary/30"
                }`}
              whileHover={loading || redirecting || prefersReducedMotion ? {} : { scale: 1.02 }}
              whileTap={loading || redirecting || prefersReducedMotion ? {} : { scale: 0.98 }}
            >
              {redirecting ? "Redirecting..." : loading ? "Logging in..." : "Log In"}
            </motion.button>

            <motion.div
              className="text-center text-sm text-gray-600 dark:text-gray-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: prefersReducedMotion ? 0 : 0.6 }}
            >
              Don&apos;t have an account?{' '}
              <a href="/signup" className="font-medium text-primary hover:text-[#0CCC40] transition-colors underline-slide">
                Sign up
              </a>
            </motion.div>
          </form>
        </div>
      </div>
    </motion.div>
  );
}