// Property List Types
export interface PropertyWithScore {
  property_id: string;
  title: string;
  market_area: string;
  bedrooms: number;
  property_type: string;
  revenue: number | null;
  adr: number | null;
  occupancy: number | null;
  total_score: number;
  grade: string;
  investment_tier: string;
  is_top_opportunity: boolean;
}

// Analysis Types
export interface ScoreBreakdown {
  revenue: number;
  occupancy: number;
  positioning: number;
  reviews: number;
  amenities: number;
  host_status: number;
  seasonal: number;
}

export interface MarketComparison {
  market_area: string;
  bedroom_count: number;
  market_avg_revenue: number;
  market_avg_adr: number;
  market_avg_occupancy: number;
  market_avg_score: number;
  property_count: number;
  revenue_vs_market: number;
  adr_vs_market: number;
  score_vs_market: number;
}

export interface PropertyAnalysis {
  property_id: string;
  title: string;
  market_area: string;
  bedrooms: number;
  bathrooms: number;
  property_type: string;
  revenue: number | null;
  adr: number | null;
  occupancy: number | null;
  total_score: number;
  grade: string;
  investment_tier: string;
  score_breakdown: ScoreBreakdown;
  market_comparison: MarketComparison | null;
  comparable_properties: PropertyWithScore[];
}

// Insights Types
export interface TopPerformer {
  property_id: string;
  title: string;
  market_area: string;
  bedrooms: number;
  total_score: number;
  grade: string;
  investment_tier: string;
  revenue: number | null;
  revenue_vs_market: number | null;
  occupancy: number | null;
  adr: number | null;
  key_strengths: string[];
}

export interface MarketGroup {
  market_area: string;
  property_count: number;
  avg_score: number;
  top_properties: TopPerformer[];
}

export interface BedroomGroup {
  bedroom_count: number;
  property_count: number;
  avg_score: number;
  top_properties: TopPerformer[];
}

export interface TopPerformersResponse {
  total_count: number;
  top_properties: TopPerformer[];
  by_market: MarketGroup[];
  by_bedroom: BedroomGroup[];
}
