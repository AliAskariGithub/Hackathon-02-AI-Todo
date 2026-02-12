'use client';

import { PageWrapper } from '@/components/ui/page-wrapper';
import { motion } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { FileText, AlertCircle, CheckCircle, XCircle, Scale, Mail } from 'lucide-react';

export default function TermsOfServicePage() {
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
                <FileText className="w-8 h-8 text-primary" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
              Terms of Service
            </h1>
            <p className="text-muted-foreground text-lg">
              Last updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
          </div>

          {/* Introduction */}
          <section className="prose prose-gray dark:prose-invert max-w-none">
            <div className="bg-muted/30 rounded-lg p-6 mb-8">
              <p className="text-lg leading-relaxed m-0">
                Welcome to Y-Todo. By accessing or using our service, you agree to be bound by these Terms of Service. Please read them carefully before using our application.
              </p>
            </div>

            {/* Acceptance of Terms */}
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <CheckCircle className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Acceptance of Terms</h2>
                  <p className="mb-4">
                    By creating an account or using Y-Todo, you agree to these Terms of Service and our Privacy Policy. If you do not agree to these terms, you may not use our service.
                  </p>
                  <p className="mb-4">
                    We reserve the right to modify these terms at any time. We will notify users of any material changes via email or through the application. Your continued use of the service after such modifications constitutes your acceptance of the updated terms.
                  </p>
                </div>
              </div>

              {/* Account Registration */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <FileText className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Account Registration</h2>
                  <p className="mb-4">
                    To use Y-Todo, you must create an account. You agree to:
                  </p>
                  <ul className="space-y-2">
                    <li>Provide accurate, current, and complete information</li>
                    <li>Maintain and promptly update your account information</li>
                    <li>Keep your password secure and confidential</li>
                    <li>Notify us immediately of any unauthorized access</li>
                    <li>Be responsible for all activities under your account</li>
                    <li>Be at least 13 years of age to use our service</li>
                  </ul>
                  <p className="mt-4">
                    You may not create an account using false information or on behalf of someone else without permission.
                  </p>
                </div>
              </div>

              {/* Acceptable Use */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <CheckCircle className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Acceptable Use</h2>
                  <p className="mb-4">
                    You agree to use Y-Todo only for lawful purposes. You agree NOT to:
                  </p>
                  <ul className="space-y-2">
                    <li>Violate any applicable laws or regulations</li>
                    <li>Infringe on intellectual property rights of others</li>
                    <li>Upload malicious code, viruses, or harmful content</li>
                    <li>Attempt to gain unauthorized access to our systems</li>
                    <li>Interfere with or disrupt the service or servers</li>
                    <li>Use automated systems to access the service without permission</li>
                    <li>Harass, abuse, or harm other users</li>
                    <li>Impersonate any person or entity</li>
                    <li>Collect or store personal data of other users</li>
                  </ul>
                </div>
              </div>

              {/* User Content */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <FileText className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">User Content</h2>
                  <p className="mb-4">
                    You retain all rights to the content you create in Y-Todo (tasks, descriptions, notes, etc.). By using our service, you grant us a limited license to:
                  </p>
                  <ul className="space-y-2 mb-4">
                    <li>Store and display your content as necessary to provide the service</li>
                    <li>Back up your content for data protection purposes</li>
                    <li>Use anonymized, aggregated data for analytics and improvements</li>
                  </ul>
                  <p className="mb-4">
                    You are solely responsible for your content and the consequences of posting or publishing it. You represent that you have all necessary rights to your content and that it does not violate any laws or third-party rights.
                  </p>
                </div>
              </div>

              {/* Service Availability */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <AlertCircle className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Service Availability</h2>
                  <p className="mb-4">
                    We strive to provide reliable service, but we cannot guarantee:
                  </p>
                  <ul className="space-y-2">
                    <li>Uninterrupted or error-free operation</li>
                    <li>That defects will be corrected immediately</li>
                    <li>That the service will meet your specific requirements</li>
                    <li>That the service will be available at all times</li>
                  </ul>
                  <p className="mt-4">
                    We reserve the right to modify, suspend, or discontinue the service (or any part thereof) at any time with or without notice. We will not be liable for any modification, suspension, or discontinuation of the service.
                  </p>
                </div>
              </div>

              {/* Intellectual Property */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Scale className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Intellectual Property</h2>
                  <p className="mb-4">
                    The Y-Todo service, including its original content, features, and functionality, is owned by Y-Todo and is protected by international copyright, trademark, patent, trade secret, and other intellectual property laws.
                  </p>
                  <p className="mb-4">
                    You may not copy, modify, distribute, sell, or lease any part of our service without our prior written permission. You may not reverse engineer or attempt to extract the source code of our software.
                  </p>
                </div>
              </div>

              {/* Termination */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <XCircle className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Termination</h2>
                  <p className="mb-4">
                    You may terminate your account at any time by contacting us or using the account deletion feature in the application.
                  </p>
                  <p className="mb-4">
                    We reserve the right to suspend or terminate your account if:
                  </p>
                  <ul className="space-y-2">
                    <li>You violate these Terms of Service</li>
                    <li>You engage in fraudulent or illegal activities</li>
                    <li>Your account has been inactive for an extended period</li>
                    <li>We are required to do so by law</li>
                  </ul>
                  <p className="mt-4">
                    Upon termination, your right to use the service will immediately cease. We may delete your account and content, though we may retain certain information as required by law or for legitimate business purposes.
                  </p>
                </div>
              </div>

              {/* Disclaimer of Warranties */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Disclaimer of Warranties</h2>
                <p className="mb-4">
                  THE SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
                </p>
                <p className="mb-4">
                  We do not warrant that the service will be uninterrupted, secure, or error-free. We do not warrant that the results obtained from using the service will be accurate or reliable.
                </p>
              </div>

              {/* Limitation of Liability */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Limitation of Liability</h2>
                <p className="mb-4">
                  TO THE MAXIMUM EXTENT PERMITTED BY LAW, Y-TODO SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES.
                </p>
                <p className="mb-4">
                  Our total liability to you for any claims arising from or related to these terms or the service shall not exceed the amount you paid us in the past 12 months, or $100, whichever is greater.
                </p>
              </div>

              {/* Indemnification */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Indemnification</h2>
                <p className="mb-4">
                  You agree to indemnify, defend, and hold harmless Y-Todo and its officers, directors, employees, and agents from any claims, liabilities, damages, losses, and expenses, including reasonable attorney&apos;s fees, arising out of or in any way connected with:
                </p>
                <ul className="space-y-2">
                  <li>Your access to or use of the service</li>
                  <li>Your violation of these Terms of Service</li>
                  <li>Your violation of any third-party rights</li>
                  <li>Your content or conduct on the service</li>
                </ul>
              </div>

              {/* Governing Law */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Governing Law</h2>
                <p className="mb-4">
                  These Terms shall be governed by and construed in accordance with the laws of the jurisdiction in which Y-Todo operates, without regard to its conflict of law provisions.
                </p>
                <p className="mb-4">
                  Any disputes arising from these terms or the service shall be resolved through binding arbitration, except where prohibited by law.
                </p>
              </div>

              {/* Changes to Terms */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Changes to Terms</h2>
                <p className="mb-4">
                  We reserve the right to modify these Terms of Service at any time. If we make material changes, we will notify you by email or through a prominent notice in the application at least 30 days before the changes take effect.
                </p>
                <p className="mb-4">
                  Your continued use of the service after the effective date of the revised Terms constitutes your acceptance of the changes.
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
                    If you have any questions about these Terms of Service, please contact us:
                  </p>
                  <ul className="space-y-2">
                    <li>Email: legal@y-todo.com</li>
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
