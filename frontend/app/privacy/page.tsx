'use client';

import { PageWrapper } from '@/components/ui/page-wrapper';
import { motion } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Shield, Lock, Eye, Database, UserCheck, Mail } from 'lucide-react';

export default function PrivacyPolicyPage() {
  const prefersReducedMotion = useReducedMotion();

  const fadeIn = {
    hidden: { opacity: 0, y: prefersReducedMotion ? 0 : 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: prefersReducedMotion ? 0 : 0.6 }
    }
  };

  return (
    <PageWrapper className="min-h-screen py-20">
      <div className="container mx-auto px-4 max-w-4xl">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          className="space-y-8"
        >
          {/* Header */}
          <div className="text-center space-y-4 mb-12">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Shield className="w-8 h-8 text-primary" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
              Privacy Policy
            </h1>
            <p className="text-muted-foreground text-lg">
              Last updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
          </div>

          {/* Introduction */}
          <section className="prose prose-gray dark:prose-invert max-w-none">
            <div className="bg-muted/30 rounded-lg p-6 mb-8">
              <p className="text-lg leading-relaxed m-0">
                At Y-Todo, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our todo application. Please read this privacy policy carefully.
              </p>
            </div>

            {/* Information We Collect */}
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Database className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Information We Collect</h2>

                  <h3 className="text-xl font-semibold mb-3">Personal Information</h3>
                  <p className="mb-4">
                    When you register for an account, we collect:
                  </p>
                  <ul className="space-y-2 mb-6">
                    <li>Email address</li>
                    <li>Username</li>
                    <li>Password (encrypted and securely stored)</li>
                  </ul>

                  <h3 className="text-xl font-semibold mb-3">Task Data</h3>
                  <p className="mb-4">
                    When you use our service, we store:
                  </p>
                  <ul className="space-y-2 mb-6">
                    <li>Task titles and descriptions</li>
                    <li>Task status, priority, and due dates</li>
                    <li>Recurrence patterns and tags</li>
                    <li>Task creation and modification timestamps</li>
                  </ul>

                  <h3 className="text-xl font-semibold mb-3">Usage Information</h3>
                  <p className="mb-4">
                    We automatically collect certain information when you use our service:
                  </p>
                  <ul className="space-y-2">
                    <li>Device information (browser type, operating system)</li>
                    <li>IP address and general location</li>
                    <li>Usage patterns and feature interactions</li>
                    <li>Error logs and performance data</li>
                  </ul>
                </div>
              </div>

              {/* How We Use Your Information */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <UserCheck className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">How We Use Your Information</h2>
                  <p className="mb-4">
                    We use the information we collect to:
                  </p>
                  <ul className="space-y-2">
                    <li>Provide, maintain, and improve our services</li>
                    <li>Create and manage your account</li>
                    <li>Store and sync your tasks across devices</li>
                    <li>Send you important updates and notifications</li>
                    <li>Respond to your comments and questions</li>
                    <li>Analyze usage patterns to improve user experience</li>
                    <li>Detect and prevent fraud or abuse</li>
                    <li>Comply with legal obligations</li>
                  </ul>
                </div>
              </div>

              {/* Data Security */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Lock className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Data Security</h2>
                  <p className="mb-4">
                    We implement appropriate technical and organizational security measures to protect your personal information:
                  </p>
                  <ul className="space-y-2">
                    <li>All data is encrypted in transit using HTTPS/TLS</li>
                    <li>Passwords are hashed using industry-standard bcrypt</li>
                    <li>Database access is restricted and monitored</li>
                    <li>Regular security audits and updates</li>
                    <li>Secure authentication using JWT tokens</li>
                  </ul>
                  <p className="mt-4 text-sm text-muted-foreground">
                    However, no method of transmission over the Internet is 100% secure. While we strive to protect your personal information, we cannot guarantee its absolute security.
                  </p>
                </div>
              </div>

              {/* Data Sharing */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Eye className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Data Sharing and Disclosure</h2>
                  <p className="mb-4">
                    We do not sell, trade, or rent your personal information to third parties. We may share your information only in the following circumstances:
                  </p>
                  <ul className="space-y-2">
                    <li><strong>Service Providers:</strong> We may share data with trusted third-party service providers who assist us in operating our application (e.g., hosting, analytics)</li>
                    <li><strong>Legal Requirements:</strong> We may disclose information if required by law or in response to valid legal requests</li>
                    <li><strong>Business Transfers:</strong> In the event of a merger, acquisition, or sale of assets, your information may be transferred</li>
                    <li><strong>With Your Consent:</strong> We may share information with your explicit consent</li>
                  </ul>
                </div>
              </div>

              {/* Your Rights */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <UserCheck className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Your Rights</h2>
                  <p className="mb-4">
                    You have the following rights regarding your personal information:
                  </p>
                  <ul className="space-y-2">
                    <li><strong>Access:</strong> Request a copy of your personal data</li>
                    <li><strong>Correction:</strong> Update or correct inaccurate information</li>
                    <li><strong>Deletion:</strong> Request deletion of your account and data</li>
                    <li><strong>Export:</strong> Download your task data in a portable format</li>
                    <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
                  </ul>
                  <p className="mt-4">
                    To exercise these rights, please contact us using the information provided below.
                  </p>
                </div>
              </div>

              {/* Data Retention */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Data Retention</h2>
                <p className="mb-4">
                  We retain your personal information for as long as your account is active or as needed to provide you services. If you delete your account, we will delete your personal information within 30 days, except where we are required to retain it for legal purposes.
                </p>
              </div>

              {/* Children's Privacy */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Children&apos;s Privacy</h2>
                <p className="mb-4">
                  Our service is not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13. If you are a parent or guardian and believe your child has provided us with personal information, please contact us.
                </p>
              </div>

              {/* Changes to Privacy Policy */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Changes to This Privacy Policy</h2>
                <p className="mb-4">
                  We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the &quot;Last updated&quot; date. You are advised to review this Privacy Policy periodically for any changes.
                </p>
              </div>

              {/* Contact */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Mail className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Contact Us</h2>
                  <p className="mb-4">
                    If you have any questions about this Privacy Policy, please contact us:
                  </p>
                  <ul className="space-y-2">
                    <li>Email: privacy@y-todo.com</li>
                    <li>Website: <a href="/contact" className="text-primary hover:underline">Contact Form</a></li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
        </motion.div>
      </div>
    </PageWrapper>
  );
}
