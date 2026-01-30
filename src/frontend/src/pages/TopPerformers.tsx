import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TopPerformersResponse } from "@/types";
import { sanitizeTitle } from "@/utils/formatters";

export default function TopPerformers() {
  const navigate = useNavigate();
  const [data, setData] = useState<TopPerformersResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTopPerformers();
  }, []);

  const fetchTopPerformers = async () => {
    setLoading(true);
    try {
      const response = await api.get("/insights/top-performers/?limit=20");
      setData(response.data);
    } catch (error) {
      console.error("Error fetching top performers:", error);
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
  if (!data)
    return (
      <div className="min-h-screen flex items-center justify-center">
        No data available
      </div>
    );

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold">Top Performers</h1>
            <p className="text-gray-600 mt-2">
              Top {data.total_count} investment opportunities
            </p>
          </div>
          <Button variant="outline" onClick={() => navigate("/")}>
            ← Home
          </Button>
        </div>

        {/* Top Properties List */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Highest Rated Properties</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.top_properties.slice(0, 10).map((property, index) => (
                <div
                  key={property.property_id}
                  className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  onClick={() => navigate(`/analysis/${property.property_id}`)}
                >
                  <div className="text-2xl font-bold text-gray-400 w-8">
                    #{index + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">
                      {sanitizeTitle(property.title)}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {property.bedrooms} bed • {property.market_area}
                    </p>
                    <div className="flex gap-2 mt-2 flex-wrap">
                      {property.key_strengths.slice(0, 3).map((strength) => (
                        <Badge
                          key={strength}
                          variant="secondary"
                          className="text-xs"
                        >
                          {strength}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge className="mb-2">{property.grade}</Badge>
                    <p className="text-sm font-semibold">
                      {property.total_score.toFixed(1)}
                    </p>
                    <p className="text-xs text-gray-600">
                      ${property.revenue?.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* By Market */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Top Markets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.by_market.slice(0, 5).map((market) => (
                  <div
                    key={market.market_area}
                    className="flex justify-between items-center p-3 bg-gray-50 rounded"
                  >
                    <div>
                      <p className="font-semibold">{market.market_area}</p>
                      <p className="text-sm text-gray-600">
                        {market.property_count} properties
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">
                        {market.avg_score.toFixed(1)}
                      </p>
                      <p className="text-xs text-gray-600">Avg Score</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* By Bedroom */}
          <Card>
            <CardHeader>
              <CardTitle>By Bedroom Count</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.by_bedroom.map((bedroom) => (
                  <div
                    key={bedroom.bedroom_count}
                    className="flex justify-between items-center p-3 bg-gray-50 rounded"
                  >
                    <div>
                      <p className="font-semibold">
                        {bedroom.bedroom_count} Bedrooms
                      </p>
                      <p className="text-sm text-gray-600">
                        {bedroom.property_count} properties
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">
                        {bedroom.avg_score.toFixed(1)}
                      </p>
                      <p className="text-xs text-gray-600">Avg Score</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
