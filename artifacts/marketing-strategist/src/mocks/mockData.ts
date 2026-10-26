import type { BusinessProfile, FeedbackItem, HistoryRecord, PerformanceMetric, Product, StrategyRecommendation, User } from '../types';

// DEV_ONLY: fabricated local-only sample data for the frontend demo.
export const demoUser: User = { id:'user-demo', email:'seller@northline.example', name:'Alex Morgan', role:'Owner' };
export const demoBusiness: BusinessProfile = { id:'biz-01', businessName:'Northline Goods', industry:'Independent footwear', description:'A neighborhood sneaker shop built around considered comfort and everyday movement.' };
export const demoProducts: Product[] = [
  { id:'prod-01', name:'Cloudstep Low', category:'Sneakers', price:118, promotionPotential:'HIGH', image:'CS' },
  { id:'prod-02', name:'Field Runner', category:'Sneakers', price:142, promotionPotential:'MEDIUM', image:'FR' },
  { id:'prod-03', name:'Everyday Canvas', category:'Casual', price:76, promotionPotential:'LOW', image:'EC' },
];
export const demoFeedback: FeedbackItem[] = [
  { id:'fb-01', source:'REVIEW', sentiment:'POSITIVE', content:'The Cloudstep feels broken in from day one. I have been wearing them everywhere.', date:'2025-03-18' },
  { id:'fb-02', source:'COMMENT', sentiment:'NEUTRAL', content:'Do these run true to size? I am between an 8 and an 8.5.', date:'2025-03-17' },
  { id:'fb-03', source:'MESSAGE', sentiment:'NEGATIVE', content:'My size was out of stock again when I came back to order.', date:'2025-03-16' },
  { id:'fb-04', source:'COMMENT', sentiment:'POSITIVE', content:'Love the close-up sole detail in the last reel. More of that please.', date:'2025-03-15' },
  { id:'fb-05', source:'REVIEW', sentiment:'NEUTRAL', content:'Would be great to see a side-by-side fit comparison.', date:'2025-03-13' },
];
export const demoPerformance: PerformanceMetric[] = [
  { id:'pm-01', platform:'Instagram', views:8420, engagementRate:6.8, conversionRate:2.4, date:'Mar 18' },
  { id:'pm-02', platform:'TikTok', views:12650, engagementRate:8.3, conversionRate:1.9, date:'Mar 17' },
  { id:'pm-03', platform:'Email', views:2180, engagementRate:4.6, conversionRate:3.7, date:'Mar 16' },
  { id:'pm-04', platform:'Instagram', views:6740, engagementRate:5.9, conversionRate:2.1, date:'Mar 14' },
];
export const demoRecommendations: StrategyRecommendation[] = [
  { id:'rec-01', title:'Create a size-focused reel for a sneaker with high attention and repeated size questions.', productTarget:'Cloudstep Low', actionType:'Short-form video', priority:'HIGH', explanationReasoning:'The Cloudstep is drawing the most attention across recent content. Customers have asked about sizing repeatedly, so a clear fit demonstration could answer a real buying question.', status:'PENDING' },
  { id:'rec-02', title:'Show the Field Runner in a day-to-evening styling carousel.', productTarget:'Field Runner', actionType:'Social carousel', priority:'MEDIUM', explanationReasoning:'Engagement is steady, while comments ask how to style the shoe beyond the gym. A practical outfit sequence gives shoppers context.', status:'PENDING' },
  { id:'rec-03', title:'Send a restock note to shoppers following Everyday Canvas.', productTarget:'Everyday Canvas', actionType:'Email update', priority:'LOW', explanationReasoning:'A few customers have mentioned availability. Verify inventory before deciding whether a restock message makes sense.', status:'PENDING' },
];
export const demoHistory: HistoryRecord[] = [
  { id:'history-01', recommendationTitle:'Share a close-up of the Cloudstep sole and materials.', executedAt:'2025-03-10T16:30:00.000Z', outcomeSummary:'Approved as a seller decision. The demo record tracks intent only; no content was published.' },
];
