export type User = { id: string; email: string; name: string; role: string };
export type BusinessProfile = { id: string; businessName: string; industry: string; description: string };
export type Product = { id: string; name: string; category: string; price: number; promotionPotential: 'HIGH' | 'MEDIUM' | 'LOW'; image: string };
export type FeedbackItem = { id: string; source: 'REVIEW' | 'COMMENT' | 'MESSAGE'; sentiment: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE'; content: string; date: string };
export type PerformanceMetric = { id: string; platform: string; views: number; engagementRate: number; conversionRate: number; date: string };
export type StrategyRecommendation = { id: string; title: string; productTarget: string; actionType: string; priority: 'HIGH' | 'MEDIUM' | 'LOW'; explanationReasoning: string; status: 'PENDING' | 'APPROVED' | 'REJECTED' };
export type HistoryRecord = { id: string; recommendationTitle: string; executedAt: string; outcomeSummary: string };
