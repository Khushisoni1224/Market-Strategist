import { demoFeedback, demoHistory, demoPerformance, demoProducts, demoRecommendations } from '../mocks/mockData';
import type { FeedbackItem, HistoryRecord, PerformanceMetric, Product, StrategyRecommendation, User } from '../types';

type ErrorOption = boolean;
let products=[...demoProducts];
const feedback=[...demoFeedback];
let recommendations=[...demoRecommendations];
let history=[...demoHistory];
let failNextRequest=false;
const wait=async<T,>(value:T,errorState:ErrorOption=false):Promise<T>=>{
  await new Promise((resolve)=>setTimeout(resolve,400));
  if(errorState||failNextRequest){failNextRequest=false;throw new Error('Demo service is temporarily unavailable. Please try again.');}
  return structuredClone(value);
};
export const setDemoErrorOnce=()=>{failNextRequest=true;};
export const api={
  login:async(email:string,_password:string,errorState:ErrorOption=false):Promise<User>=>wait({id:'demo-user',email,name:email.split('@')[0]?.replace(/[._-]/g,' ').replace(/\b\w/g,(c)=>c.toUpperCase())||'Demo seller',role:'Owner'},errorState),
  register:async(name:string,email:string,_password:string,errorState:ErrorOption=false):Promise<User>=>wait({id:'demo-user',email,name,role:'Owner'},errorState),
  getProducts:(errorState:ErrorOption=false):Promise<Product[]>=>wait(products,errorState),
  addProduct:async(input:Omit<Product,'id'|'image'>,errorState:ErrorOption=false):Promise<Product>=>{
    const product={...input,id:`prod-${Date.now()}`,image:input.name.split(' ').map((part)=>part[0]).join('').slice(0,2).toUpperCase()};
    await wait(product,errorState);products=[product,...products];return product;
  },
  getFeedback:(errorState:ErrorOption=false):Promise<FeedbackItem[]>=>wait(feedback,errorState),
  getFeedbackStats:async(errorState:ErrorOption=false)=>wait({total:feedback.length,positive:feedback.filter((item)=>item.sentiment==='POSITIVE').length,neutral:feedback.filter((item)=>item.sentiment==='NEUTRAL').length,negative:feedback.filter((item)=>item.sentiment==='NEGATIVE').length},errorState),
  getPerformanceMetrics:(errorState:ErrorOption=false):Promise<PerformanceMetric[]>=>wait(demoPerformance,errorState),
  getRecommendations:(errorState:ErrorOption=false):Promise<StrategyRecommendation[]>=>wait(recommendations,errorState),
  updateRecommendationStatus:async(id:string,status:'APPROVED'|'REJECTED',errorState:ErrorOption=false):Promise<StrategyRecommendation>=>{
    const updatedBase=recommendations.find((item)=>item.id===id);
    if(!updatedBase)throw new Error('Recommendation not found in demo data.');
    const updated={...updatedBase,status};
    await wait(updated,errorState);
    recommendations=recommendations.map((item)=>item.id===id?updated:item);
    if(status==='APPROVED'&&!history.some((record)=>record.id===id))history=[{id,recommendationTitle:updated.title,executedAt:new Date().toISOString(),outcomeSummary:'Approved by seller. The action is ready for the seller to plan and execute.'},...history];
    return updated;
  },
  getHistory:(errorState:ErrorOption=false):Promise<HistoryRecord[]>=>wait(history,errorState),
};
