import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PropertyAnalysis } from "@/types";

export default function PropertyAnalysisPage() {
  const { propertyId } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<PropertyAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalysis();
  }, [propertyId]);

  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/properties/${propertyId}/analysis/`);
      setAnalysis(response.data);
    } catch (error) {
      console.error("Error fetching analysis:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  if (!analysis)
    return (
      <div className="min-h-screen flex items-center justify-center">
        Property not found
      </div>
    );

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">{analysis.title}</h1>
          <Button variant="outline" onClick={() => navigate("/properties")}>
            ← Back
          </Button>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Overview Card */}
          <Card>
            <CardHeader>
              <CardTitle>Property Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span>Investment Score:</span>
                <Badge className="text-lg">{analysis.grade}</Badge>
              </div>
              <div className="flex justify-between">
                <span>Total Score:</span>
                <span className="font-bold text-xl">
                  {analysis.total_score.toFixed(1)}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Tier:</span>
                <Badge variant="outline">{analysis.investment_tier}</Badge>
              </div>
              <div className="flex justify-between">
                <span>Revenue:</span>
                <span className="font-semibold">
                  ${analysis.revenue?.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span>ADR:</span>
                <span className="font-semibold">
                  ${analysis.adr?.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Occupancy:</span>
                <span className="font-semibold">
                  {((analysis.occupancy || 0) * 100).toFixed(2)}%
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Score Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Score Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(analysis.score_breakdown).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center">
                  <span className="capitalize">{key.replace("_", " ")}:</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500"
                        style={{ width: `${value}%` }}
                      />
                    </div>
                    <span className="font-semibold w-12 text-right">
                      {value.toFixed(1)}
                    </span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Market Comparison */}
        {analysis.market_comparison && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Market Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">vs Market Revenue</p>
                  <p className="text-2xl font-bold">
                    {(
                      analysis.market_comparison.revenue_vs_market * 100
                    ).toFixed(0)}
                    %
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">vs Market ADR</p>
                  <p className="text-2xl font-bold">
                    {(analysis.market_comparison.adr_vs_market * 100).toFixed(
                      0,
                    )}
                    %
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Market Avg Score</p>
                  <p className="text-2xl font-bold">
                    {analysis.market_comparison.market_avg_score.toFixed(1)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Properties in Market</p>
                  <p className="text-2xl font-bold">
                    {analysis.market_comparison.property_count}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Comparable Properties */}
        <Card>
          <CardHeader>
            <CardTitle>Comparable Properties</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analysis.comparable_properties.map((comp) => (
                <div
                  key={comp.property_id}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  onClick={() => navigate(`/analysis/${comp.property_id}`)}
                >
                  <div>
                    <p className="font-semibold">{comp.title}</p>
                    <p className="text-sm text-gray-600">
                      {comp.bedrooms} bed • {comp.market_area}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge>{comp.grade}</Badge>
                    <p className="text-sm font-semibold mt-1">
                      {comp.total_score.toFixed(1)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
