'use client';

import { useState, useEffect, useCallback } from 'react';
import TestimonialCard from './TestimonialCard';
import AddTestimonialModal from './AddTestimonialModal';
import { Button } from '@/components/ui/button';
import apiClient from '@/services/api-client';
import { Plus, MessageSquare, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Testimonial {
  id: string;
  name: string;
  email: string;
  rating: number;
  message: string;
}

export default function TestimonialGrid() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage, setItemsPerPage] = useState(1);

  useEffect(() => {
    // Load testimonials from backend
    const loadTestimonials = async () => {
      try {
        const data = await apiClient.get<Testimonial[]>('/api/testimonials');
        // If API returns empty array, use fallback data instead
        if (Array.isArray(data) && data.length === 0) {
          setTestimonials([
            { id: '1', name: 'Alex Johnson', email: 'alex@example.com', rating: 5, message: 'This tool completely transformed how I manage my daily tasks. The new dashboard is stunning!' },
            { id: '2', name: 'Sarah Williams', email: 'sarah@design.co', rating: 5, message: 'The interface is absolutely beautiful. I love the glassmorphism and the smooth animations.' },
            { id: '3', name: 'Michael Chen', email: 'mike@dev.io', rating: 4, message: 'Incredible attention to detail. The 3D interactions on the cards are just next level.' },
            { id: '4', name: 'Emily Davis', email: 'emily@writer.net', rating: 5, message: 'Simple, elegant, and powerful. Exactly what I needed to boost my productivity.' },
            { id: '5', name: 'David Wilson', email: 'david@tech.com', rating: 5, message: 'I have never used a more intuitive task manager. It is simply the best out there.' },
            { id: '6', name: 'Lisa Brown', email: 'lisa@creative.studio', rating: 4, message: 'The design is so inspiring. It actually makes me want to work on my tasks!' },
            { id: '7', name: 'James Wilson', email: 'j.wilson@tech.corp', rating: 5, message: 'Productivity increased by 200%. Visuals are pleasing and not distracting.' },
            { id: '8', name: 'Nina Patel', email: 'nina@startup.io', rating: 4, message: 'Great animations and very responsive. Love using it on my tablet.' },
            { id: '9', name: 'Robert Fox', email: 'robert@marketing.agency', rating: 5, message: 'Finally a todo app that looks as good as it works. The themes are amazing.' },
          ]);
        } else {
          setTestimonials(data);
        }
      } catch (error) {
        console.error('Error loading testimonials:', error);
        // Fallback demo data - Increased to 9 items to create exactly 3 pages of 3
        setTestimonials([
          { id: '1', name: 'Alex Johnson', email: 'alex@example.com', rating: 5, message: 'This tool completely transformed how I manage my daily tasks. The new dashboard is stunning!' },
          { id: '2', name: 'Sarah Williams', email: 'sarah@design.co', rating: 5, message: 'The interface is absolutely beautiful. I love the glassmorphism and the smooth animations.' },
          { id: '3', name: 'Michael Chen', email: 'mike@dev.io', rating: 4, message: 'Incredible attention to detail. The 3D interactions on the cards are just next level.' },
          { id: '4', name: 'Emily Davis', email: 'emily@writer.net', rating: 5, message: 'Simple, elegant, and powerful. Exactly what I needed to boost my productivity.' },
          { id: '5', name: 'David Wilson', email: 'david@tech.com', rating: 5, message: 'I have never used a more intuitive task manager. It is simply the best out there.' },
          { id: '6', name: 'Lisa Brown', email: 'lisa@creative.studio', rating: 4, message: 'The design is so inspiring. It actually makes me want to work on my tasks!' },
          { id: '7', name: 'James Wilson', email: 'j.wilson@tech.corp', rating: 5, message: 'Productivity increased by 200%. Visuals are pleasing and not distracting.' },
          { id: '8', name: 'Nina Patel', email: 'nina@startup.io', rating: 4, message: 'Great animations and very responsive. Love using it on my tablet.' },
          { id: '9', name: 'Robert Fox', email: 'robert@marketing.agency', rating: 5, message: 'Finally a todo app that looks as good as it works. The themes are amazing.' },
        ]);
      }
    };

    loadTestimonials();
  }, []);

  // Handle responsive items per page
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setItemsPerPage(3); // Desktop
      } else if (window.innerWidth >= 768) {
        setItemsPerPage(2); // Tablet
      } else {
        setItemsPerPage(1); // Mobile
      }
    };

    // Initial check
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const totalPages = Math.ceil(testimonials.length / itemsPerPage);

  const handleAddTestimonial = (testimonial: Testimonial) => {
    setTestimonials([testimonial, ...testimonials]);
  };

  const nextPage = useCallback(() => {
    if (totalPages === 0) return;
    setCurrentPage((prev) => (prev + 1) % totalPages);
  }, [totalPages]);

  const prevPage = useCallback(() => {
    if (totalPages === 0) return;
    setCurrentPage((prev) => (prev - 1 + totalPages) % totalPages);
  }, [totalPages]);

  // Auto-play carousel - 3 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      nextPage();
    }, 3000);
    return () => clearInterval(timer);
  }, [nextPage]);

  if (testimonials.length === 0) return null;

  // Calculate visible items for current page
  const visibleItems = [];
  const startIndex = currentPage * itemsPerPage;
  for (let i = 0; i < itemsPerPage; i++) {
    // Handle case where last page isn't full (though with 9 items / 3 per page it fits perfectly)
    if (startIndex + i < testimonials.length) {
      visibleItems.push(testimonials[startIndex + i]);
    }
  }

  return (
    <section id='testimonials' className="py-24 relative overflow-hidden bg-background">
      {/* Ambient Background */}
      <div className="absolute top-1/2 left-0 -translate-y-1/2 w-125 h-125 bg-primary/5 rounded-full blur-[100px] -z-10" />

      <div className="container mx-auto px-4 mb-4">
        <div className="text-center relative z-10 mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/5 text-primary text-sm font-bold uppercase tracking-widest mb-6 border border-primary/10 hover:bg-primary/10 transition-colors cursor-default"
          >
            <MessageSquare className="w-4 h-4" />
            Community Feedback
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-tight"
          >
            Join <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">thousands</span> of <br className="hidden md:block" />
            satisfied users
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-lg text-muted-foreground/80 max-w-2xl mx-auto mb-10 font-light"
          >
            Don&apos;t just take our word for it. Read what others have to say about their experience.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-8"
          >
            <Button
              onClick={() => setIsModalOpen(true)}
              size="lg"
              className="rounded-full px-8 py-6 text-lg shadow-2xl shadow-primary/30 bg-linear-to-r from-primary to-emerald-600 hover:scale-105 hover:shadow-primary/50 transition-all duration-300"
            >
              <Plus className="mr-2 w-5 h-5" />
              Your Feedback
            </Button>
          </motion.div>
        </div>

        {/* Carousel */}
        <div className="relative mx-auto px-4 md:px-12">
          {/* Nav Buttons - visible on hover or always on desktop */}
          <button
            onClick={prevPage}
            className="absolute left-0 top-1/2 -translate-y-1/2 p-2 rounded-full bg-background/80 backdrop-blur-sm border shadow-sm hover:bg-muted transition-colors z-20 hidden md:flex"
            aria-label="Previous"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          <button
            onClick={nextPage}
            className="absolute right-0 top-1/2 -translate-y-1/2 p-2 rounded-full bg-background/80 backdrop-blur-sm border shadow-sm hover:bg-muted transition-colors z-20 hidden md:flex"
            aria-label="Next"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          <div className="overflow-hidden py-4 min-h-50">
            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={currentPage}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{
                  duration: 0.5,
                  ease: "easeInOut"
                }}
                className="flex gap-6 justify-center"
              >
                {visibleItems.map((item) => (
                  <div
                    key={item.id}
                    className="w-full md:w-[calc(50%-12px)] lg:w-[calc(33.333%-16px)] shrink-0"
                  >
                    <TestimonialCard {...item} />
                  </div>
                ))}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Dots - Now representing PAGES */}
          <div className="flex justify-center gap-2 mt-8">
            {Array.from({ length: totalPages }).map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentPage(idx)}
                className={`h-2 rounded-full transition-all duration-300 ${idx === currentPage ? 'w-8 bg-primary' : 'w-2 bg-muted-foreground/30'}`}
                aria-label={`Go to page ${idx + 1}`}
              />
            ))}
          </div>
        </div>
      </div>

      <AddTestimonialModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAddTestimonial={handleAddTestimonial}
      />
    </section>
  );
}