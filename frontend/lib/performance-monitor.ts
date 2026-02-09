/**
 * Utility for monitoring animation performance
 */

interface AnimationPerformanceMetrics {
  frameRate: number;
  smoothnessScore: number;
  droppedFrames: number;
}

class PerformanceMonitor {
  private startTime: number = 0;
  private frameCount: number = 0;
  private lastFrameTime: number = 0;
  private droppedFrames: number = 0;
  private animationFrameId: number | null = null;
  private observer: PerformanceObserver | null = null;

  /**
   * Starts performance monitoring
   */
  startMonitoring(): void {
    this.startTime = performance.now();
    this.frameCount = 0;
    this.lastFrameTime = this.startTime;

    this.animationFrameId = requestAnimationFrame(this.monitorFrame.bind(this));

    // Observe long tasks that could affect performance
    if ('PerformanceObserver' in window) {
      this.observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) { // Long task threshold
            this.droppedFrames++;
          }
        }
      });

      this.observer.observe({ entryTypes: ['longtask'] });
    }
  }

  /**
   * Stops performance monitoring
   */
  stopMonitoring(): void {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }

  /**
   * Gets current performance metrics
   */
  getMetrics(): AnimationPerformanceMetrics {
    const currentTime = performance.now();
    const elapsed = currentTime - this.startTime;
    const fps = elapsed > 0 ? (this.frameCount / (elapsed / 1000)) : 0;

    // Calculate smoothness score (0-100)
    const smoothnessScore = Math.min(100, Math.max(0, (fps / 60) * 100));

    return {
      frameRate: parseFloat(fps.toFixed(2)),
      smoothnessScore: parseFloat(smoothnessScore.toFixed(2)),
      droppedFrames: this.droppedFrames
    };
  }

  private monitorFrame(timestamp: number): void {
    this.frameCount++;

    // Calculate time between frames
    const delta = timestamp - this.lastFrameTime;

    // If frame took longer than expected (assuming 60fps ~16.67ms per frame)
    if (delta > 30) { // More than twice the ideal frame time
      this.droppedFrames++;
    }

    this.lastFrameTime = timestamp;

    if (this.animationFrameId) {
      this.animationFrameId = requestAnimationFrame(this.monitorFrame.bind(this));
    }
  }

  /**
   * Reports performance to console for debugging
   */
  reportPerformance(): void {
    const metrics = this.getMetrics();
    console.group('Animation Performance Report');
    console.log(`Frame Rate: ${metrics.frameRate} FPS`);
    console.log(`Smoothness Score: ${metrics.smoothnessScore}%`);
    console.log(`Estimated Dropped Frames: ${metrics.droppedFrames}`);

    if (metrics.frameRate < 30) {
      console.warn('⚠️ Low frame rate detected. Consider optimizing animations.');
    } else if (metrics.frameRate < 50) {
      console.info('ℹ️ Frame rate could be improved.');
    } else {
      console.log('✅ Good frame rate performance!');
    }
    console.groupEnd();
  }
}

// Singleton instance
const performanceMonitor = new PerformanceMonitor();

export { performanceMonitor };
export type { AnimationPerformanceMetrics, PerformanceMonitor };