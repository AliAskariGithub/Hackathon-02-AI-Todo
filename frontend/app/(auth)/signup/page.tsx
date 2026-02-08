import SignupForm from '@/components/Auth/SignupForm';

export default function SignupPage() {
  return (
    <div className="flex items-center justify-center mt-20 py-6 px-4 sm:px-6 lg:px-8 bg-secondary-light dark:bg-secondary-dark">
        <SignupForm />
    </div>
  );
}