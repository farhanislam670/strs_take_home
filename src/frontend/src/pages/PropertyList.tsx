import { useState, useEffect } from "react";
import api from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PropertyWithScore } from "@/types";
import { useNavigate } from "react-router-dom";

export default function PropertyList() {
  const navigate = useNavigate();
  const [properties, setProperties] = useState<PropertyWithScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [market, setMarket] = useState("");
  const [bedrooms, setBedrooms] = useState("");
  const [sortBy, setSortBy] = useState("total_score");

  useEffect(() => {
    fetchProperties();
  }, [market, bedrooms, sortBy]);

  const fetchProperties = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (market && market !== "all") params.append("market", market);
      if (bedrooms && bedrooms !== "all") params.append("bedrooms", bedrooms);
      params.append("sort_by", sortBy);
      params.append("order", "desc");

      const response = await api.get(`/properties/?${params}`);
      setProperties(response.data);
    } catch (error) {
      console.error("Error fetching properties:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">Properties</h1>
          <Button variant="outline" onClick={() => navigate("/")}>
            ← Home
          </Button>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <Select value={market} onValueChange={setMarket}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Markets" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Markets</SelectItem>
              <SelectItem value="Indianapolis IN">Indianapolis IN</SelectItem>
              <SelectItem value="Blue Ridge GA">Blue Ridge GA</SelectItem>
              <SelectItem value="Bradenton FL">Bradenton FL</SelectItem>
              {/* Add more markets */}
            </SelectContent>
          </Select>

          <Select value={bedrooms} onValueChange={setBedrooms}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Bedrooms" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Bedrooms</SelectItem>
              <SelectItem value="2">2 Bedrooms</SelectItem>
              <SelectItem value="3">3 Bedrooms</SelectItem>
              <SelectItem value="4">4 Bedrooms</SelectItem>
            </SelectContent>
          </Select>

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Sort By" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="total_score">Investment Score</SelectItem>
              <SelectItem value="revenue">Revenue</SelectItem>
              <SelectItem value="occupancy">Occupancy</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Property Grid */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map((property) => (
              <Card
                key={property.property_id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(`/analysis/${property.property_id}`)}
              >
                <CardHeader>
                  <CardTitle className="text-lg">{property.title}</CardTitle>
                  <div className="flex gap-2 mt-2">
                    <Badge
                      variant={
                        property.grade === "A+" ? "default" : "secondary"
                      }
                    >
                      {property.grade}
                    </Badge>
                    <Badge variant="outline">{property.investment_tier}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Score:</span>
                      <span className="font-semibold">
                        {property.total_score.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Revenue:</span>
                      <span className="font-semibold">
                        ${property.revenue?.toLocaleString() || "N/A"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Occupancy:</span>
                      <span className="font-semibold">
                        {property.occupancy}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Market:</span>
                      <span className="font-semibold">
                        {property.market_area}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Bedrooms:</span>
                      <span className="font-semibold">{property.bedrooms}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
