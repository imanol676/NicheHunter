import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background py-12">
      <SignIn fallbackRedirectUrl="/dashboard" forceRedirectUrl="/dashboard" />
    </div>
  );
}
