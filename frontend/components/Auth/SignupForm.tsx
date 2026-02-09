"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import apiClient from "@/services/api-client";
import { useAuth } from "@/providers/auth-provider";
import { Spinner } from "@/components/ui/spinner";
import { motion } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { toast } from "@/hooks/use-toast";

interface User {
  id: string;
  email: string;
  name?: string;
  user_name?: string;
}

export default function SignupForm() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const router = useRouter();
  const prefersReducedMotion = useReducedMotion();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      const errorMsg = "Passwords do not match";
      setError(errorMsg);
      toast({
        variant: "destructive",
        title: "Validation Error",
        description: errorMsg,
      });
      return;
    }

    if (password.length < 6) {
      const errorMsg = "Password must be at least 6 characters long";
      setError(errorMsg);
      toast({
        variant: "warning",
        title: "Weak Password",
        description: errorMsg,
      });
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Register user - backend will auto-login and set cookies
      const response = await apiClient.post<{ user: User; access_token?: string }>('/api/users/register', {
        user_name: username,
        email,
        password,
      });

      if (response.user) {
        // Update auth context with user data
        // Cookies are already set by the backend
        login(response.user);

        // Show success toast
        toast({
          variant: "success",
          title: "Account Created!",
          description: "Welcome! Redirecting to dashboard...",
        });

        router.push("/dashboard");
        router.refresh();
      } else {
        const errorMsg = "Registration failed. Please try again.";
        setError(errorMsg);
        toast({
          variant: "destructive",
          title: "Registration Failed",
          description: errorMsg,
        });
      }
    } catch (err: unknown) {
      console.error("Signup error:", err);

      let errorMessage = "An error occurred during signup";

      if (typeof err === 'object' && err !== null && 'message' in err) {
        const errorObj = err as { message?: string; response?: { data?: { detail?: string } } };

        if (errorObj.message?.includes("409")) {
          errorMessage = "A user with this email already exists";
        } else if (errorObj.message?.includes("422")) {
          errorMessage = "Invalid input data. Please check your information.";
        } else if (errorObj.response?.data?.detail) {
          errorMessage = errorObj.response.data.detail;
        } else if ('message' in errorObj && typeof errorObj.message === 'string') {
          errorMessage = errorObj.message;
        }
      }

      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "Signup Failed",
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
      className="w-full max-w-md md:max-w-xl mx-auto"
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
                Create Your Account
              </h2>
              <p className="mt-2 text-gray-600 dark:text-gray-300">
                Join us today to boost your productivity
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

            <div className="space-y-4">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: prefersReducedMotion ? 0 : 0.3 }}
              >
                <label htmlFor="username" className={`block text-sm font-medium mb-2 transition-colors duration-200 ${focusedField === 'username' ? 'text-primary' : 'text-gray-700 dark:text-gray-300'
                  }`}>
                  Username
                </label>
                <div className="relative">
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    onFocus={() => setFocusedField('username')}
                    onBlur={() => setFocusedField(null)}
                    required
                    aria-describedby="username-help"
                    className={inputClasses('username')}
                    placeholder="Choose a username"
                  />
                </div>
                <p id="username-help" className="sr-only">Enter your desired username</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: prefersReducedMotion ? 0 : 0.35 }}
              >
                <label htmlFor="email" className={`block text-sm font-medium mb-2 transition-colors duration-200 ${focusedField === 'email' ? 'text-primary' : 'text-gray-700 dark:text-gray-300'
                  }`}>
                  Email
                </label>
                <div className="relative">
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onFocus={() => setFocusedField('email')}
                    onBlur={() => setFocusedField(null)}
                    required
                    aria-describedby="email-help"
                    className={inputClasses('email')}
                    placeholder="your@email.com"
                  />
                </div>
                <p id="email-help" className="sr-only">Enter your email address</p>
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
                    placeholder="Create a strong password"
                  />
                </div>
                <p id="password-help" className="sr-only">Enter your password</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: prefersReducedMotion ? 0 : 0.45 }}
              >
                <label htmlFor="confirmPassword" className={`block text-sm font-medium mb-2 transition-colors duration-200 ${focusedField === 'confirmPassword' ? 'text-primary' : 'text-gray-700 dark:text-gray-300'
                  }`}>
                  Confirm Password
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    onFocus={() => setFocusedField('confirmPassword')}
                    onBlur={() => setFocusedField(null)}
                    required
                    aria-describedby="confirm-password-help"
                    className={inputClasses('confirmPassword')}
                    placeholder="Confirm your password"
                  />
                </div>
                <p id="confirm-password-help" className="sr-only">Confirm your password</p>
              </motion.div>
            </div>

            <motion.button
              type="submit"
              disabled={loading}
              className={`w-full flex justify-center py-3 px-4 rounded-lg shadow-md text-base font-semibold transition-all duration-300 ${loading
                ? "bg-gray-400 text-gray-700 cursor-not-allowed"
                : "bg-linear-to-r from-primary-custom to-[#0CCC40] text-[#161616] hover:from-[#0CCC40] hover:to-[#0AAA30] hover:shadow-lg hover:shadow-primary/30"
                }`}
              whileHover={loading || prefersReducedMotion ? {} : { scale: 1.02 }}
              whileTap={loading || prefersReducedMotion ? {} : { scale: 0.98 }}
            >
              {loading ? (
                <>
                  <Spinner className="mr-2 h-5 w-5 animate-spin" />
                  Creating Account...
                </>
              ) : (
                "Create Account"
              )}
            </motion.button>

            <motion.div
              className="text-center text-sm text-gray-600 dark:text-gray-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: prefersReducedMotion ? 0 : 0.5 }}
            >
              Already have an account?{' '}
              <a href="/login" className="font-medium text-primary hover:text-[#0CCC40] transition-colors underline-slide">
                Log In
              </a>
            </motion.div>
          </form>
        </div>
      </div>
    </motion.div>
  );
}