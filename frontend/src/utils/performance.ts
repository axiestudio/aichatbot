/**
 * Frontend Performance Monitoring Utilities
 * Tracks Core Web Vitals, user interactions, and application performance
 */

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  tags?: Record<string, string>;
}

interface WebVitalsMetric {
  name: 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB';
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  timestamp: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private webVitals: WebVitalsMetric[] = [];
  private observer: PerformanceObserver | null = null;
  private isEnabled: boolean = true;

  constructor() {
    this.initializeWebVitals();
    this.initializePerformanceObserver();
    this.trackNavigationTiming();
  }

  /**
   * Initialize Core Web Vitals tracking
   */
  private initializeWebVitals() {
    if (typeof window === 'undefined') return;

    // Track Largest Contentful Paint (LCP)
    this.observeWebVital('largest-contentful-paint', (entry: any) => {
      this.recordWebVital('LCP', entry.startTime);
    });

    // Track First Input Delay (FID)
    this.observeWebVital('first-input', (entry: any) => {
      this.recordWebVital('FID', entry.processingStart - entry.startTime);
    });

    // Track Cumulative Layout Shift (CLS)
    this.observeWebVital('layout-shift', (entry: any) => {
      if (!entry.hadRecentInput) {
        this.recordWebVital('CLS', entry.value);
      }
    });

    // Track First Contentful Paint (FCP)
    this.observeWebVital('paint', (entry: any) => {
      if (entry.name === 'first-contentful-paint') {
        this.recordWebVital('FCP', entry.startTime);
      }
    });

    // Track Time to First Byte (TTFB)
    if (performance.timing) {
      const ttfb = performance.timing.responseStart - performance.timing.navigationStart;
      this.recordWebVital('TTFB', ttfb);
    }
  }

  /**
   * Initialize Performance Observer for resource timing
   */
  private initializePerformanceObserver() {
    if (typeof window === 'undefined' || !window.PerformanceObserver) return;

    this.observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'navigation') {
          this.trackNavigationMetrics(entry as PerformanceNavigationTiming);
        } else if (entry.entryType === 'resource') {
          this.trackResourceMetrics(entry as PerformanceResourceTiming);
        }
      });
    });

    try {
      this.observer.observe({ entryTypes: ['navigation', 'resource'] });
    } catch (error) {
      console.warn('Performance Observer not supported:', error);
    }
  }

  /**
   * Track navigation timing metrics
   */
  private trackNavigationTiming() {
    if (typeof window === 'undefined' || !performance.timing) return;

    const timing = performance.timing;
    const navigationStart = timing.navigationStart;

    // Calculate key timing metrics
    const metrics = {
      'dns-lookup': timing.domainLookupEnd - timing.domainLookupStart,
      'tcp-connection': timing.connectEnd - timing.connectStart,
      'server-response': timing.responseEnd - timing.requestStart,
      'dom-processing': timing.domComplete - timing.domLoading,
      'page-load': timing.loadEventEnd - navigationStart,
      'dom-ready': timing.domContentLoadedEventEnd - navigationStart,
    };

    Object.entries(metrics).forEach(([name, value]) => {
      if (value > 0) {
        this.recordMetric(`navigation.${name}`, value, { type: 'timing' });
      }
    });
  }

  /**
   * Track navigation metrics from PerformanceNavigationTiming
   */
  private trackNavigationMetrics(entry: PerformanceNavigationTiming) {
    const metrics = {
      'redirect-time': entry.redirectEnd - entry.redirectStart,
      'dns-time': entry.domainLookupEnd - entry.domainLookupStart,
      'connect-time': entry.connectEnd - entry.connectStart,
      'request-time': entry.responseEnd - entry.requestStart,
      'response-time': entry.responseEnd - entry.responseStart,
      'dom-processing-time': entry.domComplete - entry.domInteractive,
      'load-event-time': entry.loadEventEnd - entry.loadEventStart,
    };

    Object.entries(metrics).forEach(([name, value]) => {
      if (value > 0) {
        this.recordMetric(`navigation.${name}`, value, { 
          type: 'navigation',
          navigationType: entry.type 
        });
      }
    });
  }

  /**
   * Track resource loading metrics
   */
  private trackResourceMetrics(entry: PerformanceResourceTiming) {
    const duration = entry.responseEnd - entry.startTime;
    const resourceType = this.getResourceType(entry.name);

    this.recordMetric('resource.load-time', duration, {
      type: 'resource',
      resourceType,
      url: entry.name,
      size: entry.transferSize?.toString() || '0'
    });

    // Track slow resources
    if (duration > 1000) { // > 1 second
      this.recordMetric('resource.slow-load', duration, {
        type: 'slow-resource',
        resourceType,
        url: entry.name
      });
    }
  }

  /**
   * Observe specific web vital metrics
   */
  private observeWebVital(type: string, callback: (entry: any) => void) {
    if (typeof window === 'undefined' || !window.PerformanceObserver) return;

    try {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach(callback);
      });
      observer.observe({ entryTypes: [type] });
    } catch (error) {
      console.warn(`Cannot observe ${type}:`, error);
    }
  }

  /**
   * Record a web vital metric
   */
  private recordWebVital(name: WebVitalsMetric['name'], value: number) {
    const rating = this.getWebVitalRating(name, value);
    
    this.webVitals.push({
      name,
      value,
      rating,
      timestamp: Date.now()
    });

    // Also record as regular metric
    this.recordMetric(`web-vitals.${name.toLowerCase()}`, value, {
      type: 'web-vital',
      rating
    });
  }

  /**
   * Get web vital rating based on thresholds
   */
  private getWebVitalRating(name: string, value: number): 'good' | 'needs-improvement' | 'poor' {
    const thresholds = {
      LCP: { good: 2500, poor: 4000 },
      FID: { good: 100, poor: 300 },
      CLS: { good: 0.1, poor: 0.25 },
      FCP: { good: 1800, poor: 3000 },
      TTFB: { good: 800, poor: 1800 }
    };

    const threshold = thresholds[name as keyof typeof thresholds];
    if (!threshold) return 'good';

    if (value <= threshold.good) return 'good';
    if (value <= threshold.poor) return 'needs-improvement';
    return 'poor';
  }

  /**
   * Get resource type from URL
   */
  private getResourceType(url: string): string {
    if (url.includes('.js')) return 'script';
    if (url.includes('.css')) return 'stylesheet';
    if (url.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i)) return 'image';
    if (url.match(/\.(woff|woff2|ttf|eot)$/i)) return 'font';
    if (url.includes('/api/')) return 'api';
    return 'other';
  }

  /**
   * Record a custom metric
   */
  recordMetric(name: string, value: number, tags?: Record<string, string>) {
    if (!this.isEnabled) return;

    this.metrics.push({
      name,
      value,
      timestamp: Date.now(),
      tags
    });

    // Keep only last 1000 metrics to prevent memory leaks
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
  }

  /**
   * Track user interaction timing
   */
  trackInteraction(action: string, startTime: number, endTime?: number) {
    const duration = (endTime || Date.now()) - startTime;
    this.recordMetric('user.interaction', duration, {
      type: 'interaction',
      action
    });
  }

  /**
   * Track API call performance
   */
  trackApiCall(endpoint: string, method: string, duration: number, status: number) {
    this.recordMetric('api.request', duration, {
      type: 'api',
      endpoint,
      method,
      status: status.toString()
    });

    // Track slow API calls
    if (duration > 2000) { // > 2 seconds
      this.recordMetric('api.slow-request', duration, {
        type: 'slow-api',
        endpoint,
        method
      });
    }
  }

  /**
   * Get performance summary
   */
  getPerformanceSummary(timeRange: number = 300000): any { // 5 minutes default
    const cutoff = Date.now() - timeRange;
    const recentMetrics = this.metrics.filter(m => m.timestamp > cutoff);
    const recentWebVitals = this.webVitals.filter(w => w.timestamp > cutoff);

    return {
      timeRange,
      totalMetrics: recentMetrics.length,
      webVitals: recentWebVitals,
      metricsSummary: this.summarizeMetrics(recentMetrics),
      performanceScore: this.calculatePerformanceScore(recentWebVitals)
    };
  }

  /**
   * Summarize metrics by type
   */
  private summarizeMetrics(metrics: PerformanceMetric[]) {
    const summary: Record<string, any> = {};

    metrics.forEach(metric => {
      const category = metric.name.split('.')[0];
      if (!summary[category]) {
        summary[category] = {
          count: 0,
          totalValue: 0,
          avgValue: 0,
          maxValue: 0,
          minValue: Infinity
        };
      }

      summary[category].count++;
      summary[category].totalValue += metric.value;
      summary[category].maxValue = Math.max(summary[category].maxValue, metric.value);
      summary[category].minValue = Math.min(summary[category].minValue, metric.value);
      summary[category].avgValue = summary[category].totalValue / summary[category].count;
    });

    return summary;
  }

  /**
   * Calculate overall performance score
   */
  private calculatePerformanceScore(webVitals: WebVitalsMetric[]): number {
    if (webVitals.length === 0) return 100;

    const scores = webVitals.map(vital => {
      switch (vital.rating) {
        case 'good': return 100;
        case 'needs-improvement': return 75;
        case 'poor': return 50;
        default: return 100;
      }
    });

    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  }

  /**
   * Send metrics to backend
   */
  async sendMetrics() {
    if (this.metrics.length === 0) return;

    try {
      const payload = {
        metrics: this.metrics.splice(0, 100), // Send batch of 100
        webVitals: this.webVitals.splice(0, 50), // Send batch of 50
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href
      };

      await fetch('/api/v1/metrics/frontend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (error) {
      console.warn('Failed to send performance metrics:', error);
    }
  }

  /**
   * Enable/disable monitoring
   */
  setEnabled(enabled: boolean) {
    this.isEnabled = enabled;
  }

  /**
   * Clean up observers
   */
  destroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

// Create global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();

// Auto-send metrics every 30 seconds
if (typeof window !== 'undefined') {
  setInterval(() => {
    performanceMonitor.sendMetrics();
  }, 30000);
}

// Send metrics before page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    performanceMonitor.sendMetrics();
  });
}

export default performanceMonitor;
