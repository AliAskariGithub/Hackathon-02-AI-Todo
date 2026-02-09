import LoginForm from '@/components/Auth/LoginForm';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center mt-20 py-6 px-4 sm:px-6 lg:px-8 bg-secondary-light dark:bg-secondary-dark">
      <LoginForm />
    </div>
  );
}