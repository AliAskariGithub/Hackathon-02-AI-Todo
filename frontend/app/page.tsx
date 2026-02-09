'use client';

import { FeaturesSection } from "@/components/FeaturesSection";
import HeroSection from "@/components/HeroSection";
import TestimonialGrid from "@/components/Testimonials/TestimonialGrid";
import StatsShowcase from "@/components/StatsShowcase";
import PricingSection from "@/components/PricingSection";
import FAQSection from "@/components/FAQSection";
import SubscribeSection from "@/components/SubscribeSection";
import { PageWrapper } from '@/components/ui/page-wrapper';
import { Separator } from "@/components/ui/separator";

export default function Home() {
  return (
    <PageWrapper className="flex min-h-screen flex-col font-sans bg-secondary-light dark:bg-secondary-dark">
      <HeroSection />
      <Separator />
      <StatsShowcase />
      <Separator />
      <FeaturesSection />
      <Separator />
      <PricingSection />
      <Separator />
      <TestimonialGrid />
      <Separator />
      <FAQSection />
      <Separator />
      <SubscribeSection />
    </PageWrapper>
  );
}
