'use client';

import { useEffect, useState } from 'react';

interface CountUpProps {
  end: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
  decimals?: number;
}

export function CountUp({ end, prefix = '', suffix = '', duration = 2, decimals = 0 }: CountUpProps) {
  const [count, setCount] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    if (hasAnimated || end <= 0) return;

    let start: number | null = null;
    const totalDuration = duration * 1000; // Convert to milliseconds

    const animate = (timestamp: number) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / totalDuration, 1);
      const currentCount = Math.floor(progress * end);

      setCount(currentCount);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setCount(end);
        setHasAnimated(true);
      }
    };

    requestAnimationFrame(animate);
  }, [end, duration, hasAnimated]);

  const formatNumber = (num: number): string => {
    return num.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  };

  return <span>{prefix}{formatNumber(count)}{suffix}</span>;
}