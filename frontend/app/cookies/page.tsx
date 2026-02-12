'use client';

import { PageWrapper } from '@/components/ui/page-wrapper';
import { motion } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Cookie, Settings, Eye, ToggleLeft, Mail } from 'lucide-react';

export default function CookiePolicyPage() {
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
                <Cookie className="w-8 h-8 text-primary" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
              Cookie Policy
            </h1>
            <p className="text-muted-foreground text-lg">
              Last updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
          </div>

          {/* Introduction */}
          <section className="prose prose-gray dark:prose-invert max-w-none">
            <div className="bg-muted/30 rounded-lg p-6 mb-8">
              <p className="text-lg leading-relaxed m-0">
                This Cookie Policy explains how Y-Todo uses cookies and similar technologies to recognize you when you visit our application. It explains what these technologies are, why we use them, and your rights to control our use of them.
              </p>
            </div>

            {/* What Are Cookies */}
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Cookie className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">What Are Cookies?</h2>
                  <p className="mb-4">
                    Cookies are small text files that are placed on your device (computer, smartphone, or tablet) when you visit a website or use an application. They are widely used to make applications work more efficiently and provide information to the owners of the application.
                  </p>
                  <p className="mb-4">
                    Cookies can be &quot;persistent&quot; or &quot;session&quot; cookies:
                  </p>
                  <ul className="space-y-2">
                    <li><strong>Persistent cookies:</strong> Remain on your device for a set period or until you delete them</li>
                    <li><strong>Session cookies:</strong> Are temporary and are deleted when you close your browser</li>
                  </ul>
                </div>
              </div>

              {/* Why We Use Cookies */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Eye className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Why We Use Cookies</h2>
                  <p className="mb-4">
                    We use cookies for several reasons:
                  </p>
                  <ul className="space-y-2">
                    <li>To keep you signed in to your account</li>
                    <li>To remember your preferences and settings</li>
                    <li>To understand how you use our application</li>
                    <li>To improve our services and user experience</li>
                    <li>To ensure the security of your account</li>
                    <li>To analyze application performance</li>
                  </ul>
                </div>
              </div>

              {/* Types of Cookies We Use */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Settings className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Types of Cookies We Use</h2>

                  <div className="space-y-6">
                    {/* Essential Cookies */}
                    <div className="bg-muted/20 rounded-lg p-4">
                      <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-red-500"></span>
                        Essential Cookies
                      </h3>
                      <p className="mb-3">
                        These cookies are necessary for the application to function and cannot be disabled. They are usually set in response to actions you take, such as logging in or filling in forms.
                      </p>
                      <p className="text-sm text-muted-foreground mb-2"><strong>Examples:</strong></p>
                      <ul className="space-y-1 text-sm">
                        <li>• Authentication tokens (JWT)</li>
                        <li>• Session identifiers</li>
                        <li>• Security cookies</li>
                        <li>• Load balancing cookies</li>
                      </ul>
                      <p className="text-sm text-muted-foreground mt-3">
                        <strong>Duration:</strong> Session or up to 7 days
                      </p>
                    </div>

                    {/* Functional Cookies */}
                    <div className="bg-muted/20 rounded-lg p-4">
                      <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                        Functional Cookies
                      </h3>
                      <p className="mb-3">
                        These cookies enable enhanced functionality and personalization, such as remembering your preferences and settings.
                      </p>
                      <p className="text-sm text-muted-foreground mb-2"><strong>Examples:</strong></p>
                      <ul className="space-y-1 text-sm">
                        <li>• Theme preferences (dark/light mode)</li>
                        <li>• Language preferences</li>
                        <li>• Display settings</li>
                        <li>• Notification preferences</li>
                      </ul>
                      <p className="text-sm text-muted-foreground mt-3">
                        <strong>Duration:</strong> Up to 1 year
                      </p>
                    </div>

                    {/* Analytics Cookies */}
                    <div className="bg-muted/20 rounded-lg p-4">
                      <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-green-500"></span>
                        Analytics Cookies
                      </h3>
                      <p className="mb-3">
                        These cookies help us understand how visitors interact with our application by collecting and reporting information anonymously.
                      </p>
                      <p className="text-sm text-muted-foreground mb-2"><strong>Examples:</strong></p>
                      <ul className="space-y-1 text-sm">
                        <li>• Page views and navigation patterns</li>
                        <li>• Feature usage statistics</li>
                        <li>• Error tracking</li>
                        <li>• Performance metrics</li>
                      </ul>
                      <p className="text-sm text-muted-foreground mt-3">
                        <strong>Duration:</strong> Up to 2 years
                      </p>
                    </div>

                    {/* Performance Cookies */}
                    <div className="bg-muted/20 rounded-lg p-4">
                      <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
                        Performance Cookies
                      </h3>
                      <p className="mb-3">
                        These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our application.
                      </p>
                      <p className="text-sm text-muted-foreground mb-2"><strong>Examples:</strong></p>
                      <ul className="space-y-1 text-sm">
                        <li>• Load time measurements</li>
                        <li>• Response time tracking</li>
                        <li>• Resource usage monitoring</li>
                        <li>• Error rate tracking</li>
                      </ul>
                      <p className="text-sm text-muted-foreground mt-3">
                        <strong>Duration:</strong> Up to 1 year
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Third-Party Cookies */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Third-Party Cookies</h2>
                <p className="mb-4">
                  In addition to our own cookies, we may use third-party cookies to report usage statistics and deliver relevant content. These third parties have their own privacy policies:
                </p>
                <ul className="space-y-2">
                  <li><strong>Authentication Services:</strong> For secure login and account management</li>
                  <li><strong>Analytics Providers:</strong> To understand application usage and improve user experience</li>
                  <li><strong>Content Delivery Networks (CDN):</strong> To deliver content efficiently</li>
                </ul>
              </div>

              {/* Local Storage */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Local Storage and Similar Technologies</h2>
                <p className="mb-4">
                  In addition to cookies, we may use other technologies such as:
                </p>
                <ul className="space-y-2">
                  <li><strong>Local Storage:</strong> To store user preferences and application state locally in your browser</li>
                  <li><strong>Session Storage:</strong> To temporarily store data during your browsing session</li>
                  <li><strong>IndexedDB:</strong> To store larger amounts of structured data for offline functionality</li>
                </ul>
                <p className="mt-4">
                  These technologies serve similar purposes to cookies but can store more data and persist longer on your device.
                </p>
              </div>

              {/* Your Cookie Choices */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <ToggleLeft className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Your Cookie Choices</h2>
                  <p className="mb-4">
                    You have several options to manage cookies:
                  </p>

                  <h3 className="text-xl font-semibold mb-3">Browser Settings</h3>
                  <p className="mb-4">
                    Most web browsers allow you to control cookies through their settings. You can:
                  </p>
                  <ul className="space-y-2 mb-6">
                    <li>Block all cookies</li>
                    <li>Block third-party cookies only</li>
                    <li>Delete cookies when you close your browser</li>
                    <li>View and delete individual cookies</li>
                  </ul>

                  <h3 className="text-xl font-semibold mb-3">Application Settings</h3>
                  <p className="mb-4">
                    You can manage certain preferences within the Y-Todo application:
                  </p>
                  <ul className="space-y-2 mb-6">
                    <li>Go to Settings → Privacy</li>
                    <li>Adjust your cookie preferences</li>
                    <li>Enable or disable analytics tracking</li>
                  </ul>

                  <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mt-4">
                    <p className="text-sm m-0">
                      <strong>Note:</strong> If you block or delete essential cookies, some features of Y-Todo may not function properly, and you may not be able to access certain parts of the application.
                    </p>
                  </div>
                </div>
              </div>

              {/* Do Not Track */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Do Not Track Signals</h2>
                <p className="mb-4">
                  Some browsers include a &quot;Do Not Track&quot; (DNT) feature that signals to websites that you do not want to have your online activity tracked. Currently, there is no industry standard for how to respond to DNT signals.
                </p>
                <p className="mb-4">
                  Y-Todo does not currently respond to DNT signals, but we are committed to respecting your privacy choices and will update our practices as industry standards evolve.
                </p>
              </div>

              {/* Updates to Cookie Policy */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">Updates to This Cookie Policy</h2>
                <p className="mb-4">
                  We may update this Cookie Policy from time to time to reflect changes in our practices or for other operational, legal, or regulatory reasons. We will notify you of any material changes by posting the updated policy on this page with a new &quot;Last updated&quot; date.
                </p>
                <p className="mb-4">
                  We encourage you to review this Cookie Policy periodically to stay informed about how we use cookies.
                </p>
              </div>

              {/* More Information */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4">More Information About Cookies</h2>
                <p className="mb-4">
                  To learn more about cookies and how to manage them, visit:
                </p>
                <ul className="space-y-2">
                  <li><a href="https://www.allaboutcookies.org" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">AllAboutCookies.org</a></li>
                  <li><a href="https://www.youronlinechoices.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">YourOnlineChoices.com</a></li>
                  <li><a href="https://www.networkadvertising.org" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Network Advertising Initiative</a></li>
                </ul>
              </div>

              {/* Contact */}
              <div className="flex items-start gap-4 mt-8">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Mail className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-4 mt-0">Contact Us</h2>
                  <p className="mb-4">
                    If you have any questions about our use of cookies, please contact us:
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
